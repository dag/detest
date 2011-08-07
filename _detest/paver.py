# encoding: utf-8
from __future__ import absolute_import, unicode_literals

from paver import easy as paver


paver.options.detest = paver.Bunch()


@paver.task
def auto():
    from . import config
    conf = config.Config()
    conf.load_local_configs()
    for section in conf.sections():
        paver.options.detest[section] = paver.Bunch(conf.items(section))


@paver.task
@paver.consume_args
def test():
    from . import environment
    env = environment.Environment()
    env.config.load_local_configs()
    for section, options in paver.options.detest.iteritems():
        for option, value in options.iteritems():
            env.config.set(section, option, value)
    env.create_argparser(prog='paver test')
    env.parse_arguments(paver.options.get('args', []))
    try:
        env.run()
    except SystemExit as e:
        if e.code != 0:
            raise
