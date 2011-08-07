import sys
sys.path.insert(0, '')

from detest.paver import auto, test
from paver import easy as paver
from paved import paved


@paver.task
def cover():
    import coverage
    import pkgutil

    cover = coverage.coverage()
    cover.start()

    # count import-time code as covered
    for importer, name, ispkg in pkgutil.iter_modules(['_detest']):
        __import__('_detest', fromlist=[name])

    # _detest.config is loaded by the auto task, reload to count it
    from _detest import config
    reload(config)

    cover.stop()

    import detest
    env = detest.Environment()
    env.coverage = cover
    env.config.load_local_configs()
    with detest.ExceptionCapture(SystemExit):
        env.run()

    print
    paver.sh('coverage report')
    paver.sh('coverage html')


@paver.task
def dump():
    import detest
    print detest.TreeRepr().repr(paver.options._SimpleProxy__get_object())
