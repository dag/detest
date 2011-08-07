# encoding: utf-8
from __future__ import unicode_literals

import argparse
import contextlib
import inspect
import locale
import sys
import traceback
import venusian

from . import caching, config, importing, pygmentizing, sysexits, writing


class BaseEnvironment(object):

    def __init__(self):
        self.config = config.Config()

    def getbound(self, section, option):
        return self.config.getobject(section, option)(self)

    @caching.getter
    def suite(self):
        instance = self.config.getobject('suite', 'class')()
        instance.configure(self)
        return instance

    @caching.getter
    def runner(self):
        return self.getbound('environment', 'runner')

    @caching.getter
    def repr(self):
        obj = self.config.getobject('environment', 'repr')
        if inspect.isclass(obj):
            return obj().repr
        return obj


class CommandLineMixin(object):

    @classmethod
    def main(cls, args=None, prog='python -mdetest', **params):
        self = cls()
        self.config.load_local_configs()
        self.create_argparser(prog=prog, **params)
        self.parse_arguments(args)
        self.run()

    def run(self):
        self.runner.run(self.suite)
        self.stdout.newline()
        self.stderr.writeline("error: test runner didn't exit")
        sys.exit(sysexits.SOFTWARE)

    @caching.getter
    def argparser_signals(self):
        return {
            'arguments-parsed': [],
            'configured': [],
        }

    def create_argparser(self, **params):
        self.argparser = argparse.ArgumentParser(**params)
        self.scan_for_arguments('_detest.cli')

    def parse_arguments(self, args=None):
        self.cli_arguments = self.argparser.parse_args(args)
        for signal in ['arguments-parsed', 'configured']:
            for dest, callback in self.argparser_signals[signal]:
                callback(self, getattr(self.cli_arguments, dest))

    def scan_for_arguments(self, package):
        if isinstance(package, basestring):
            package = importing.import_string(package)
        scanner = venusian.Scanner(env=self)
        scanner.scan(package, ('argument',))


class TerminalMixin(object):

    @caching.getter
    def tty(self):
        if self.config.has_option('terminal', 'tty'):
            return self.config.getboolean('terminal', 'tty')
        return getattr(sys.stdout, 'isatty', bool)()

    def create_writer(self, stream, **kwargs):
        kwargs.setdefault('pygmentizer', self.pygmentize)
        kwargs.setdefault('fallback_encoding', locale.getpreferredencoding())
        kwargs.setdefault('ignore_options', not self.tty)
        kwargs.setdefault('indent', ' ' * 2)
        return writing.TerminalWriter(stream, **kwargs)

    @caching.getter
    def stdout(self):
        return self.create_writer(sys.stdout)

    @caching.getter
    def stderr(self):
        return self.create_writer(sys.stderr)

    def interact(self, local=None, banner=None):
        interpreter = self.config.getobject('environment', 'interpreter')
        kwargs = dict(local=local, locals=local, locals_=local, banner=banner)
        args = inspect.getargspec(interpreter).args
        for key in kwargs.keys():
            if key not in args:
                del kwargs[key]
        interpreter(**kwargs)

    def debug(self, frame):
        debugger = self.config.getobject('environment', 'debugger')()
        debugger.reset()
        debugger.interaction(frame, None)

    @caching.getter
    def coverage(self):
        if self.config.getboolean('terminal', 'coverage'):
            import coverage
            return coverage.coverage()

    @contextlib.contextmanager
    def covering(self):
        if self.coverage:
            self.coverage.start()
        try:
            yield
        finally:
            if self.coverage:
                self.coverage.stop()


class PygmentsMixin(object):

    def run(self):
        sys.excepthook = self.excepthook
        super(PygmentsMixin, self).run()

    def excepthook(self, *exc_info):
        tb = ''.join(traceback.format_exception(*exc_info))
        self.stderr.writelines(self.pygmentize('pytb', tb))

    @caching.getter
    def pygmentize(self):
        if not self.tty:
            return pygmentizing.NonPygmentizer()
        parts = self.config.get('terminal', 'formatter').split(None, 1)
        if len(parts) == 1:
            options = {}
        else:
            options = eval('dict({0})'.format(parts[1]))
        return pygmentizing.Pygmentizer(parts[0], **options)

    def repr_pygments(self, obj):
        return self.pygmentize('python', self.repr(obj))


class DiffingMixin(object):

    @caching.getter
    def differ(self):
        return self.getbound('diffing', 'differ')

    @caching.getter
    def delta_generator(self):
        return self.config.getobject('diffing', 'delta-generator')


class Environment(PygmentsMixin, TerminalMixin, CommandLineMixin,
                  DiffingMixin, BaseEnvironment):
    pass
