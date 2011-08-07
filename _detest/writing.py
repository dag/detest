# encoding: utf-8
from __future__ import unicode_literals

import io

from . import caching, pygmentizing
from brownie import terminal


class TerminalWriter(terminal.TerminalWriter):

    def __init__(self, *args, **kwargs):
        self.pygmentizer = kwargs.pop('pygmentizer',
            pygmentizing.NonPygmentizer())
        super(TerminalWriter, self).__init__(*args, **kwargs)

    @caching.getter
    def encoding(self):
        return getattr(self.stream, 'encoding', None) or self.fallback_encoding

    def get_dimensions(self):
        try:
            return super(TerminalWriter, self).get_dimensions()
        except EnvironmentError:
            raise NotImplementedError

    def writelines(self, lines, **kwargs):
        if isinstance(lines, basestring):
            lines = lines.splitlines()
        return super(TerminalWriter, self).writelines(lines, **kwargs)

    def pygmentize(self, lexer, code, **options):
        pygmented = self.pygmentizer(lexer, code, **options)
        self.writelines(pygmented, escape=False)


class MemoryWriter(TerminalWriter):

    def __init__(self, **kwargs):
        super(MemoryWriter, self).__init__(
            stream=io.StringIO(), autoescape=False, **kwargs)

    def encode(self, string):
        return unicode(string)
