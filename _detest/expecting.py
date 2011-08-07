# encoding: utf-8
from __future__ import unicode_literals


class ExpectationError(AssertionError):

    def __str__(self):
        return unicode(self.args[0])


class MustRaise(object):

    message = None

    exc_info = (None, None, None)

    def __init__(self, *exceptions):
        self.exceptions = exceptions

    def __enter__(self):
        return self

    def __exit__(self, *exc_info):
        self.exc_info = exc_info
        if not isinstance(exc_info[1], self.exceptions):
            raise ExpectationError(self)
        return True

    def __unicode__(self):
        if self.message is not None:
            return self.message
        names = [type.__name__ for type in self.exceptions]
        if len(self.exceptions) == 1:
            message = 'expectation to raise {0} not met'
        else:
            message = 'expectation to raise ({0}) not met'
        return message.format(', '.join(names))
