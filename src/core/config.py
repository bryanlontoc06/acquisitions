import os
from urllib.parse import quote_plus

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

# Determine the path to the .env.local file relative to this config.py file
current_dir = os.path.dirname(os.path.abspath(__file__))
app_env = os.getenv("APP_ENV", "local")
env_filename = f".env.{app_env}"
# Assuming the .env.local file is located in the parent directory of src/core
env_path = os.path.join(current_dir, env_filename)


class Settings(BaseSettings):
    db_user: str
    db_password: str
    db_host: str
    db_name: str
    WEB_CLIENT_ID_KEY: str
    MOBILE_CLIENT_ID_KEY: str
    model_config = SettingsConfigDict(
        env_file=env_path,
        extra="ignore",
        env_file_encoding="utf-8",
    )

    @property
    def DATABASE_URL(self) -> str:
        encoded_password = quote_plus(self.db_password)
        return f"mysql+aiomysql://{self.db_user}:{encoded_password}@{self.db_host}:4000/{self.db_name}"

    # Default values can be overridden by .env file or environment variables
    secret_key: SecretStr
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7


settings = Settings()  # type: ignore[call-arg] # Loaded from .env file
