from utils.settings import settings
# from os import cpu_count
from fastapi.logger import logger
from utils.logger import logging_schema


bind = [f"{settings.listening_host}:{settings.listening_port}"]
workers = 2
backlog = 400
worker_class = "asyncio"
logconfig_dict = logging_schema
errorlog = logger
