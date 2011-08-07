# encoding: utf-8
from __future__ import unicode_literals

import detest


@detest.test
def output():
    with detest.OutputCapture() as capture:
        print b'Hello, World!'
    assert capture.stdout == 'Hello, World!\n'


@detest.test
def exceptions(exception):
    try:
        with detest.ExceptionCapture(exception) as capture:
            raise exception
    except exception:
        raise AssertionError("didn't capture exception")
    else:
        assert capture.exc_info[0] is exception
