import os
import logging
import inspect
import itertools
import tempfile
import subprocess as subp

from pypfop.conversion import xml_to_fo_with_style

__version__ = '0.1.1'
__version_info__ = __version__.split('.')

BASEDIR =  os.path.join(os.getcwd(), os.path.dirname(__file__))
SKELDIR = os.path.join(BASEDIR, 'skeletons')
FOP_ENV_VAR = 'FOP_CMD'
VALID_OFORMATS = frozenset(('awt', 'pdf', 'mif', 'rtf',
                            'tiff', 'png', 'pcl', 'ps', 'txt'))


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
    __fop_cmd__ = ''
    __template__ = None
    __tempdir__ = tempfile.gettempdir()


    def __init__(self, template=None, stylesheets=(), oformat='pdf',
                 instparams=None, styledir=None, fop_cmd=None,
                 tempdir=None, debug=False):
        self.styledir = styledir or self.__style_dir__
        self.tempdir = tempdir or self.__tempdir__
        self._setup_logging()
        self.debug = debug
        self.template = self._check_template(template)
        self.oformat = self._check_oformat(oformat)
        self.fop_cmd = self._find_fop_cmd(fop_cmd)
        self.defparams = self._get_inst_params(instparams)
        self.ssheets = self._ssheets_with_abspath(stylesheets)

        

    def _check_template(self, template):
        # I wonder if this method really needs to be that pedantinc...
        if template is None and self.__template__ is None:
            raise Exception("Cannot build %s, " 
                            "neither __template__ or template is set" % \
                            self.__class__.__name__ )
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
                        'The template object %s does not implement '
                        'a 1 argument "render" property (method)' % template)
            else:
                raise Exception(
                    'The template object %s does not implement '
                    'a callable "render" property (method)' % template)
    

    def _check_oformat(self, oformat):
        oformat = oformat.lower()
        if oformat in VALID_OFORMATS:
            return oformat
        else:
            raise Exception('Invalid output format %s' % oformat)


    def _find_fop_cmd(self, fop_cmd):
        if fop_cmd is not None and fop_cmd:
            return fop_cmd
        if self.__fop_cmd__:
            return self.__fop_cmd__
        else:                
            try:
                return os.environ[FOP_ENV_VAR]
            except KeyError:
                raise Exception(
                    'Unable to find the path to execute FOP.'
                    'Check the environment variable "%s"' % FOP_ENV_VAR)


    def _setup_logging(self):
        """Overwrite this method in case that you want
        a more "intelligent" logging handler.
        """
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter())
        log = logging.getLogger('pypfop')
        log.setLevel(logging.DEBUG)
        log.addHandler(handler)
        self.log = log

    def _ssheets_with_abspath(self, ssheets):
        if isinstance(ssheets, str): 
            ssheets = [ssheets,]
        return [os.path.join(self.styledir, sheet)
                for sheet in itertools.chain(self.__style_sheets__, ssheets)]
            

    def _debug_msg(self, msg, label=''):
        if self.debug:  # TODO: Improve this method.
            if isinstance(msg, str):
                self.log.debug('%s: %s' % (label, msg))
            else:
                self.log.debug('%s: %s' % (label, msg.decode()) )

        
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
        self._debug_msg(xml, 'Generated XML')
        xslfo = xml_to_fo_with_style(xml, self.ssheets)
        self._debug_msg(xslfo, 'Generated XSL-FO from xml_to_fo')
        return xslfo


    def _get_tempfile(self):
        fd, ofilepath = tempfile.mkstemp('.' + self.oformat, dir=self.tempdir)
        os.close(fd)
        return ofilepath


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
        ofilepath = self._get_tempfile()
        cmdargs = [self.fop_cmd, '-q', '-fo', '-',  # - == stdin
                   '-%s' % oformat, ofilepath]
        self._debug_msg('cmdline %s' % cmdargs)
        with subp.Popen(cmdargs,
                        stdin=subp.PIPE, stdout=subp.PIPE,
                        stderr=subp.PIPE) as proc:
            stdout, stderr = proc.communicate(xslfo)
            self._debug_msg(stderr, 'STDERR of fop command')
            if b'SEVERE: Exception' in stderr or \
               b'GRAVE: Exception' in stderr:
                raise Exception(stderr.decode())
            else:
                return ofilepath


