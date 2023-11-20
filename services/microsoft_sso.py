from fastapi_sso.sso.microsoft import MicrosoftSSO
from utils.settings import settings

CLIENT_ID = settings.microsoft_client_id
CLIENT_SECRET = settings.microsoft_client_secret


def get_microsoft_sso() -> MicrosoftSSO:
    return MicrosoftSSO(
        CLIENT_ID,
        CLIENT_SECRET,
        redirect_uri=f"{settings.app_url}/auth/microsoft/callback",
    )
