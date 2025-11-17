"""Cliente MQTT para recibir y procesar mensajes de TimeData."""

import asyncio
import json
import logging

from aiomqtt import Client, MqttError
from pydantic import ValidationError

from app.core.config import settings
from app.db.base import SessionLocal
from app.iot_data.time_data_service import store_time_data
from app.mqtt.schemas import TimeDataMQTTMessage

logger = logging.getLogger(__name__)


class MQTTClient:
    """Cliente MQTT para recibir datos de TimeData."""

    def __init__(self):
        """Inicializa el cliente MQTT."""
        self.client: Client | None = None
        self._running = False
        self._task: asyncio.Task | None = None

    async def connect(self) -> None:
        """Conecta al broker MQTT."""
        if not settings.mqtt_enabled:
            logger.info("MQTT está deshabilitado en la configuración")
            return

        try:
            self.client = Client(
                hostname=settings.mqtt_broker_host,
                port=settings.mqtt_broker_port,
                username=settings.mqtt_username,
                password=settings.mqtt_password,
                client_id=settings.mqtt_client_id,
            )
            await self.client.connect()
            logger.info(
                f"Conectado al broker MQTT en {settings.mqtt_broker_host}:{settings.mqtt_broker_port}"
            )
        except MqttError as e:
            logger.error(f"Error al conectar al broker MQTT: {e}")
            raise

    async def disconnect(self) -> None:
        """Desconecta del broker MQTT."""
        if self.client:
            try:
                await self.client.disconnect()
                logger.info("Desconectado del broker MQTT")
            except Exception as e:
                logger.error(f"Error al desconectar del broker MQTT: {e}")

    async def _process_message(self, message: str) -> None:
        """Procesa un mensaje MQTT y lo almacena en la base de datos.

        Args:
            message: Mensaje JSON recibido del broker MQTT
        """
        try:
            # Parsear JSON
            data = json.loads(message)

            # Validar con Pydantic
            mqtt_message = TimeDataMQTTMessage(**data)

            # Almacenar en base de datos
            db = SessionLocal()
            try:
                store_time_data(db, mqtt_message)
            finally:
                db.close()

        except json.JSONDecodeError as e:
            logger.error(f"Error al parsear JSON del mensaje MQTT: {e}")
        except ValidationError as e:
            logger.error(f"Error de validación del mensaje MQTT: {e}")
        except Exception as e:
            logger.error(f"Error al procesar mensaje MQTT: {e}")

    async def _message_handler(self) -> None:
        """Maneja los mensajes recibidos del broker MQTT."""
        if not self.client:
            return

        try:
            async with self.client.messages() as messages:
                await self.client.subscribe(settings.mqtt_topic)
                logger.info(f"Suscrito al tópico: {settings.mqtt_topic}")

                async for message in messages:
                    payload = message.payload.decode("utf-8")
                    topic = str(message.topic)
                    logger.debug(f"Mensaje recibido en {topic}: {payload}")
                    await self._process_message(payload)

        except MqttError as e:
            logger.error(f"Error en el handler de mensajes MQTT: {e}")
        except Exception as e:
            logger.error(f"Error inesperado en el handler MQTT: {e}")

    async def start(self) -> None:
        """Inicia el cliente MQTT y comienza a escuchar mensajes."""
        if not settings.mqtt_enabled:
            logger.info("MQTT está deshabilitado, no se iniciará el cliente")
            return

        if self._running:
            logger.warning("El cliente MQTT ya está corriendo")
            return

        try:
            await self.connect()
            self._running = True
            self._task = asyncio.create_task(self._message_handler())
            logger.info("Cliente MQTT iniciado correctamente")
        except Exception as e:
            logger.error(f"Error al iniciar el cliente MQTT: {e}")
            self._running = False
            raise

    async def stop(self) -> None:
        """Detiene el cliente MQTT."""
        if not self._running:
            return

        self._running = False

        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass

        await self.disconnect()
        logger.info("Cliente MQTT detenido")


# Instancia singleton del cliente MQTT
_mqtt_client: MQTTClient | None = None


def get_mqtt_client() -> MQTTClient:
    """Obtiene la instancia singleton del cliente MQTT.

    Returns:
        Instancia del cliente MQTT
    """
    global _mqtt_client
    if _mqtt_client is None:
        _mqtt_client = MQTTClient()
    return _mqtt_client

