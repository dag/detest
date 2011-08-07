import detest

from _detest import expecting


@detest.test
def must_raise_catch_one(exception):
    try:
        with detest.MustRaise(exception):
            raise exception
    except exception:
        raise AssertionError("didn't catch expected exception")


@detest.test
def must_raise_nothing_raised(exception):
    try:
        with detest.MustRaise(exception):
            pass
    except expecting.ExpectationError as exc:
        name = exception.__name__
        assert str(exc) == 'expectation to raise {0} not met'.format(name)
    else:
        raise AssertionError("didn't fail when expected exception not raised")


@detest.test
def must_raise_custom_message(exception):
    try:
        with detest.MustRaise(exception) as expectation:
            expectation.message = 'raise me up, before you go-go'
    except expecting.ExpectationError as exc:
        assert str(exc) == 'raise me up, before you go-go'


@detest.test
def must_raise_multiple_exceptions():
    try:
        with detest.MustRaise(ValueError, RuntimeError):
            pass
    except expecting.ExpectationError as exc:
        assert str(exc) == 'expectation to raise (ValueError, RuntimeError) not met'

    try:
        with detest.MustRaise(ValueError, RuntimeError):
            raise RuntimeError
    except (ValueError, RuntimeError):
        raise AssertionError("didn't catch expected exception")

    try:
        with detest.MustRaise(ValueError, RuntimeError):
            raise ValueError
    except (ValueError, RuntimeError):
        raise AssertionError("didn't catch expected exception")
