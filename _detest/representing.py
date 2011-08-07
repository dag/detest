# encoding: utf-8
from __future__ import unicode_literals

import collections
import repr as reprlib

from . import utils, writing
from contextlib import contextmanager


class AttributeRepr(reprlib.Repr, object):

    def repr(self, obj):
        if isinstance(obj, object) and\
           getattr(obj.__repr__, '__objclass__', None) is object:
            return u'<{0} {1}>'.format(utils.dotted_name(type(obj)),
                                       self.repr(vars(obj)))
        return super(AttributeRepr, self).repr(obj)


class TreeRepr(object):

    types = [
        basestring,
        collections.Mapping,
        collections.Sequence,
        collections.Iterable,
    ]

    def repr(self, obj, fallback=repr):
        self.fallback = fallback
        self.writer = writing.MemoryWriter(indent=' ' * 2)
        self.visit(obj)
        return self.writer.stream.getvalue().strip('\n')

    def visit(self, obj):
        for base in self.types:
            if isinstance(obj, base):
                getattr(self, 'visit_' + base.__name__)(obj)
                break
        else:
            self.generic_visit(obj)

    def generic_visit(self, obj):
        with self.writer.line():
            self.writer.write('\N{BULLET} ')
            self.writer.write(self.fallback(obj))

    def indented(self):
        return self.writer.options(indentation=True)

    @contextmanager
    def nesting(self, obj):
        with self.writer.line():
            self.writer.write('<')
            self.writer.write(utils.dotted_name(type(obj)))
            self.writer.write('>')
        with self.indented():
            yield
        self.writer.newline()

    def visit_basestring(self, obj):
        with self.nesting(obj):
            self.writer.writelines(obj.splitlines())

    def visit_Mapping(self, obj):
        with self.nesting(obj):
            for name, value in sorted(obj.items()):
                with self.writer.line():
                    self.writer.write(self.fallback(name))
                    self.writer.write(':')
                with self.indented():
                    self.visit(value)

    def visit_Sequence(self, obj):
        with self.nesting(obj):
            for value in obj:
                self.visit(value)

    def visit_Iterable(self, obj):
        with self.nesting(obj):
            for value in sorted(obj):
                self.visit(value)
