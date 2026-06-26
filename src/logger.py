import datetime
import logging
logging.basicConfig(
    filename="log.log",
    level=logging.INFO,
    format="%(asctime)s %(filename)s:%(lineno)d - %(message)s"
)


def log(message: str):
    logging.info(message,stacklevel=2)