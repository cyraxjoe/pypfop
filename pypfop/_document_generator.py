import os
import tempfile
import warnings
import logging
import inspect
import itertools

from pypfop import compat
from pypfop.conversion import xml_to_fo_with_style
from pypfop.builder import SubprocessBuilder, FopsBuilder
from pypfop.exceptions import DocumentGeneratorError


VALID_OFORMATS = ('pdf', 'rtf', 'tiff', 'png', 'pcl', 'ps', 'txt')
_LOG = logging.getLogger('pypfop')


class DocumentGenerator(object):
    """
    The primary way to generate a new document.

    You can define (and encouraged) to define the following properties:

    - `__style_sheets__`
    - `__style_dir__`
    - `__defparams__`
    - `__template__`
    - `__tempdir__ `
    - `__fop_cmd__`
    - `__builder__ `
    - `__builder_args__`

    style_sheets::
       A collection of the *relative file path* of the css files
       that are going to be applied to the document.
    style_dir::
       A base directory from which the relative style sheet names defined
       on  `__style_sheets__` are going be be looked up.
    defparams::
       Dictionary with defaults parameters to be passed on the generation.
    template::
       Callable accepting two parameters: `properties, format`
    You can  define the `__template__` attribute
    on each subclass or pass it as a parameter on the __init__,
    the requirement for the template is that it needs to have a callable
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
    log = None
    builder = None

    def __init__(self, template=None, stylesheets=(), oformat='pdf', instparams=None,
                 styledir=None, fop_cmd=None, tempdir=None, debug=None,
                 builder=None, log_level=logging.DEBUG):
        self._setup_log(debug, log_level)
        self.styledir = styledir or self.__style_dir__
        self.template = self._check_template(template)
        self.oformat = self._check_oformat(oformat)
        self.defparams = self._get_instparams(instparams)
        self.ssheets = self._ssheets_with_abspath(stylesheets)
        _tempdir = tempdir or self.__tempdir__ # legacy tempdir
        self._setup_builder(fop_cmd, builder, _tempdir)


    @classmethod
    def from_fops(cls, host='localhost', port=3000, *args, **kwargs):
        """
        Set the builder argument to use the FopsBuilder and generate the
        document on the fops server listening on
        ``host`` and ``port``.
        """
        kwargs['builder'] = FopsBuilder(host, port)
        return cls(*args, **kwargs)

    def _setup_builder(self, fop_cmd, builder, tempdir):
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

    def _setup_log(self, debug, log_level):
        self.log = _LOG.getChild('Document.{}'.format(id(self)))
        self.log.propagate = True
        if debug is not None:
            warnings.warn(
                'The `debug` parameter is deprecated, please use `log_level` '
                'with the appropriate logging level.')
            if debug:
                log_level = logging.DEBUG
        self.log.setLevel(log_level)

    def _check_template(self, template):
        # I wonder if this method really needs to be that pedantinc...
        if template is None and self.__template__ is None:
            raise DocumentGeneratorError("Cannot build {}, "
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
                    raise DocumentGeneratorError(
                        'The template object {} does not implement '
                        'a 1 argument "render" property (method)'.format(template))
            else:
                raise DocumentGeneratorError(
                    'The template object {} does not implement '
                    'a callable "render" property (method)'.format(template))

    def _check_oformat(self, oformat):
        oformat = oformat.lower()
        if oformat in VALID_OFORMATS:
            return oformat
        else:
            raise DocumentGeneratorError('Invalid output format {}'.format(oformat))

    def _ssheets_with_abspath(self, ssheets):
        if isinstance(ssheets, compat.BASE_STRING):
            ssheets = [ssheets,]
        return [os.path.join(self.styledir, sheet)
                for sheet in itertools.chain(self.__style_sheets__, ssheets)]

    def _get_instparams(self, params):
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
        """Generate the document and return the name of the generated
        document (file).
        """
        if oformat is None:
            oformat = self.oformat
        else:
            oformat = self._check_oformat(oformat)
        xslfo = self._generate_xslfo(params, copy_params)
        return self.builder(xslfo, oformat, self.log)
