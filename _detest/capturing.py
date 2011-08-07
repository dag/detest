# encoding: utf-8
from __future__ import unicode_literals

import io
import sys


class OutputCapture(object):

    _stdout = _stderr = None

    def __init__(self, stdout=True, stderr=True):
        if stdout:
            self._stdout = io.BytesIO()
        if stderr:
            self._std= io.BytesIO()

    def __enter__(self):
        if self._stdout:
            self._sys_stdout = sys.stdout
            sys.stdout = self._stdout
        if self._stderr:
            self._sys_stderr = sys.stderr
            sys.stderr = self._stderr
        return self

    def __exit__(self, *exc_info):
        if self._stdout:
            sys.stdout = self._sys_stdout
        if self._stderr:
            sys.stderr = self._sys_stderr

    @property
    def stdout(self):
        return self._stdout.getvalue().decode(self._sys_stdout.encoding)

    @property
    def stderr(self):
        return self._stderr.getvalue().decode(self._sys_stderr.encoding)


class ExceptionCapture(object):

    exc_info = None

    def __init__(self, *exceptions):
        self.exceptions = exceptions

    def __enter__(self):
        return self

    def __exit__(self, *exc_info):
        self.exc_info = exc_info
        return isinstance(exc_info[1], self.exceptions)
