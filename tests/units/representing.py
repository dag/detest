import detest


@detest.test
def trees(tree):
    assert detest.TreeRepr().repr(tree.data) == tree.repr
