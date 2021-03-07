import os
import logging

from pypfop.document_generator import DocumentGenerator
from pypfop.helpers import (
    make_document_decorator,
    get_mako_template_factory,
    get_document_generator,
    generate_document
)

__version__ = '1.0a1'
__version_info__ = __version__.split('.')
__all__ = [
    'DocumentGenerator',
    'make_document_decorator', 'get_mako_template_factory',
    'get_document_generator', 'generate_document'
]


# configure the base logger
_log_handler = logging.StreamHandler()
_log_handler.setFormatter(logging.Formatter())
_logger = logging.getLogger(__name__)
_logger.setLevel(logging.INFO)
_logger.addHandler(_log_handler)
# we no longer need this references
del _logger, _log_handler, logging, os
