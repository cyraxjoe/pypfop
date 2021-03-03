import os
import logging

from pypfop.document_generator import DocumentGenerator

__version__ = '1.0'
__version_info__ = __version__.split('.')
__all__ = ['DocumentGenerator', 'BASEDIR']

BASEDIR = os.path.join(os.getcwd(), os.path.dirname(__file__))

# configure the base logger
_log_handler = logging.StreamHandler()
_log_handler.setFormatter(logging.Formatter())
_logger = logging.getLogger(__name__)
_logger.setLevel(logging.INFO)
_logger.addHandler(_log_handler)
# we no longer need this references
del _logger, _log_handler, logging, os
