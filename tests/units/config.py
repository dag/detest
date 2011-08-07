import detest
import os
import sys


@detest.test
def getobject(config):
    config.set('environment', 'someobject', 'os sys')

    assert config.getobject('environment', 'someobject') is os

    with detest.BlockingImporter('os'):
        assert config.getobject('environment', 'someobject') is sys

    with detest.MustRaise(ImportError):
        with detest.BlockingImporter('os', 'sys'):
            config.getobject('environment', 'someobject')
