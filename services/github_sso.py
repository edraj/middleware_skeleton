from fastapi_sso.sso.github import GithubSSO
from utils.settings import settings

CLIENT_ID = settings.github_client_id
CLIENT_SECRET = settings.github_client_secret


def get_github_sso() -> GithubSSO:
    return GithubSSO(
        CLIENT_ID,
        CLIENT_SECRET,
        redirect_uri=f"{settings.app_url}/auth/github/callback",
    )
