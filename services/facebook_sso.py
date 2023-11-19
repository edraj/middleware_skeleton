from fastapi_sso.sso.facebook import FacebookSSO
from utils.settings import settings

CLIENT_ID = settings.facebook_client_id
CLIENT_SECRET = settings.facebook_client_secret


def get_facebook_sso() -> FacebookSSO:
    return FacebookSSO(
        CLIENT_ID,
        CLIENT_SECRET,
        redirect_uri=f"{settings.app_url}/auth/facebook/callback",
    )
