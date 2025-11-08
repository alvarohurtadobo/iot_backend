"""Configuración central de la aplicación iotMonitor."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Valores configurables de la API."""

    project_name: str = "iotMonitor"
    version: str = "0.1.0"
    database_url: str = (
        "postgresql+psycopg2://postgres:postgres@localhost:5432/iot_monitor"
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix="IOT_MONITOR_",
    )


settings = Settings()
