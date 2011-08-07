import operator

from detest import fixture, generator, test


CALCULATORS = 4
LEFTS       = 2
RIGHTS      = 2
GENERATORS  = 2
TESTS       = 2
PASSING     = 2 * LEFTS * RIGHTS * TESTS
FAILING     = 1 * LEFTS * RIGHTS * TESTS
ERRORING    = 1 * LEFTS * RIGHTS * TESTS
TOTAL       = CALCULATORS * LEFTS * RIGHTS * TESTS


class Simple(object):

    def add(self, x, y):
        return x + y

    def multiply(self, x, y):
        return x * y


class Magic(object):

    def __getattr__(self, name):
        return getattr(operator, name[:3])


class Broken(object):

    def add(self, x, y):
        return x * y

    def multiply(self, x, y):
        return x + y


class Fatal(object):

    def add(self, x, y):
        return x / 0

    def multiply(self, x, y):
        return y / 0


@fixture
def calculator(cls):
    yield cls()


@generator
def calculators(calculator):
    yield calculator(Simple)
    yield calculator(Magic)
    yield calculator(Fatal)
    yield calculator(Broken)


@generator
def numbers(left, right):
    yield left(5)
    yield left(10)
    yield right(5)
    yield right(10)


@test
def addition(calculator, left, right):
    assert calculator.add(left, right) == left + right


@test
def multiplication(calculator, left, right):
    assert calculator.multiply(left, right) == left * right
