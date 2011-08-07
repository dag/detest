import abc
import ast
import imp
import os
import sys

from . import asserting
from brownie import importing


def import_string(name):
    return importing.import_string(str(name))


_find_module_cache = {}


def find_module(name, path=None):
    if name not in _find_module_cache:
        module_name = name.rsplit('.', 1)[-1]
        _find_module_cache[name] = imp.find_module(module_name, path)
    return _find_module_cache[name]


def get_sourcefile(fd, fn, info):
    if info[2] == imp.PY_SOURCE:
        return fn
    elif info[2] == imp.PY_COMPILED:
        return fn[:-1]
    elif info[2] == imp.PKG_DIRECTORY:
        return os.path.join(fn, '__init__.py')


class AbstractImporter(object):

    __metaclass__ = abc.ABCMeta

    def __init__(self, *packages):
        self.packages = packages
        self.paths = {}

    def __enter__(self):
        sys.meta_path.insert(0, self)

    def __exit__(self, *exc_info):
        sys.meta_path[:] = [finder for finder in sys.meta_path
                            if finder is not self]

    def find_module(self, name, path=None):
        if self.isignored(name):
            return
        try:
            find_module(name, path)
        except ImportError:
            return
        self.paths[name] = path
        return self

    def isignored(self, name):
        return (name not in self.packages and
                not any(name.startswith(package + '.')
                        for package in self.packages))

    @abc.abstractmethod
    def load_module(self, name):
        pass


class AbstractCompilingImporter(AbstractImporter):

    def load_module(self, name):
        fd, fn, info = find_module(name, self.paths[name])
        filename = get_sourcefile(fd, fn, info)
        if filename is None:
            return imp.load_module(name, fd, fn, info)
        code = self.compile(filename)
        module = imp.new_module(name)
        module.__file__ = filename
        if info[2] == imp.PKG_DIRECTORY:
            module.__path__ = [fn]
        sys.modules[name] = module
        vars(module).update(self.globals())
        exec code in vars(module)
        return module

    def globals(self):  # pragma: no cover
        return {}

    @abc.abstractmethod
    def compile(self, filename):
        pass


class AbstractTransformingImporter(AbstractCompilingImporter):

    def compile(self, filename):
        with open(filename) as stream:
            tree = ast.parse(stream.read(), filename)
        transformed = self.transform(tree)
        ast.fix_missing_locations(transformed)
        return compile(transformed, filename, 'exec')

    @abc.abstractmethod
    def transform(self, tree):
        pass


class AssertionLoggingImporter(AbstractTransformingImporter):

    def transform(self, tree):
        transformer = asserting.AssertionTransformer()
        return transformer.visit(tree)

    def globals(self):
        return {'__assert__': asserting.__assert__}


class BlockingImporter(AbstractImporter):

    def __enter__(self):
        super(BlockingImporter, self).__enter__()
        self.deleted = {}
        for name, module in sys.modules.items():
            if not self.isignored(name):
                self.deleted[name] = module
                del sys.modules[name]

    def __exit__(self, *exc_info):
        for name, module in self.deleted.iteritems():
            sys.modules.setdefault(name, module)
        super(BlockingImporter, self).__exit__(*exc_info)

    def load_module(self, name):
        raise ImportError('blocking imports for {0!r} in this context'.format(name))
