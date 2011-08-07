# encoding: utf-8
from __future__ import unicode_literals

import ConfigParser as configparser
import contextlib
import pkg_resources

from brownie import importing
from os import path


class Config(configparser.RawConfigParser, object):

    default_config = (__name__, 'defaults.ini')

    local_configs = ['~/.detest.ini', 'detest.ini']

    def __init__(self, *args, **kwargs):
        self.local_configs = list(self.local_configs)
        super(Config, self).__init__(*args, **kwargs)
        self.load_resource(*self.default_config)

    def load_resource(self, package, resource):
        stream = pkg_resources.resource_stream(package, resource)
        with contextlib.closing(stream) as fp:
            self.readfp(fp, resource)

    def load_local_configs(self):
        self.read(map(path.expanduser, self.local_configs))

    def getobject(self, section, option):
        strings = self.get(section, option)
        for string in strings.split():
            try:
                return importing.import_string(string)
            except ImportError:
                continue
        raise ImportError(strings)
