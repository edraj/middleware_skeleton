""" Application Settings """

import os
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Main settings class"""

    app_name: str = "dmart-middleware"
    app_url: str = ""
    log_file: str = "../logs/middleware.ljson.log"
    log_handlers: list[str] = ["console", "file"]
    jwt_secret: str = ""
    jwt_algorithm: str = ""
    jwt_access_expires: int = 14400
    jwt_refresh_expires: int = 86400 * 30
    listening_host: str = "0.0.0.0"
    listening_port: int = 8081
    is_debug_enabled: bool = True
    redis_host: str = "127.0.0.1"
    redis_password: str = ""
    redis_port: int = 6379
    dmart_url: str = "http://localhost:8282"
    dmart_username: str = ""
    dmart_password: str = ""
    debug_enabled: bool = True
    logger_password_hash_key: str = b"ZmDfcTF7_60GrrY167zsiPd67pEvs0aGOv2oasOM1Pg="
    access_token_expire: int = 86400
    otp_expire: int = 300 # seconds

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

    google_client_id: str = ""
    google_client_secret: str = ""

    facebook_client_id: str = ""
    facebook_client_secret: str = ""

    github_client_id: str = ""
    github_client_secret: str = ""

    microsoft_client_id: str = ""
    microsoft_client_secret: str = ""

    model_config = SettingsConfigDict(
        env_file=os.getenv("BACKEND_ENV", "config.env"), env_file_encoding="utf-8"
    )


settings = Settings()
# Uncomment this when you have a problem running the app to see if you have a problem with the env file
# print(settings.model_dump_json())
