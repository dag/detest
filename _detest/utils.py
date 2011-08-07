# encoding: utf-8
from __future__ import unicode_literals

import functools
import venusian


def dotted_name(object):
    if object.__module__ in ('__main__', '__builtin__'):
        return object.__name__
    return ':'.join([object.__module__, object.__name__])


def decorator(callback):
    @functools.wraps(callback)
    def wrapper(target):
        venusian.attach(target, callback, callback.__name__)
        return target
    return wrapper


def pluralize(quantity, singular, plural=None):
    if quantity == 1:
        return singular
    if plural is None:
        return singular + 's'
    return plural
