from enum import Enum


class StrEnum(str, Enum):
    def __str__(self):
        return self.value


class Schema(StrEnum):
    sample_product = "sample_product"
    user = "user"
    otp = "otp"
    inactive_token = "inactive_token"
    order = "order"
    meta = "meta"


class Space(StrEnum):
    acme = "acme"


class Status(StrEnum):
    success = "success"
    failed = "failed"


class OperatingSystems(StrEnum):
    android = "android"
    ios = "ios"


class Language(StrEnum):
    ar = "ar"
    en = "en"
    kd = "kd"


class ResourceType(StrEnum):
    folder = "folder"
    schema = "schema"
    content = "content"
    comment = "comment"
    media = "media"
    ticket = "ticket"
    json = "json"
    lock = "lock"


class CancellationReason(StrEnum):
    not_needed = "not_needed"
    ordered_by_mistake = "ordered_by_mistake"
    changed_my_mind = "changed_my_mind"
    change_order = "change_order"


class DeliverStatus(StrEnum):
    cancelled = "cancelled"
    pending = "pending"
    confirmed = "confirmed"
    rejected = "rejected"
    assigned = "assigned"
    failed = "failed"
    delivered = "delivered"


class Gender(StrEnum):
    male = "male"
    female = "female"


class OTPOperationType(StrEnum):
    register = "register"
    login = "login"
    update_profile = "update_profile"
    forgot_password = "forgot_password"

class NotificationPriority(StrEnum):
    high = "high"
    medium = "medium"
    low = "low"