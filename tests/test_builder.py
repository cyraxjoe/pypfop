import logging
import subprocess
from unittest.mock import Mock, patch

import pytest

from pypfop import builder




def test_builder_invalid_instance():
    doc_builder = builder.Builder()
    with pytest.raises(NotImplementedError):
        doc_builder("foo", "bar", None)


def test_subprocess_builder_missing_fop():
    with patch('shutil.which', return_value=None):
        with pytest.raises(builder.BuilderError):
            builder.SubprocessBuilder(None, None)


def test_subprocess_builder_using_system_fop():
    with patch('shutil.which', return_value='/usr/bin/fop'):
        doc_builder = builder.SubprocessBuilder(None, None)
        assert doc_builder.fop_cmd == '/usr/bin/fop'


def test_subprocess_builder_using_custom_fop():
    doc_builder = builder.SubprocessBuilder('my-custom-fop', None)
    assert doc_builder.fop_cmd == 'my-custom-fop'


def test_subprocess_builder_with_custom_args():
    doc_builder = builder.SubprocessBuilder(
        'fop', fop_cmd_extra_args=['a', 'b', 'c']
    )
    assert doc_builder.fop_cmd_extra_args == ['a', 'b', 'c']


@patch('subprocess.Popen', spec=subprocess.Popen, **{
    'communicate.return_value': (b'', b''),
    'returncode': 0
})
def test_subprocess_builder_success_call(subproc_popen_mock):
    with patch.object(
            builder.SubprocessBuilder,
            '_get_tempfile',
            return_value='mocked-output-file.pdf'
    ):
        doc_builder = builder.SubprocessBuilder('fop')
        generated_doc_path = doc_builder(
            '<root></root>', 'pdf', Mock(logging.getLogger())
        )
        assert generated_doc_path == 'mocked-output-file.pdf'


@patch('subprocess.Popen', spec=subprocess.Popen, **{
    'communicate.return_value': (b'', b'ERROR'),
    'returncode': 1
})
def test_subprocess_builder_error_call(subproc_popen_mock):
    with patch.object(
            builder.SubprocessBuilder,
            '_get_tempfile',
            return_value='mocked-output-file.pdf'
    ):
        with pytest.raises(builder.BuilderError):
            builder.SubprocessBuilder('fop')(
                '<root></root>', 'pdf', Mock(logging.getLogger())
            )
