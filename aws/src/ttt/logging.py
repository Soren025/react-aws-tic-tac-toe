import logging
import os

logger = logging.getLogger()
logger.setLevel(logging.getLevelName(os.getenv('LOG_LEVEL')))
