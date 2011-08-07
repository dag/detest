import ast
import inspect

from . import stacking


if 'ast_cache' not in globals():  # survive reload()
    ast_cache = {None: None}

if 'stack' not in globals():
    stack = stacking.Stack()


class Assertion(object):

    def __init__(self, frame=None, ast=None):
        self.frame = frame
        self.ast = ast


class AssertionTransformer(ast.NodeTransformer):

    def visit_Assert(self, node):
        ast_cache[id(node)] = node
        args = [node.test, ast.Num(id(node))]
        if node.msg is not None:
            args.append(node.msg)
        assert_call = ast.Expr(ast.Call(
            ast.Name('__assert__', ast.Load()), args, [], None, None))
        return ast.copy_location(assert_call, node)


def __assert__(condition, id, *args):
    ast = ast_cache[id]
    frame = inspect.currentframe(1)
    assertion = Assertion(frame, ast)
    log = stack.current
    if log is not None:
        log.append(assertion)
    if not condition:
        raise AssertionError(*args)
