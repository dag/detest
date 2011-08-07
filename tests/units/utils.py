import detest
from _detest import utils


@detest.test
def dotted_name():
    assert utils.dotted_name(utils.dotted_name) == '_detest.utils:dotted_name'
    assert utils.dotted_name(detest.test) == '_detest.suite:test'
    assert utils.dotted_name(len) == 'len'


@detest.test
def pluralize():
    assert utils.pluralize(0, 'thing') == 'things'
    assert utils.pluralize(0, 'thing', 'stuffs') == 'stuffs'
    assert utils.pluralize(1, 'thing') == 'thing'
    assert utils.pluralize(2, 'thing') == 'things'
