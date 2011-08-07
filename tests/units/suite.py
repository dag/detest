import detest

from tests.fixtures import complex


@detest.test
def fixtures(suite):
    assert suite.fixtures.keys() == ['calculator']


@detest.test
def generators(suite):
    assert len(suite.generators) == complex.GENERATORS


@detest.test
def tests(suite):
    assert len(suite.tests) == complex.TESTS


@detest.test
def build(suite):
    tests = list(suite)
    assert len(tests) == complex.TOTAL


@detest.test
def consistency(incomplete):

    with detest.MustRaise(RuntimeError) as expectation:
        list(incomplete)

    assert str(expectation.exc_info[1]) ==\
        'missing fixtures for test tests.fixtures.incomplete:missing_fixture'
