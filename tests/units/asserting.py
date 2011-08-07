import detest

from _detest import asserting


@detest.test
def logging():

    with asserting.stack.bind([]) as log:
        assert 1 + 1 == 2
        assert 2 + 2 == 4

    assert len(log) == 2


@detest.test
def message():

    with detest.MustRaise(AssertionError) as expectation:
        assert False, 'must be True'

    assert str(expectation.exc_info[1]) == 'must be True'
