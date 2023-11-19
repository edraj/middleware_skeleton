from fastapi_sso.sso.google import GoogleSSO
from utils.settings import settings

CLIENT_ID = settings.google_client_id
CLIENT_SECRET = settings.google_client_secret


def get_google_sso() -> GoogleSSO:
    return GoogleSSO(
        CLIENT_ID,
        CLIENT_SECRET,
        redirect_uri=f"{settings.app_url}/auth/google/callback",
    )
