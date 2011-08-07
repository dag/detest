# encoding: utf-8
from __future__ import unicode_literals

import ast
import inspect
import sys
import traceback

from . import caching, inspecting, utils, sysexits, representing, results


class Runner(object):

    def __init__(self, environment):
        self.env = environment
        self.config = environment.config

    def run(self, suite=None):
        if suite is None:
            suite = self.env.suite
        tests = list(suite)
        self.start(tests)
        for id, test in enumerate(tests, start=1):
            self.run_test(id, test)
        return self.end()

    def start(self, tests):
        self.tests = tests
        self.results = []
        self.failures = 0

    def run_test(self, id, test):
        result = results.Result(self.env)
        result.set(id=id, runner=self)
        try:
            result.run(test)
        except (Exception, SystemExit):
            self.failed(result)
        else:
            self.passed(result)

    def failed(self, result):
        self.failures += 1
        self.results.append(result)

    def passed(self, result):
        self.results.append(result)

    def end(self):
        return self.results


class TerminalRunner(Runner):

    def __init__(self, environment):
        super(TerminalRunner, self).__init__(environment)
        self.out = environment.stdout
        self.err = environment.stderr

    @caching.getter
    def progress(self):
        if self.env.tty and self.config.has_option('terminal', 'progressbar'):
            return self.out.progress(
                self.config.get('terminal', 'progressbar'),
                maxsteps=len(self.tests))

    def clear_progress(self):
        self.progress.writer.write('\r' + (' ' * self.out.get_width()))

    def progress_hint(self, test):
        name = utils.dotted_name(test)
        if not self.failures:
            return name
        return '{0} ({1} failed)'.format(name, self.failures)

    def start(self, tests):
        if not tests:
            self.err.writeline('error: empty suite')
            sys.exit(sysexits.CONFIG)
        super(TerminalRunner, self).start(tests)
        if self.progress:
            self.progress.init()

    def run_test(self, id, test):
        if self.progress:
            self.clear_progress()
            self.progress.next(hint=self.progress_hint(test))
        try:
            with self.env.covering():
                super(TerminalRunner, self).run_test(id, test)
        except KeyboardInterrupt:
            self.end(aborted=True)

    def failed(self, result):
        super(TerminalRunner, self).failed(result)
        if self.config.getboolean('terminal', 'fail-fast'):
            raise KeyboardInterrupt

    def end(self, aborted=False):
        status = sysexits.OK
        if self.env.coverage:
            self.env.coverage.save()
        if self.progress:
            self.progress.finish()
            self.clear_progress()
        interacted = False
        interactive = self.config.getboolean('terminal', 'interactive')
        debug = self.config.getboolean('terminal', 'debug')
        verbose = self.config.getboolean('terminal', 'verbose')
        for result in self.results:
            if not interacted and result.exc_info:
                interacted = True
                if interactive:
                    result.interact()
                elif debug:
                    result.debug()
            if verbose or result.exc_info:
                self.out.newline()
                ResultFormatter(self.env, result, len(self.tests)).write()
        if self.failures:
            status = 1
        elif len(self.tests) != len(self.results):
            status = 130
        self.out.newline()
        self.out.newline()
        with self.out.options(indentation=True):
            StatsFormatter(self.env, self.tests, self.results).write()
        sys.exit(status)


