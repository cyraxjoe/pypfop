import os
import pypfop._logging_setup
from pypfop._document import Document, VALID_OFORMATS

__version__ = '0.3.0a'
__version_info__ = __version__.split('.')

__all__ = ['Document', 'skeldir_for']

_BASEDIR =  os.path.join(os.getcwd(), os.path.dirname(__file__))
_SKELDIR = os.path.join(_BASEDIR, 'skeletons')


def skeldir_for(tname):
    return os.path.join(_SKELDIR, tname)
