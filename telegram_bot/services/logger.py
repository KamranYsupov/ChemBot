import logging


def log_info(text):
    logging.log(logging.INFO, text)


def log_error(text):
    logging.log(logging.ERROR, text)


def log_debug(text):
    logging.log(logging.DEBUG, text)
