"""MQTT client for receiving and processing TimeData messages using paho-mqtt."""

import asyncio
import json
import logging
import threading
from queue import Empty, Queue

import paho.mqtt.client as mqtt
from pydantic import ValidationError

from app.core.config import settings
from app.db.base import SessionLocal
from app.iot_data.time_data_service import store_time_data
from app.mqtt.schemas import TimeDataMQTTMessage

logger = logging.getLogger(__name__)


class MQTTClient:
    """MQTT client for receiving TimeData using paho-mqtt."""

    def __init__(self):
        """Initialize the MQTT client."""
        self.client: mqtt.Client | None = None
        self._running = False
        self._thread: threading.Thread | None = None
        self._message_queue: Queue = Queue()

    def _on_connect(self, client: mqtt.Client, userdata: dict, flags: dict, rc: int) -> None:
        """Callback when the client connects to the broker.

        Args:
            client: MQTT client
            userdata: User data passed to the client
            flags: Response flags from the broker
            rc: Connection result code
        """
        if rc == 0:
            logger.info(
                f"Connected to MQTT broker at {settings.mqtt_broker_host}:{settings.mqtt_broker_port}"
            )
            # Subscribe to topic
            client.subscribe(settings.mqtt_topic)
            logger.info(f"Subscribed to topic: {settings.mqtt_topic}")
        else:
            logger.error(f"Error connecting to MQTT broker. Code: {rc}")

    def _on_message(self, client: mqtt.Client, userdata: dict, msg: mqtt.MQTTMessage) -> None:
        """Callback when a message is received.

        Args:
            client: MQTT client
            userdata: User data passed to the client
            msg: Received message
        """
        try:
            payload = msg.payload.decode("utf-8")
            topic = msg.topic
            logger.debug(f"Message received on {topic}: {payload}")
            # Add message to queue for processing
            self._message_queue.put(payload)
        except Exception as e:
            logger.error(f"Error processing MQTT message: {e}")

    def _on_disconnect(self, client: mqtt.Client, userdata: dict, rc: int) -> None:
        """Callback when the client disconnects from the broker.

        Args:
            client: MQTT client
            userdata: User data passed to the client
            rc: Disconnection result code
        """
        if rc != 0:
            logger.warning(f"Unexpected disconnection from MQTT broker. Code: {rc}")
        else:
            logger.info("Disconnected from MQTT broker")

    async def _process_message(self, message: str) -> None:
        """Process an MQTT message and store it in the database.

        Args:
            message: JSON message received from MQTT broker
        """
        try:
            # Parse JSON
            data = json.loads(message)

            # Validate with Pydantic
            mqtt_message = TimeDataMQTTMessage(**data)

            # Store in database (execute in thread pool to avoid blocking)
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, self._store_in_db, mqtt_message)

        except json.JSONDecodeError as e:
            logger.error(f"Error parsing JSON from MQTT message: {e}")
        except ValidationError as e:
            logger.error(f"MQTT message validation error: {e}")
        except Exception as e:
            logger.error(f"Error processing MQTT message: {e}")

    def _store_in_db(self, mqtt_message: TimeDataMQTTMessage) -> None:
        """Store the message in the database (executed in thread pool).

        Args:
            mqtt_message: Validated TimeData message
        """
        db = SessionLocal()
        try:
            store_time_data(db, mqtt_message)
        except Exception as e:
            logger.error(
                f"Error storing MQTT message in database: sensor_id={mqtt_message.sensor_id}, "
                f"device_id={mqtt_message.device_id}, error={str(e)}"
            )
            logger.exception("Full traceback for MQTT database storage error")
            raise
        finally:
            db.close()

    async def _message_processor(self) -> None:
        """Process messages from the queue asynchronously."""
        while self._running:
            try:
                # Try to get message from queue (non-blocking)
                try:
                    message = self._message_queue.get_nowait()
                    await self._process_message(message)
                except Empty:
                    # If no messages, wait a bit before trying again
                    await asyncio.sleep(0.1)
            except Exception as e:
                logger.error(f"Error in message processor: {e}")
                await asyncio.sleep(0.1)

    def _run_mqtt_client(self) -> None:
        """Run the MQTT client loop in a separate thread."""
        try:
            self.client.loop_forever()
        except Exception as e:
            logger.error(f"Error in MQTT client loop: {e}")
            self._running = False

    async def connect(self) -> None:
        """Connect to the MQTT broker."""
        if not settings.mqtt_enabled:
            logger.info("MQTT is disabled in configuration")
            return

        try:
            # Create MQTT client
            self.client = mqtt.Client(
                client_id=settings.mqtt_client_id,
                callback_api_version=mqtt.CallbackAPIVersion.VERSION1,
            )

            # Configure callbacks
            self.client.on_connect = self._on_connect
            self.client.on_message = self._on_message
            self.client.on_disconnect = self._on_disconnect

            # Configure authentication if available
            if settings.mqtt_username and settings.mqtt_password:
                self.client.username_pw_set(
                    settings.mqtt_username, settings.mqtt_password
                )

            # Connect to broker (execute in thread pool)
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                None,
                self.client.connect,
                settings.mqtt_broker_host,
                settings.mqtt_broker_port,
                60,  # keepalive
            )

        except Exception as e:
            logger.error(f"Error connecting to MQTT broker: {e}")
            raise

    async def disconnect(self) -> None:
        """Disconnect from the MQTT broker."""
        if self.client:
            try:
                self.client.loop_stop()
                self.client.disconnect()
                logger.info("Disconnected from MQTT broker")
            except Exception as e:
                logger.error(f"Error disconnecting from MQTT broker: {e}")

    async def start(self) -> None:
        """Start the MQTT client and begin listening for messages."""
        if not settings.mqtt_enabled:
            logger.info("MQTT is disabled, client will not start")
            return

        if self._running:
            logger.warning("MQTT client is already running")
            return

        try:
            await self.connect()
            self._running = True

            # Start thread for MQTT loop
            self._thread = threading.Thread(
                target=self._run_mqtt_client, daemon=True
            )
            self._thread.start()

            # Start asynchronous message processor
            asyncio.create_task(self._message_processor())

            logger.info("MQTT client started successfully")
        except Exception as e:
            logger.error(f"Error starting MQTT client: {e}")
            self._running = False
            raise

    async def stop(self) -> None:
        """Stop the MQTT client."""
        if not self._running:
            return

        self._running = False

        # Stop the MQTT client
        await self.disconnect()

        # Wait for thread to finish
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=5.0)

        logger.info("MQTT client stopped")


# Singleton instance of the MQTT client
_mqtt_client: MQTTClient | None = None


def get_mqtt_client() -> MQTTClient:
    """Get the singleton instance of the MQTT client.

    Returns:
        MQTT client instance
    """
    global _mqtt_client
    if _mqtt_client is None:
        _mqtt_client = MQTTClient()
    return _mqtt_client
