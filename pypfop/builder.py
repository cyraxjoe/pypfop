import os
import subprocess
import tempfile
import shutil
from http import HTTPStatus
from urllib import request
from urllib.error import URLError
from urllib.parse import urlencode, urljoin


from pypfop.exceptions import BuilderError


FOP_ENV_VAR = 'FOP_CMD'


class Builder:
    tempdir = tempfile.gettempdir()

    def _get_tempfile(self, oformat):
        fdesc, ofilepath = tempfile.mkstemp(
            '.{}'.format(oformat), dir=self.tempdir
        )
        os.close(fdesc)
        return ofilepath

    def __call__(self, xslfo, out_format, log):
        raise NotImplementedError()


class SubprocessBuilder(Builder):
    """Subprocess based document builder.

    It will create a subprocess for each document generation.

    This is the easiest way to locally generate a document,
    with the side-effect of having the jvm up-and-down each time
    a document gets generated.
    """

    def __init__(self, fop_cmd=None, fop_cmd_extra_args=None):
        self.fop_cmd = self._find_fop_cmd(fop_cmd)
        if fop_cmd_extra_args is None:
            self.fop_cmd_extra_args = []
        else:
            self.fop_cmd_extra_args = list(fop_cmd_extra_args)

    def _find_fop_cmd(self, fop_cmd):
        if fop_cmd:
            return fop_cmd
        cmd = os.environ.get(
            FOP_ENV_VAR,
            shutil.which("fop")
        )
        if cmd is None:
            raise BuilderError(
                'Unable to find the path to execute FOP.'
                'Verify your PATH or the environment variable "{}"'
                .format(FOP_ENV_VAR)
            )
        return cmd

    def __call__(self, xslfo, out_format, log):
        """
        Execute the subprocess of the fop command,
        it returns the filepath of the generated document.

        In case of an error, it will raise an Exception on which
        the body will be the standard error of the fop command.
        """
        ofilepath = self._get_tempfile(out_format)
        cmdargs = [self.fop_cmd, ] + self.fop_cmd_extra_args
        cmdargs += ['-q', '-fo', '-', '-{}'.format(out_format), ofilepath]
        log.debug('cmdline {}'.format(cmdargs))
        proc = subprocess.Popen(cmdargs,
                                stdin=subprocess.PIPE,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE)
        _, stderr = proc.communicate(xslfo)
        stderr = stderr.decode()
        log.debug('STDERR of fop command: {}'.format(stderr))
        if proc.returncode:  # != 0
            raise BuilderError(stderr)
        else:
            return ofilepath


class FopsBuilder(Builder):
    """
    FOPS based document builder.

    The actual document generation takes places on the `fops`
    server: https://github.com/cyraxjoe/fops.

    FOPS is a HTTP server dedicated to the generation of
    documents that natively wraps the Apache fop generation functionality.

    This approach dramatically increase the document generation speed with
    the cost of having another server running that implies using more ram.
    """

    def __init__(
        self, host, port, protocol='http',
        url_opener=request.urlopen, **kwargs
    ):
        self.host = host
        self.port = port
        self.protocol = protocol
        self.url_opener = url_opener
        self.encoding = kwargs.get('encoding', 'utf-8')

    @staticmethod
    def server_url(host, port, protocol, part=''):
        return urljoin('{}://{}:{}/'.format(protocol, host, port), part)

    @classmethod
    def with_basic_auth(cls, host, port, protocol='http', **kwargs):
        if 'user' not in kwargs or 'passwd' not in kwargs:
            raise TypeError('Missing required parameters "user" and "passwd".')
        user, passwd = kwargs['user'], kwargs['passwd']
        realm = kwargs.get('realm', 'FOP Server')
        password_mgr = request.HTTPPasswordMgrWithDefaultRealm()
        top_level_url = cls.server_url(host, port, protocol)
        password_mgr.add_password(realm, top_level_url, user, passwd)
        handler = request.HTTPBasicAuthHandler(password_mgr)
        url_opener = request.build_opener(handler)
        return cls(host, port, protocol, url_opener.open, **kwargs)

    def _server_url(self, ext):
        return self.server_url(self.host, self.port, self.protocol, ext)

    def __call__(self, xslfo, out_format, log):
        try:
            ofilepath = self._make_document(out_format, xslfo)
        except URLError as url_error:
            raise BuilderError(
                'Unable to build the document on the fops server\n{}'
                .format(url_error)
            )
        else:
            return ofilepath

    def _build_request(self, out_format, xslfo):
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded; charset={}'
            .format(self.encoding)}
        data = urlencode({'document': xslfo}).encode(self.encoding)
        return request.Request(
            self._server_url(out_format), data=data, headers=headers
        )

    def _make_document(self, out_format, xslfo):
        response = self.url_opener(self._build_request(out_format, xslfo))
        if response.code is HTTPStatus.OK:
            ofilepath = self._get_tempfile(out_format)
            with open(ofilepath, 'wb') as outfile:
                for fragment in response:
                    outfile.write(fragment)
            return ofilepath
        else:
            raise Exception(
                '{}\r\n{} - code {}'
                .format(response.read(), response.msg, response.code)
            )
