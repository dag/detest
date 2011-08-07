import inspect
import sys

from . import asserting, caching, stacking


if 'stack' not in globals():  # survive reload()
    stack = stacking.Stack()


class Result(object):

    exc_info = None

    def __init__(self, environment=None):
        self.env = environment
        self.assertions = []

    def set(self, **attributes):
        for name, value in attributes.iteritems():
            setattr(self, name, value)

    def run(self, test):
        self.test = test
        with stack.bind(self):
            try:
                with asserting.stack.bind(self.assertions):
                    test(self)
            except (Exception, SystemExit):
                self.exc_info = sys.exc_info()
                raise

    def interact(self):
        locals = dict(self.frame.f_globals, **self.frame.f_locals)
        locals.setdefault('__result__', self)
        self.env.interact(locals)

    def debug(self):
        self.env.debug(self.frame)

    @caching.getter
    def filename(self):
        return inspect.getfile(self.function)

    @caching.getter
    def traceback(self):
        tb = self.exc_info[2]
        while tb:
            frame = inspect.getframeinfo(tb)
            if (frame.filename == self.filename and
                frame.function == self.function.__name__):
                return tb
            tb = tb.tb_next

    @caching.getter
    def frame(self):
        return self.traceback.tb_frame

    @caching.getter
    def status(self):
        if not self.exc_info:
            return 'pass'
        elif issubclass(self.exc_info[0], AssertionError):
            return 'fail'
        else:
            return 'error'

    @caching.getter
    def assertion(self):
        if self.assertions:
            return self.assertions[-1]
