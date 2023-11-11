from fastapi_mail import ConnectionConfig, FastMail
from utils.settings import settings

conf = ConnectionConfig(
    MAIL_USERNAME=settings.mail_username,
    MAIL_PASSWORD=settings.mail_password,
    MAIL_FROM=settings.mail_from,
    MAIL_PORT=settings.mail_port,
    MAIL_SERVER=settings.mail_server,
    MAIL_STARTTLS=settings.mail_start_tls,
    MAIL_SSL_TLS=settings.mail_ssl_tls,
    USE_CREDENTIALS=settings.mail_user_credentials,
    VALIDATE_CERTS=settings.mail_validate_certs,
)


mailer = FastMail(conf)
