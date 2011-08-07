import detest

from tests.fixtures import complex


@detest.test
def environment(result):
    assert isinstance(result.env, detest.Environment)


@detest.test
def status(result):
    assert result.status in ('pass', 'fail', 'error')


@detest.test
def function(result):
    assert result.function in (complex.addition, complex.multiplication)


@detest.test
def args(result):
    assert isinstance(result.args[0],
        (complex.Simple, complex.Magic, complex.Broken, complex.Fatal))
    assert result.args[1] in (5, 10)
    assert result.args[2] in (5, 10)
