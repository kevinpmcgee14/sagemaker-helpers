import logging

logging_format = ' %(name)s :: %(levelname)-8s :: %(message)s'
logging.basicConfig(level=logging.WARNING, format=logging_format)

logging.getLogger().setLevel(logging.WARNING)

logger = logging.getLogger()