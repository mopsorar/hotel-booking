from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

ENV_FILE = Path(__file__).resolve().parents[2] / ".env"


class EnvironmentSettings(BaseSettings):
    django_secret_key: str
    django_debug: bool = False
    django_allowed_hosts: str = "localhost,127.0.0.1"
    django_log_level: str = "INFO"

    db_name: str
    db_user: str
    db_password: str
    db_host: str
    db_port: int

    model_config = SettingsConfigDict(
        env_file=ENV_FILE,
        env_file_encoding="utf-8",
        extra="ignore",
    )


environment = EnvironmentSettings()