class ResultFormatter(object):

    status_color = {
        'pass': 'green',
        'fail': 'yellow',
        'error': 'red',
    }

    def __init__(self, environment, result, total=1):
        self.env = environment
        self.out = environment.stdout
        self.result = result
        self.total = total

    def write(self):
        self.docstring()
        with self.out.options(faint=True, underline=True):
            self.out.hr(' ')
        self.header()
        self.out.newline()
        self.fixtures()
        self.traceback()
        self.assertion()

    def docstring(self):
        doc = inspect.getdoc(self.result.function)
        if doc:
            self.out.newline()
            self.out.pygmentize('rst', doc)

    def header(self):
        with self.out.line():
            id = '#{0:0{1}} '.format(self.result.id, len(str(self.total)))
            self.out.write(id, text_colour=self.status_color[self.result.status])
            self.out.write(utils.dotted_name(self.result.function), bold=True)
            assertions = len(self.result.assertions)
            if assertions:
                plural = utils.pluralize(assertions, 'assertion')
                self.out.write(' ({0} {1})'.format(assertions, plural),
                               text_colour='teal')

    def fixtures(self):
        if not self.result.args:
            return
        names = inspect.getargspec(self.result.function).args
        for name, value in zip(names, self.result.args):
            self.out.writeline('{0} ='.format(name))
            with self.out.options(indentation=True):
                tree = representing.TreeRepr().repr(value, self.env.repr_pygments)
                self.out.writelines(tree)
        self.out.newline()

    def traceback(self):
        tb = ''.join(traceback.format_exception(*self.result.exc_info))
        self.out.pygmentize('pytb', tb)

    def assertion(self):
        if self.result.assertion:
            inspector = AssertionInspector(self.env)
            inspector.inspect(self.result.assertion)


class AssertionInspector(ast.NodeVisitor):

    def __init__(self, environment):
        self.env = environment
        self.out = environment.stdout
        self._eval_cache = {}

    def inspect(self, assertion):
        self.assertion = assertion
        self.out.newline()
        self.visit(self.assertion.ast)

    def eval(self, node):
        if id(node) not in self._eval_cache:
            expr = ast.Expression(node)
            code = compile(expr, '<string>', 'eval')
            frame = self.assertion.frame
            value = eval(code, frame.f_globals, frame.f_locals)
            self._eval_cache[id(node)] = value
        return self._eval_cache[id(node)]

    def source(self, node):
        return unicode(inspecting.SimpleAstSource(node, self.env.repr))

    def visit_Compare(self, node):
        if self.eval(node):
            return

        self.out.pygmentize('python', 'assert {0}'.format(self.source(node)))

        arrow = '\N{HEAVY BLACK CURVED DOWNWARDS AND RIGHTWARDS ARROW}'
        leftval = self.eval(node.left)
        for op, right in zip(node.ops, node.comparators):
            rightval = self.eval(right)

            if inspecting.check(op, leftval, rightval):
                continue

            self.out.write(' ' * 5)
            self.out.write(arrow)
            self.out.write(' ')
            self.out.pygmentize('python', ' '.join(
                [self.env.repr(leftval),
                 inspecting.getinverse(op),
                 self.env.repr(rightval)]))

            diff = self.env.differ.diff(
                leftval, rightval,
                fromfile=self.source(node.left),
                tofile=self.source(right))

            if diff is not None:
                self.out.newline()
                self.out.pygmentize('diff', diff)


class StatsFormatter(object):

    passed = failures = errors = skipped = 0

    def __init__(self, environment, tests, results):
        self.env = environment
        self.out = environment.stdout
        self.tests = tests
        self.results = results
        self._count()

    def _count(self):
        for result in self.results:
            if result.status == 'pass':
                self.passed += 1
            elif result.status == 'fail':
                self.failures += 1
            elif result.status == 'error':
                self.errors += 1
        self.skipped = len(self.tests) - len(self.results)
        self.assertions = sum(len(result.assertions) for result in self.results)

    def write(self):
        with self.out.line():
            if self.passed == len(self.tests):
                self.out.write('\N{CHECK MARK} ', text_colour='green')
            else:
                self.out.write('\N{BALLOT X} ', text_colour='red')
            self._print(self.passed, 'passed', 'green', prefix=None, force=True)
            self._print(self.failures, 'failed', 'yellow')
            self._print(self.errors, 'error', pluralize=True)
            self._print(self.skipped, 'aborted')
            self._print(self.assertions, 'assertion', 'teal', pluralize=True)

    def _print(self, number, suffix, color='red', prefix=' / ',
               pluralize=False, force=False):
        if number or force:
            if prefix:
                self.out.write(prefix)
            with self.out.options(text_colour=color):
                self.out.write(unicode(number))
                self.out.write(' ')
                if pluralize:
                    self.out.write(utils.pluralize(number, suffix))
                else:
                    self.out.write(suffix)
