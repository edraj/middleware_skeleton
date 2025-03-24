from pydmart.service import DmartService

from utils.settings import settings

dmart = DmartService(
    base_url=settings.dmart_base_url,
    # username=settings.dmart_username,
    # password=settings.dmart_password
)
