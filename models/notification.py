

from datetime import datetime
from pydantic import BaseModel
from models.base.enums import NotificationPriority
from models.base.json_model import JsonModel

class Translation(BaseModel):
    en: str | None = None
    ar: str | None = None
    ku: str | None = None
    
class Notification(JsonModel):
    shortname: str
    displayname: Translation
    description: Translation
    created_at: datetime
    updated_at: datetime
    owner_shortname: str
    
    is_read: bool = False
    priority: NotificationPriority
    
    @classmethod
    def payload_body_attributes(cls) -> set[str]:
        return set()

    @classmethod
    def class_attributes(cls) -> set[str]:
        return {
            "shortname", "displayname", "description", "created_at", "updated_at", "owner_shortname", "is_read", "priority"
        }
    