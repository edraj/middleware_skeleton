import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path


class Settings(BaseSettings):
    """Settings class specific to logging and FastAPI webhook"""

    # Logging settings
    log_handlers: list[str] = ['console','file'] 
    log_file: str = "../logs/delivery.ljson.log"

    # API settings
    app_name: str = "Dmart MicroService"
    listening_host: str = "0.0.0.0"
    listening_port: int = 8989

    base_path: str = "/"

    jwt_secret: str = ""
    jwt_algorithm: str = "HS256"
    jwt_access_expires: int = 86400 * 30

    # Dmart Creds
    dmart_base_url:str=""
    dmart_username:str=""
    dmart_password:str=""


    # Environment file loading configuration
    model_config = SettingsConfigDict(
        env_file=os.getenv(
            "BACKEND_ENV",
            str(Path(__file__).resolve().parent.parent.parent / "config.env") if __file__.endswith(".pyc") else "config.env"
        ),
        env_file_encoding="utf-8"
    )


settings = Settings()
