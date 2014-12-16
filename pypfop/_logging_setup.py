import logging

_logger = logging.getLogger('pypfop')
_log_handler = logging.StreamHandler()
_log_handler.setFormatter(logging.Formatter())
_logger.setLevel(logging.INFO)
_logger.addHandler(_log_handler)
