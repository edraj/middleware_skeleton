from pydantic import Field
from models.enums import OTPFor
from models.json_model import JsonModel
from utils import regex


class UserOtp(JsonModel):
    user_shortname: str = Field(pattern=regex.NAME)
    otp_for: OTPFor
    otp: str
