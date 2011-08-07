from detest import test
from textwrap import dedent


@test
def dicts():
    assert dict(one=1, two=2, three=3) == dict(zero=0, one=1, two=2)


@test
def lists():
    assert range(5) == range(2, 6)


@test
def nested():
    assert dict(one=range(5), two=2, three=3)\
        == dict(zero=0, one=range(2, 6), two=2)


@test
def multilines():
    one = dedent("""\
        What is the answer to the ultimate question?
        Why, 42 of course!
        """)
    two = dedent("""\
        What is the atomic number of molybdenum?
        Why, 42 of course!
        """)
    assert one == two


@test
def similar():
    assert 'referer' == 'referrer'


@test
def zen():
    text1 = dedent("""\
        1. Beautiful is better than ugly.
        2. Explicit is better than implicit.
        3. Simple is better than complex.
        4. Complex is better than complicated.
        """)
    text2 = dedent("""\
        1. Beautiful is better than ugly.
        3.   Simple is better than complex.
        4. Complicated is better than complex.
        5. Flat is better than nested.
        """)
    assert text1 == text2
