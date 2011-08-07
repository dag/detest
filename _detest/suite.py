# encoding: utf-8
from __future__ import unicode_literals

import collections
import contextlib
import functools
import inspect
import itertools
import venusian

from . import caching, utils, importing


class ParametricFixture(object):

    def __init__(self, name, factory):
        self.name = name
        self.factory = factory

    def __call__(self, *args, **kwargs):
        bound = functools.partial(self.factory, *args, **kwargs)
        return self.name, bound


class Fixtures(dict):

    def __missing__(self, key):
        def default(value):
            yield value
        default.__name__ = key
        self[key] = default
        return default


class Suite(object):

    def __init__(self):
        self.fixtures = Fixtures()
        self.generators = []
        self.tests = []

    def configure(self, environment):  # pragma: no cover
        pass

    def add_fixture(self, name, factory):
        self.fixtures[name] = factory

    def fixture(self, factory):
        self.add_fixture(factory.__name__, factory)
        return factory

    def add_generator(self, generator):
        self.generators.append(generator)

    def generator(self, generator):
        self.add_generator(generator)
        return generator

    def add_test(self, function):
        self.tests.append(function)

    def test(self, function):
        self.add_test(function)
        return function

    def scan(self, package, categories=None, **parameters):
        with importing.AssertionLoggingImporter(package):
            if isinstance(package, basestring):
                package = importing.import_string(str(package))
            scanner = venusian.Scanner(suite=self, **parameters)
            scanner.scan(package, categories)

    def wrap_test(self, function, contexts=()):
        @functools.wraps(function)
        def wrapper(result):
            result.function = function
            managers = [context() for context in contexts]
            with contextlib.nested(*managers) as args:
                result.args = args
                function(*args)
        return wrapper

    @caching.memoize
    def contextmanager(self, fixture):
        return contextlib.contextmanager(self.fixtures[fixture])

    def __iter__(self):

        for test in self.tests:
            test_dependencies = inspect.getargspec(test).args

            # tests without dependencies are simply run once and without
            # any fixture context
            if not test_dependencies:
                yield self.wrap_test(test)
                continue

            # with generators, a fixture might come in multiple forms
            fixtures = collections.defaultdict(list)

            # non-parametric fixtures are used directly
            for name in test_dependencies:
                if not inspect.getargspec(self.fixtures[name]).args:
                    fixtures[name].append(self.contextmanager(name))

            for generator in self.generators:
                generates = inspect.getargspec(generator).args

                # skip this generator if it isn't generating fixtures for
                # any of the test dependencies
                if not any(fixture in test_dependencies
                           for fixture in generates):
                    continue

                wrappers = [ParametricFixture(name, self.contextmanager(name))
                            for name in generates]
                for name, factory in generator(*wrappers):

                    # skip fixtures not in the test dependencies
                    if name not in test_dependencies:
                        continue

                    fixtures[name].append(factory)

            if any(name not in fixtures for name in test_dependencies):
                raise RuntimeError('missing fixtures for test {0}'
                                   .format(utils.dotted_name(test)))

            fixtures_by_position = tuple(fixtures[name]
                for name in test_dependencies)

            # create a test for each possible combination of the fixtures
            for contexts in itertools.product(*fixtures_by_position):
                yield self.wrap_test(test, contexts)


class ConfigSuite(Suite):

    def configure(self, env):
        package = env.config.get('suite', 'package')
        with importing.AssertionLoggingImporter(package):
            if env.config.has_option('suite', 'modules'):
                for module in env.config.get('suite', 'modules').split():
                    with env.covering():
                        self.scan('.'.join([package, module]))
            else:
                with env.covering():
                    self.scan(package)


@utils.decorator
def fixture(scanner, name, ob):
    scanner.suite.add_fixture(name, ob)


@utils.decorator
def generator(scanner, name, ob):
    scanner.suite.add_generator(ob)


@utils.decorator
def test(scanner, name, ob):
    scanner.suite.add_test(ob)
