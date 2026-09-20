import os


class Settings:
    database_url = os.getenv("DATABASE_URL", "sqlite:///./industrial.db")
    mqtt_host = os.getenv("MQTT_HOST", "localhost")
    mqtt_port = int(os.getenv("MQTT_PORT", "1883"))
    mqtt_enabled = os.getenv("MQTT_ENABLED", "true").lower() == "true"


settings = Settings()
