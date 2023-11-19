""" Application Settings """

import os
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Main settings class"""

    app_name: str = "dmart-middleware"
    log_file: str = "../logs/middleware.ljson.log"
    log_handlers: list[str] = ["file"]
    jwt_secret: str = ""
    jwt_algorithm: str = ""
    jwt_access_expires: int = 14400
    jwt_refresh_expires: int = 86400 * 30
    listening_host: str = "0.0.0.0"
    listening_port: int = 8081
    is_debug_enabled: bool = True
    dmart_url: str = "http://localhost:8282"
    dmart_username: str = ""
    dmart_password: str = ""
    debug_enabled: bool = True


    base_path: str = "/middleware"

    mail_username: str = ""
    mail_password: str = ""
    mail_from: str = ""
    mail_port: int = 25
    mail_server: str = ""
    mail_start_tls: bool = False
    mail_ssl_tls: bool = True
    mail_user_credentials: bool = True
    mail_validate_certs: bool = True

    sms_provider_host: str = ""
    mock_sms_provider: bool = True

    api_key: str = ""
    servername: str = ""  # This is for print purposes only.
    env_servername: str = ""  # server name in code.


    model_config = SettingsConfigDict(env_file = os.getenv("BACKEND_ENV", "config.env"), env_file_encoding = "utf-8")
settings = Settings()
# Uncomment this when you have a problem running the app to see if you have a problem with the env file
# print(settings.model_dump_json())
