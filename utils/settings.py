import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path
from utils.dmart import DmartService

class Settings(BaseSettings):
    """Settings class specific to logging and FastAPI webhook"""

    # Logging settings
    log_handlers: list[str] = ['console','file'] 
    log_file: str = "../logs/delivery.ljson.log"

    # API settings
    app_name: str = "Delivery MicroService"
    listening_host: str = "0.0.0.0"
    listening_port: int = 8989

    base_path: str = "/delivery"

    jwt_secret: str = ""
    jwt_algorithm: str = "HS256"
    jwt_access_expires: int = 86400 * 30


    api_authkeys : dict[str, str] = {}

    # Dmart Creds
    dmart_base_url:str=""


    # Azzajel
    azzajel_url:str="https://alzajelservice.com/api"
    azzajel_key:str=""
    azzajel_vendor_id:str=""
    mock_azzajel:bool=True


    #Oddi-jet
    oodi_jet_url:str="https://oodi.olivery.io"
    oodi_jet_username:str=""
    oodi_jet_password:str=""
    oodi_jet_db:str=""
    mock_oodi_jet:bool=True

    # Dmart

    dmart_service : DmartService = DmartService(url=dmart_base_url, username="", password="")



    # wecan_callback
    wecan_callback_url:str=""
    wecan_callback_username:str=""
    wecan_callback_password:str=""


    # Environment file loading configuration
    model_config = SettingsConfigDict(
        env_file=os.getenv(
            "BACKEND_ENV",
            str(Path(__file__).resolve().parent.parent.parent / "config.env") if __file__.endswith(".pyc") else "config.env"
        ),
        env_file_encoding="utf-8"
    )


    def fix_config(self) -> None:
        self.dmart_service.dmart_url = self.dmart_base_url

settings = Settings()
settings.fix_config()
