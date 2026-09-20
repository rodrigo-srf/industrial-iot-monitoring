import json
import logging
from threading import Lock

import paho.mqtt.client as mqtt
from pydantic import ValidationError

from app.config import settings
from app.database import SessionLocal
from app.schemas import TelemetryIn
from app.services import save_measurement

logger = logging.getLogger(__name__)


class MQTTCollector:
    def __init__(self) -> None:
        self.connected = False
        self._started = False
        self._lock = Lock()
        self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id="industrial-api")
        self.client.on_connect = self._on_connect
        self.client.on_disconnect = self._on_disconnect
        self.client.on_message = self._on_message

    def _on_connect(self, client, userdata, flags, reason_code, properties) -> None:
        self.connected = reason_code == 0
        if self.connected:
            client.subscribe("factory/machines/+/telemetry", qos=1)
            logger.info("Coletor conectado ao broker MQTT")
        else:
            logger.warning("Falha na conexão MQTT: %s", reason_code)

    def _on_disconnect(self, client, userdata, disconnect_flags, reason_code, properties) -> None:
        self.connected = False

    @staticmethod
    def _on_message(client, userdata, message) -> None:
        try:
            payload = json.loads(message.payload.decode("utf-8"))
            telemetry = TelemetryIn.model_validate(payload)
            with SessionLocal() as db:
                save_measurement(db, telemetry)
        except (json.JSONDecodeError, UnicodeDecodeError, ValidationError) as exc:
            logger.warning("Telemetria MQTT inválida em %s: %s", message.topic, exc)
        except Exception:
            logger.exception("Erro ao processar telemetria MQTT")

    def start(self) -> None:
        if not settings.mqtt_enabled:
            logger.info("MQTT desabilitado")
            return
        with self._lock:
            if self._started:
                return
            self.client.connect_async(settings.mqtt_host, settings.mqtt_port, keepalive=60)
            self.client.loop_start()
            self._started = True

    def stop(self) -> None:
        with self._lock:
            if not self._started:
                return
            self.client.disconnect()
            self.client.loop_stop()
            self._started = False
            self.connected = False


collector = MQTTCollector()
