from logging import getLogger, basicConfig, INFO

basicConfig(level=INFO)
logger = getLogger(__name__)
logger.info("Logger initialized")
