import detest
from _detest import inspecting


EXPRESSION_MODES = dict(
    normal=inspecting.AstSource,
    simple=inspecting.SimpleAstSource,
)


@detest.test
def expressions(expression):
    builder = EXPRESSION_MODES[expression.mode](expression.ast)
    assert unicode(builder) == expression.expected
