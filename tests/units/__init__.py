import ast
import collections
import detest
import exceptions
import inspect
import pkg_resources
import yaml
import sys


Expression = collections.namedtuple(
    'Expression', [
        'ast',
        'expected',
        'mode'
    ]
)


Tree = collections.namedtuple(
    'Tree', [
        'data',
        'repr'
    ]
)


Diff = collections.namedtuple(
    'Diff', [
        'env',
        'left',
        'right',
        'expected'
    ]
)


class List(collections.Iterable):

    def __iter__(self):
        yield 1
        yield 2
        yield 3


def yaml_fixtures(filename):
    stream = pkg_resources.resource_stream('tests.fixtures', filename)
    with stream:
        for doc in yaml.load_all(stream):
            yield doc


def create_env(**sections):
    from _detest import writing
    env = detest.Environment()
    env.stdout = writing.MemoryWriter()
    env.stderr = writing.MemoryWriter()
    env.config.load_resource('tests.fixtures', 'config.ini')
    for section, options in sections.iteritems():
        for option, value in options.iteritems():
            env.config.set(section, option, value)
    return env


@detest.fixture
def environment():
    yield create_env()


@detest.fixture
def config():
    env = create_env()
    yield env.config


@detest.fixture
def suite():
    env = create_env()
    yield env.suite


@detest.fixture
def incomplete():
    env = create_env(suite={'modules': 'fixtures.incomplete'})
    yield env.suite


@detest.fixture
def runner():
    env = create_env()
    yield env.runner


@detest.generator
def results(result, formatter):
    from _detest import running
    env = create_env()
    for item in env.runner.run():
        yield result(item)
        yield formatter(running.ResultFormatter(
            create_env(), item, len(env.runner.tests)))


@detest.generator
def expressions(expression):
    filename = 'tests/fixtures/expressions.yml'
    for doc in yaml_fixtures('expressions.yml'):
        for mode, types in doc.iteritems():
            for input, output in types['lossy'].iteritems():
                node = ast.parse(input, filename, 'eval').body
                yield expression(Expression(node, output, mode))
            for expr in types['lossless']:
                node = ast.parse(expr, filename, 'eval').body
                yield expression(Expression(node, expr, mode))


@detest.generator
def trees(tree):
    for doc in yaml_fixtures('trees.yml'):
        yield tree(Tree(doc['data'], doc['tree'].strip()))


@detest.fixture
def importerror():
    with detest.MustRaise(ImportError) as expectation:
        yield expectation


@detest.generator
def module_names(module):
    for name in sys.modules:
        yield module(name)


@detest.generator
def exception_types(exception):
    for name, value in inspect.getmembers(exceptions, inspect.isclass):

        # these subclasses have required arguments and can't easily be
        # generically tested against so we skip them
        if issubclass(value, UnicodeError):
            continue

        yield exception(value)


@detest.generator
def diffs(diff):
    for doc in yaml_fixtures('diffs.yml'):
        for differ, deltas in doc['diffs'].iteritems():
            for generator, delta in deltas.iteritems():
                env = create_env()
                env.config.set(
                    'diffing', 'differ', 'detest:' + differ)
                env.config.set(
                    'diffing', 'delta-generator', 'difflib:' + generator)
                expected = '\n'.join(delta).strip() if delta else None
                yield diff(Diff(env, doc['left'], doc['right'], expected))
