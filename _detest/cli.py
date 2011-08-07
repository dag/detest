# encoding: utf-8
from __future__ import unicode_literals

import functools
import io

from . import utils


def argument(*args, **kwargs):
    @utils.decorator
    def argument(scanner, name, ob):
        parser = scanner.env.argparser
        kwargs.setdefault('help', ob.__doc__)
        after = kwargs.pop('after', 'arguments-parsed')
        action = parser.add_argument(*args, **kwargs)
        scanner.env.argparser_signals[after].append((action.dest, ob))
    return argument


def switch(*args, **kwargs):
    def decorator(callback):
        @argument(*args, action='store_true', default=False, **kwargs)
        @functools.wraps(callback)
        def wrapper(env, value):
            if value:
                callback(env)
        return wrapper
    return decorator


@argument('-c', '--config', metavar='FILE')
def read_config(env, value):
    """read additional configuration from a file"""
    if value:
        env.config.read(value)


@argument('-o', '--set', metavar=('SECTION', 'OPTION', 'VALUE'),
          nargs=3, action='append')
def set_options(env, value):
    """set a configuration option"""
    if value:
        for triple in value:
            env.config.set(*triple)


@argument('--unset', metavar=('SECTION', 'OPTION'),
          nargs=2, action='append')
def unset_options(env, value):
    """remove an option from the configuration"""
    if value:
        for pair in value:
            env.config.remove_option(*pair)


@switch('-i', '--interactive')
def set_interactive(env):
    """enter the interactive interpreter in the context of the first
    failing test"""
    env.config.set('terminal', 'interactive', 'yes')


@switch('-d', '--debug')
def set_debug(env):
    """enter the debugger in the context of the first failing test"""
    env.config.set('terminal', 'debug', 'yes')


@switch('-f', '--fail-fast')
def set_fail_fast(env):
    """abort remaining tests on the first failure"""
    env.config.set('terminal', 'fail-fast', 'yes')


@argument('module', nargs='*')
def configsuite_modules(env, value):
    """instruct configsuite to scan these modules under the configured
    tests package"""
    if value:
        env.config.set('suite', 'modules', ' '.join(value))


@switch('--dump-config', after='configured')
def dump_config(env):
    """print the internal configuration state as a configuration file"""
    stream = io.BytesIO()
    env.config.write(stream)
    env.write_pygmented('ini', stream.getvalue())
    env.argparser.exit()


@switch('--shell', after='configured')
def shell(env):
    """enter the interactive interpreter for this environment without
    running tests"""
    env.interact(dict(env=env))
    env.argparser.exit()
