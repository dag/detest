# encoding: utf-8
from __future__ import unicode_literals

from . import caching


class NonPygmentizer(object):

    def __init__(self, formatter=None, **options):
        pass

    def __call__(self, lexer, code, **options):
        return code


try:
    import pygments
    from pygments import formatters, lexers

except ImportError:
    Pygmentizer = NonPygmentizer

else:

    class Pygmentizer(object):

        def __init__(self, formatter, **options):
            self.formatter = formatters.get_formatter_by_name(
                formatter, **options)

        @caching.memoize
        def _lexer(self, name, **options):
            return lexers.get_lexer_by_name(name, **options)

        @caching.memoize
        def __call__(self, lexer, code, **options):
            return pygments.highlight(code,
                self._lexer(lexer, **options), self.formatter)
