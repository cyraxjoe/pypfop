import os
import sys

import pypfop._logging_setup
from pypfop.document_generator import DocumentGenerator
from pypfop.utils import ensure_fop, ensure_fops

__version__ = '0.3.0a'
__version_info__ = __version__.split('.')
__all__ = [
    'DocumentGenerator', 'ensure_fop', 'ensure_fops', 'BASEDIR'
]

BASEDIR = os.path.join(os.getcwd(), os.path.dirname(__file__))
