import os
import sys
import subprocess
import tempfile
import socket

if sys.version_info.major < 3:
    import httplib
else:
    import http.client as httplib

from pypfop import compat

FOP_ENV_VAR = 'FOP_CMD'

class Builder(object):
    tempdir = tempfile.gettempdir()

    def _get_tempfile(self, oformat):
        fdesc, ofilepath = tempfile.mkstemp(
            '.{}'.format(oformat), dir=self.tempdir)
        os.close(fdesc)
        return ofilepath

    def __call__(self, xslfo, out_format, log):
        raise NotImplementedError()


class SubprocessBuilder(Builder):
    """
    Subprocess based document builder.

    It will create a subprocess for each document generation.

    This is the easiest way to locally generate a document,
    with the side-effect on having a the jvm up-and-down each time
    a document gets generated.
    """
    __fop_cmd__ = ''

    def __init__(self, fop_cmd=None):
        self.fop_cmd = self._find_fop_cmd(fop_cmd)

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

    def __call__(self, xslfo, out_format, log):
        """
        Execute the subprocess of the fop command,
        it returns the filepath of the generated document.

        In case of an error, it will raise an Exception on which
        the body will be the standard error of the fop command.
        """
        ofilepath = self._get_tempfile(out_format)
        cmdargs = [self.fop_cmd, '-q', '-fo', '-',  # - == stdin
                   '-{}'.format(out_format), ofilepath]
        compat.debug_msg(log, 'cmdline %s' % cmdargs)
        proc = subprocess.Popen(cmdargs,
                                stdin=subprocess.PIPE,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE)
        _, stderr = proc.communicate(xslfo)
        stderr = stderr.decode()
        compat.debug_msg(log, stderr, 'STDERR of fop command')
        if proc.returncode:  # != 0
            raise Exception(stderr)
        else:
            return ofilepath


class FopsBuilder(Builder):
    """
    FOPS based document builder.

    The actual document generation takes places on the `fops`
    server: https://github.com/cyraxjoe/fops.

    FOPS is a HTTP server dedicated to the generation of
    documents that natively wraps the Apache fop generation functionality.

    This approach dramatically increse the document generation speed  with
    the cost of having another server running that implies using more ram.
    """

    def __init__(self, host, port):
        self.host = host
        self.port = port

    def __call__(self, xslfo, out_format, log):
        conn = httplib.HTTPConnection(self.host, self.port)
        try:
            conn.connect()
        except socket.error:
            raise Exception('Unable to connect to the fops server')
        try:
            ofilepath = self._make_document(conn, out_format, xslfo)
        except:
            raise
        else:
            return ofilepath
        finally:
            conn.close()

    def _make_document(self, conn, out_format, xslfo):
        conn.request('POST', '/{}'.format(out_format), xslfo)
        response = conn.getresponse()
        if response.status == httplib.OK:
            ofilepath = self._get_tempfile(out_format)
            with open(ofilepath, 'wb') as outfile:
                outfile.write(response.read())
            return ofilepath
        else:
            raise Exception('{}\r\n{} - code {}'
                            .format(response.read(),
                                    response.reason, response.status))
