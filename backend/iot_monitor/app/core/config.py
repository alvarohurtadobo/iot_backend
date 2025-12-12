"""Central configuration for the iotMonitor application."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configurable values for the API."""

    project_name: str = "iotMonitor"
    version: str = "0.1.0"
    database_url: str = (
        "postgresql+psycopg2://postgres:postgres@localhost:5432/iot_monitor"
    )
    
    # MQTT configuration
    mqtt_broker_host: str = "localhost"
    mqtt_broker_port: int = 1883
    mqtt_username: str | None = None
    mqtt_password: str | None = None
    mqtt_topic: str = "iot/data"
    mqtt_client_id: str = "iot_monitor_client"
    mqtt_enabled: bool = True

    # JWT configuration
    secret_key: str = "your-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7
    
    # Security settings
    max_login_attempts: int = 5
    account_lockout_minutes: int = 30
    password_min_length: int = 8
    rate_limit_per_minute: int = 5

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix="IOT_MONITOR_",
    )


settings = Settings()
