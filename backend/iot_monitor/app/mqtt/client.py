"""Cliente MQTT para recibir y procesar mensajes de TimeData usando paho-mqtt."""

import asyncio
import json
import logging
import threading
from queue import Queue
from typing import Callable

import paho.mqtt.client as mqtt
from pydantic import ValidationError

from app.core.config import settings
from app.db.base import SessionLocal
from app.iot_data.time_data_service import store_time_data
from app.mqtt.schemas import TimeDataMQTTMessage

logger = logging.getLogger(__name__)


class MQTTClient:
    """Cliente MQTT para recibir datos de TimeData usando paho-mqtt."""

    def __init__(self):
        """Inicializa el cliente MQTT."""
        self.client: mqtt.Client | None = None
        self._running = False
        self._thread: threading.Thread | None = None
        self._message_queue: Queue = Queue()

    def _on_connect(self, client: mqtt.Client, userdata: dict, flags: dict, rc: int) -> None:
        """Callback cuando el cliente se conecta al broker.

        Args:
            client: Cliente MQTT
            userdata: Datos de usuario pasados al cliente
            flags: Flags de respuesta del broker
            rc: Código de resultado de la conexión
        """
        if rc == 0:
            logger.info(
                f"Conectado al broker MQTT en {settings.mqtt_broker_host}:{settings.mqtt_broker_port}"
            )
            # Suscribirse al tópico
            client.subscribe(settings.mqtt_topic)
            logger.info(f"Suscrito al tópico: {settings.mqtt_topic}")
        else:
            logger.error(f"Error al conectar al broker MQTT. Código: {rc}")

    def _on_message(self, client: mqtt.Client, userdata: dict, msg: mqtt.MQTTMessage) -> None:
        """Callback cuando se recibe un mensaje.

        Args:
            client: Cliente MQTT
            userdata: Datos de usuario pasados al cliente
            msg: Mensaje recibido
        """
        try:
            payload = msg.payload.decode("utf-8")
            topic = msg.topic
            logger.debug(f"Mensaje recibido en {topic}: {payload}")
            # Agregar mensaje a la cola para procesamiento
            self._message_queue.put(payload)
        except Exception as e:
            logger.error(f"Error al procesar mensaje MQTT: {e}")

    def _on_disconnect(self, client: mqtt.Client, userdata: dict, rc: int) -> None:
        """Callback cuando el cliente se desconecta del broker.

        Args:
            client: Cliente MQTT
            userdata: Datos de usuario pasados al cliente
            rc: Código de resultado de la desconexión
        """
        if rc != 0:
            logger.warning(f"Desconexión inesperada del broker MQTT. Código: {rc}")
        else:
            logger.info("Desconectado del broker MQTT")

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

            # Almacenar en base de datos (ejecutar en thread pool para no bloquear)
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, self._store_in_db, mqtt_message)

        except json.JSONDecodeError as e:
            logger.error(f"Error al parsear JSON del mensaje MQTT: {e}")
        except ValidationError as e:
            logger.error(f"Error de validación del mensaje MQTT: {e}")
        except Exception as e:
            logger.error(f"Error al procesar mensaje MQTT: {e}")

    def _store_in_db(self, mqtt_message: TimeDataMQTTMessage) -> None:
        """Almacena el mensaje en la base de datos (ejecutado en thread pool).

        Args:
            mqtt_message: Mensaje validado de TimeData
        """
        db = SessionLocal()
        try:
            store_time_data(db, mqtt_message)
        finally:
            db.close()

    async def _message_processor(self) -> None:
        """Procesa mensajes de la cola de forma asíncrona."""
        while self._running:
            try:
                # Intentar obtener mensaje de la cola (no bloqueante)
                try:
                    message = self._message_queue.get_nowait()
                    await self._process_message(message)
                except Exception:
                    # Si no hay mensajes, esperar un poco antes de intentar de nuevo
                    await asyncio.sleep(0.1)
            except Exception as e:
                logger.error(f"Error en el procesador de mensajes: {e}")
                await asyncio.sleep(0.1)

    def _run_mqtt_client(self) -> None:
        """Ejecuta el loop del cliente MQTT en un hilo separado."""
        try:
            self.client.loop_forever()
        except Exception as e:
            logger.error(f"Error en el loop del cliente MQTT: {e}")
            self._running = False

    async def connect(self) -> None:
        """Conecta al broker MQTT."""
        if not settings.mqtt_enabled:
            logger.info("MQTT está deshabilitado en la configuración")
            return

        try:
            # Crear cliente MQTT
            self.client = mqtt.Client(
                client_id=settings.mqtt_client_id,
                callback_api_version=mqtt.CallbackAPIVersion.VERSION1,
            )

            # Configurar callbacks
            self.client.on_connect = self._on_connect
            self.client.on_message = self._on_message
            self.client.on_disconnect = self._on_disconnect

            # Configurar autenticación si está disponible
            if settings.mqtt_username and settings.mqtt_password:
                self.client.username_pw_set(
                    settings.mqtt_username, settings.mqtt_password
                )

            # Conectar al broker (ejecutar en thread pool)
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                None,
                self.client.connect,
                settings.mqtt_broker_host,
                settings.mqtt_broker_port,
                60,  # keepalive
            )

        except Exception as e:
            logger.error(f"Error al conectar al broker MQTT: {e}")
            raise

    async def disconnect(self) -> None:
        """Desconecta del broker MQTT."""
        if self.client:
            try:
                self.client.loop_stop()
                self.client.disconnect()
                logger.info("Desconectado del broker MQTT")
            except Exception as e:
                logger.error(f"Error al desconectar del broker MQTT: {e}")

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

            # Iniciar thread para el loop de MQTT
            self._thread = threading.Thread(
                target=self._run_mqtt_client, daemon=True
            )
            self._thread.start()

            # Iniciar procesador de mensajes asíncrono
            asyncio.create_task(self._message_processor())

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

        # Detener el cliente MQTT
        await self.disconnect()

        # Esperar a que termine el thread
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=5.0)

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
