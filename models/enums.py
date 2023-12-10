from enum import Enum


class StrEnum(str, Enum):
    def __str__(self):
        return self.value


class Schema(StrEnum):
    sample_product = "sample_product"
    user = "user"
    otp = "otp"
    inactive_token = "inactive_token"


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


class OTPFor(StrEnum):
    mail_verification = "mail_verification"
    mobile_verification = "mobile_verification"
    reset_password = "reset_password"
    

class ResourceType(StrEnum):
    folder = "folder"
    schema = "schema"
    content = "content"
    comment = "comment"
    media = "media"
    ticket = "ticket"
    json = "json"
    lock = "lock"
