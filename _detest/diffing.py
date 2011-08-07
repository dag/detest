# encoding: utf-8
from __future__ import unicode_literals

import inspect
import json
import numbers
import pprint

from . import representing


class AbstractDiffer(object):

    def __init__(self, environment):
        self.env = environment

    def ignore(self, value):
        return isinstance(value, numbers.Number)

    def generate_deltas(self, **kwargs):
        generator = self.env.delta_generator
        if inspect.isclass(generator):
            generator = generator().compare
        args = inspect.getargspec(generator).args
        for key in kwargs.keys():
            if key not in args:
                del kwargs[key]
        return generator(**kwargs)

    def serialize(self, value):
        raise NotImplementedError

    def diff(self, left, right, fromfile='', tofile=''):
        if self.ignore(left) or self.ignore(right):
            return
        a = self.serialize(left).splitlines()
        b = self.serialize(right).splitlines()
        deltas = self.generate_deltas(a=a, b=b,
            fromfile=fromfile, tofile=tofile, lineterm='')
        return '\n'.join(deltas)


class TreeDiffer(AbstractDiffer):

    def serialize(self, value):
        return representing.TreeRepr().repr(value, self.env.repr)


class JSONDiffer(AbstractDiffer):

    def serialize(self, value):
        if isinstance(value, basestring):
            return value
        return json.dumps(value,
            default=self.env.repr, sort_keys=True, indent=2)


class PrettyDiffer(AbstractDiffer):

    def serialize(self, value):
        if isinstance(value, basestring):
            return value
        return pprint.pformat(value, width=1)


class YAMLDiffer(AbstractDiffer):

    def serialize(self, value):
        import yaml
        return yaml.dump(value, default_flow_style=False)


class DataDiffer(AbstractDiffer):

    def diff(self, left, right, fromfile, tofile):
        import datadiff
        try:
            diff = datadiff.diff(left, right, fromfile=fromfile, tofile=tofile)
        except (datadiff.DiffNotImplementedForType, datadiff.DiffTypeError):
            pass
        else:
            return unicode(diff)
