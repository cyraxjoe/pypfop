import os

import logging
import inspect
import itertools
import tempfile
import warnings

from pypfop import compat
from pypfop.conversion import xml_to_fo_with_style
from pypfop.builder import SubprocessBuilder, FopsBuilder

__version__ = '0.3.0a'
__version_info__ = __version__.split('.')

BASEDIR =  os.path.join(os.getcwd(), os.path.dirname(__file__))
SKELDIR = os.path.join(BASEDIR, 'skeletons')

VALID_OFORMATS = frozenset(('awt', 'pdf', 'mif', 'rtf',
                            'tiff', 'png', 'pcl', 'ps', 'txt'))

_log_handler = logging.StreamHandler()
_log_handler.setFormatter(logging.Formatter())
log = logging.getLogger('pypfop')
log.setLevel(logging.INFO)
log.addHandler(_log_handler)


def skeldir_for(tname):
    return os.path.join(SKELDIR, tname)


class Document(object):
    """Basic document, you should define the `__template__` attribute
    on each subclass or pass it as a parameter in the __init__,
    the requirement for the template is that need to have a callable
    property which accept two arguments (properties, format) that
    will be translated by the renderer to a single string.
    """
    __style_sheets__ = ()
    __style_dir__ = '.'
    __defparams__ = {}
    __template__ = None
    __tempdir__ = tempfile.gettempdir()
    __fop_cmd__ = ''
    __builder__ = SubprocessBuilder
    __builder_args__ = ()

    def __init__(self, template=None, stylesheets=(), oformat='pdf',
                 instparams=None, styledir=None, fop_cmd=None,
                 tempdir=None, debug=None, builder=None,
                 log_level=logging.DEBUG):
        self.styledir = styledir or self.__style_dir__
        self.tempdir = tempdir or self.__tempdir__
        self.log = log.getChild('Document.{}'.format(id(self)))
        self.log.propagate = True
        if debug is not None:
            warnings.warn(
                'The `debug` parameter is deprecated, please use `log_level` with '
                'the appropiate logging level.')
            if debug:
                log_level = logging.DEBUG
        self.log.setLevel(log_level)
        self.template = self._check_template(template)
        self.oformat = self._check_oformat(oformat)
        self.defparams = self._get_inst_params(instparams)
        self.ssheets = self._ssheets_with_abspath(stylesheets)
        if fop_cmd or self.__fop_cmd__: # legacy interface
            self.builder = SubprocessBuilder(fop_cmd or self.__fop_cmd__)
        else:
            if builder:
                self.builder = builder
            else:
                if isinstance(self.__builder_args__, dict):
                    self.builder = self.__builder__(**self.__builder_args__)
                else:
                    self.builder = self.__builder__(*self.__builder_args__)
        if tempdir is not None:
            self.builder.tempdir = tempdir

    @classmethod
    def from_fops(cls, host='localhost', port=3000, *args, **kwargs):
        """
        Set the builder argument to use the FopsBuilder and generate the
        document on the fops server listening on
        ``host`` and ``port``.
        """
        kwargs['builder'] = FopsBuilder(host, port)
        return cls(*args, **kwargs)


    def _check_template(self, template):
        # I wonder if this method really needs to be that pedantinc...
        if template is None and self.__template__ is None:
            raise Exception("Cannot build {}, "
                            "neither __template__ or template is set"
                            .format(self.__class__.__name__))
        else:
            if hasattr(template, 'render') and callable(template.render):
                if inspect.ismethod(template.render) and \
                       len(inspect.getargspec(template.render).args) == 2:
                    return template
                elif inspect.isfunction(template.render) and \
                         len(inspect.getargspec(template.render).args) == 1:
                    return template
                else:
                    raise Exception(
                        'The template object {} does not implement '
                        'a 1 argument "render" property (method)'.format(template))
            else:
                raise Exception(
                    'The template object {} does not implement '
                    'a callable "render" property (method)'.format(template))

    def _check_oformat(self, oformat):
        oformat = oformat.lower()
        if oformat in VALID_OFORMATS:
            return oformat
        else:
            raise Exception('Invalid output format {}'.format(oformat))

    def _ssheets_with_abspath(self, ssheets):
        if isinstance(ssheets, compat.BASE_STRING):
            ssheets = [ssheets,]
        return [os.path.join(self.styledir, sheet)
                for sheet in itertools.chain(self.__style_sheets__, ssheets)]

    def _get_inst_params(self, params):
        if isinstance(params, dict) and params:
            defparams = self.__defparams__.copy()
            defparams.update(params)
            return defparams
        else:
            return self.__defparams__

    def _generate_xslfo(self, params, copy_params):
        if copy_params:
            params = params.copy()
        params.update(self.defparams)
        xml = self.template.render(params)
        compat.debug_msg(self.log, xml, 'Generated XML')
        xslfo = xml_to_fo_with_style(xml, self.ssheets)
        compat.debug_msg(self.log, xslfo, 'Generated XSL-FO from xml_to_fo')
        return xslfo


    def generate(self, params, oformat=None, copy_params=False):
        """Return the name of the generated document.

        Raise Exception in case of an error with the fop command and use
        the stderr of the command as the body of the Exception.
        """
        if oformat is None:
            oformat = self.oformat
        else:
            oformat = self._check_oformat(oformat)
        xslfo = self._generate_xslfo(params, copy_params)
        return self.builder(xslfo, oformat, self.log)
