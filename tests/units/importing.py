import detest


@detest.test
def blocking_context():

    with detest.MustRaise(ImportError) as expectation:
        with detest.BlockingImporter('os'):
            from os import path

    assert unicode(expectation.exc_info[1])\
        == "blocking imports for 'os' in this context"

    # should not block after context
    from os import path

    # blocking should still work after successful import
    with detest.MustRaise(ImportError):
        with detest.BlockingImporter('os'):
            from os import path


@detest.test
def blocking_module(importerror, module):
    with detest.BlockingImporter(module):
        __import__(module)
