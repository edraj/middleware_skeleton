import re

NAME = "^[a-zA-Z\u0621-\u064A0-9\u0660-\u0669_]{1,64}$"
PASSWORD = "^[A-Za-z0-9@#$%^&+=]{8,}$"
EMAIL = (
    "^[a-zA-Z\u0621-\u064A0-9\u0660-\u0669_\\.-]+@([a-zA-Z\u0621-\u064A0-9\u0660-\u0669_-]+\\.)+"
    "[a-zA-Z\u0621-\u064A0-9\u0660-\u0669_-]{2,4}$"
)
MSISDN = "^[1-9][0-9]{9}$"  # Exactly 10 digits, not starting with zero
URL = "^(http(s)?:\/\/)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)$"

# SUBPATH = "^[a-zA-Z\u0621-\u064A0-9\u0660-\u0669_/]{1,128}$"
# FILENAME = re.compile(
#     "^[a-zA-Z\u0621-\u064A0-9\u0660-\u0669_]{1,32}\\.(gif|png|jpeg|jpg|pdf|wsq|mp3|mp4)$"
# )
# USERNAME = "^[a-zA-Z\u0621-\u064A0-9\u0660-\u0669_]{3,10}$"
# SPACENAME = "^[a-zA-Z\u0621-\u064A0-9\u0660-\u0669_]{1,32}$"
# EXT = "^(gif|png|jpeg|jpg|json|md|pdf|wsq|mp3|mp4)$"
# IMG_EXT = "^(gif|png|jpeg|jpg|wsq)$"
# META_DOC_ID = (
#     "^[a-zA-Z\u0621-\u064A0-9\u0660-\u0669_]*:[a-zA-Z\u0621-\u064A0-9\u0660-\u0669_]"
#     "[a-zA-Z\u0621-\u064A0-9\u0660-\u0669_]*:meta:[a-zA-Z\u0621-\u064A0-9\u0660-\u0669_/]+$"
# )
# EXTENDED_MSISDN = (
#     "^[1-9][0-9]{9,14}$"  # Between 10 and 14 digits, not starting with zero
# )
# OTP_CODE = "^[0-9\u0660-\u0669]{6}$"  # Exactly 6 digits
# INVITATION = (
#     "^([a-zA-Z\u0621-\u064A0-9\u0660-\u0669_=]+)\\.([a-zA-Z\u0621-\u064A0-9\u0660-\u0669_=]+)"
#     "\\.([a-zA-Z\u0621-\u064A0-9\u0660-\u0669_+/=-]*)$"
# )

# FILE_PATTERN = re.compile(
#     "\\.dm/([a-zA-Z\u0621-\u064A0-9\u0660-\u0669_]*)/meta\\.([a-zA-Z\u0621-\u064A]*)\\.json$"
# )
# PAYLOAD_FILE_PATTERN = re.compile("([a-zA-Z\u0621-\u064A0-9\u0660-\u0669_]*)\\.json$")
# # HISTORY_PATTERN = re.compile("([0-9\u0660-\u0669]*)\\.json$")
# ATTACHMENT_PATTERN = re.compile(
#     "attachments\\.*[a-zA-Z\u0621-\u064A0-9\u0660-\u0669_]*\\.([a-zA-Z\u0621-\u064A0-9\u0660-\u0669_]+)"
#     "/meta\\.([a-zA-Z\u0621-\u064A0-9\u0660-\u0669_]*)\\.json$"
# )
# FOLDER_PATTERN = re.compile(
#     "/([a-zA-Z\u0621-\u064A0-9\u0660-\u0669_]*)/\\.dm/meta\\.folder\\.json$"
# )
# SPACES_PATTERN = re.compile(
#     "/([a-zA-Z\u0621-\u064A0-9\u0660-\u0669_]*)/\\.dm/meta\\.space\\.json$"
# )
