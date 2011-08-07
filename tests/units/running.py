import detest
import traceback

from _detest import running, writing
from tests.fixtures import complex


@detest.test
def run(runner, suite):
    results = runner.run(suite)
    assert len(results) == complex.TOTAL

    bystatus = {'pass': [], 'fail': [], 'error': []}
    for result in results:
        bystatus[result.status].append(result)

    assert len(bystatus['pass']) == complex.PASSING
    for result in bystatus['pass']:
        assert isinstance(result.args[0], (complex.Simple, complex.Magic))

    assert len(bystatus['fail']) == complex.FAILING
    for result in bystatus['fail']:
        assert isinstance(result.args[0], complex.Broken)

    assert len(bystatus['error']) == complex.ERRORING
    for result in bystatus['error']:
        assert isinstance(result.args[0], complex.Fatal)


@detest.test
def formatted_header(formatter):
    result = formatter.result
    parts = ['#', format(result.id, '02'), ' ']
    parts += ['tests.fixtures.complex:', result.function.__name__]
    if result.assertions:
        parts.append(' (1 assertion)')
    parts.append('\n')
    formatter.header()
    assert formatter.out.stream.getvalue() == ''.join(parts)


@detest.test
def formatted_traceback(formatter):
    result = formatter.result
    if not result.exc_info:
        return
    formatter.traceback()
    expected = ''.join(traceback.format_exception(*result.exc_info))
    assert formatter.out.stream.getvalue() == expected
