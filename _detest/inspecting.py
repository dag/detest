import ast

from _ast import *
from operator import *


FUNCTIONS = {
    Lt:    lt,
    LtE:   le,
    Eq:    eq,
    NotEq: ne,
    GtE:   ge,
    Gt:    gt,
    Is:    is_,
    IsNot: is_not,
}


OPERATORS = {
    And:      'and',
    Or:       'or',
    Add:      '+',
    Sub:      '-',
    Mult:     '*',
    Pow:      '**',
    Div:      '/',
    FloorDiv: '//',
    Mod:      '%',
    LShift:   '<<',
    RShift:   '>>',
    BitOr:    '|',
    BitAnd:   '&',
    BitXor:   '^',
    Eq:       '==',
    Gt:       '>',
    GtE:      '>=',
    In:       'in',
    Is:       'is',
    IsNot:    'is not',
    Lt:       '<',
    LtE:      '<=',
    NotEq:    '!=',
    NotIn:    'not in',
    Invert:   '~',
    Not:      'not',
    UAdd:     '+',
    USub:     '-',
}


OPPOSITES = {
    Eq:  NotEq,
    Is:  IsNot,
    In:  NotIn,
    Gt:  LtE,
    GtE: Lt,
}

for key, value in OPPOSITES.items():
    OPPOSITES[value] = key


def check(node, left, right):
    return FUNCTIONS[type(node)](left, right)

def getoperator(node):
    return OPERATORS[type(node)]

def getinverse(node):
    return OPERATORS[OPPOSITES[type(node)]]


def _commatizer():
    yield
    while True:
        yield ', '


class AstSource(ast.NodeVisitor):

    def __init__(self, node, repr=repr):
        self.repr = repr
        self.parts = []
        self.visit(node)

    def __unicode__(self):
        return ''.join(self.parts)

    def visit(self, node):
        for part in super(AstSource, self).visit(node):
            if isinstance(part, AST):
                self.visit(part)
            elif part is not None:
                self.parts.append(part)

    def generic_visit(self, node):
        yield '<AST: {0}>'.format(ast.dump(node))

    def visit_Compare(self, node):
        yield '('
        yield node.left
        for op, right in zip(node.ops, node.comparators):
            yield ' {0} '.format(OPERATORS[type(op)])
            yield right
        yield ')'

    def visit_BinOp(self, node):
        yield '('
        yield node.left
        yield ' {0} '.format(OPERATORS[type(node.op)])
        yield node.right
        yield ')'

    def visit_Name(self, node):
        yield node.id

    def visit_Attribute(self, node):
        yield node.value
        yield '.'
        yield node.attr

    def visit_Str(self, node):
        yield self.repr(node.s)

    visit_Bytes = visit_Str

    def visit_Num(self, node):
        yield self.repr(node.n)

    def visit_List(self, node):
        yield '['
        comma = _commatizer()
        for element in node.elts:
            yield next(comma)
            yield element
        yield ']'

    def visit_Dict(self, node):
        yield '{'
        comma = _commatizer()
        for key, value in zip(node.keys, node.values):
            yield next(comma)
            yield key
            yield ': '
            yield value
        yield '}'

    def visit_Call(self, node):
        yield node.func
        yield '('
        comma = _commatizer()
        for arg in node.args:
            yield next(comma)
            yield arg
        for kw in node.keywords:
            yield next(comma)
            yield kw.arg
            yield '='
            yield kw.value
        if node.starargs is not None:
            yield next(comma)
            yield '*'
            yield node.starargs
        if node.kwargs is not None:
            yield next(comma)
            yield '**'
            yield node.kwargs
        yield ')'


class SimpleAstSource(AstSource):

    def visit_Compare(self, node):
        yield node.left
        for op, right in zip(node.ops, node.comparators):
            yield ' {0} '.format(OPERATORS[type(op)])
            yield right
