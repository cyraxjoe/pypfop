import os
import logging
import inspect
import itertools

from pypfop.conversion import xml_to_fo_with_style
from pypfop.builder import SubprocessBuilder, FopsBuilder
from pypfop.exceptions import DocumentGeneratorError


logger = logging.getLogger('pypfop')

OUTPUT_FORMATS = ('pdf', 'rtf', 'tiff', 'png', 'pcl', 'ps', 'txt')


class DocumentGenerator:
    """The primary way to generate a new document.

    You can define (and encouraged) to define the following properties:

    - `__style_sheets__`
    - `__style_dir__`
    - `__defparams__`
    - `__template__`

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

    def __init__(self, template=None, stylesheets=(), out_format='pdf',
                 instparams=None, style_dir=None, fop_cmd=None,
                 tempdir=None, builder=None, log_level=logging.INFO):
        self._setup_log(log_level)
        self.style_dir = style_dir or self.__style_dir__
        self.template = self._check_template(template)
        self.out_format = self._check_out_format(out_format)
        self.defparams = self._get_instparams(instparams)
        self.ssheets = self._ssheets_with_abspath(stylesheets)
        self._setup_builder(fop_cmd, builder, tempdir)

    @classmethod
    def from_fops(cls, host='localhost', port=3000, *args, **kwargs):
        """Set the builder argument to use the FopsBuilder and generate the
        document on the fops server listening on ``host`` and ``port``.
        """
        kwargs['builder'] = FopsBuilder(host, port)
        return cls(*args, **kwargs)

    def _setup_builder(self, fop_cmd, builder, tempdir):
        if builder:
            self.builder = builder
        else:
            self.builder = SubprocessBuilder(fop_cmd)
        if tempdir is not None:
            self.builder.tempdir = tempdir

    def _setup_log(self, log_level):
        self.log = logger.getChild(
            '{}.{}'.format(self.__class__.__name__, id(self))
        )
        self.log.propagate = True
        self.log.setLevel(log_level)

    def _check_template(self, template):
        # I wonder if this method really needs to be that pedantic...
        if template is None and self.__template__ is None:
            raise DocumentGeneratorError(
                "Cannot build {}, neither __template__ or template is set"
                .format(self.__class__.__name__)
            )
        if not (hasattr(template, 'render') and callable(template.render)):
            raise DocumentGeneratorError(
                'The template object {} does not implement '
                'a callable "render" property (method)'.format(template)
            )
        expected_args = 1
        if inspect.ismethod(template.render):
            expected_args = 2
        if len(inspect.getargspec(template.render).args) != expected_args:
            raise DocumentGeneratorError(
                'The template object {} does not implement '
                'a 1 argument "render" property (method)'
                .format(template)
            )
        return template

    def _check_out_format(self, out_format):
        out_format = out_format.lower()
        if out_format in OUTPUT_FORMATS:
            return out_format
        else:
            raise DocumentGeneratorError(
                'Invalid output format {}'.format(out_format)
            )

    def _ssheets_with_abspath(self, ssheets):
        if isinstance(ssheets, str):
            ssheets = [ssheets, ]
        return [os.path.join(self.style_dir, sheet)
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
        self.log.debug('Generated XML: {}'.format(xml))
        xslfo = xml_to_fo_with_style(xml, self.ssheets)
        self.log.debug(
            'Generated XSL-FO from xml_to_fo: {}'
            .format(xslfo)
        )
        return xslfo

    def generate(self, params, out_format=None, copy_params=False):
        """Generate the document and return the name of the generated
        document (file).
        """
        if out_format is None:
            out_format = self.out_format
        else:
            out_format = self._check_out_format(out_format)
        xslfo = self._generate_xslfo(params, copy_params)
        return self.builder(xslfo, out_format, self.log)
