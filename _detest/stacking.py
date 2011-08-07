# encoding: utf-8
from __future__ import unicode_literals

import contextlib


class Stack(object):

    def __init__(self):
        self.stack = []

    @contextlib.contextmanager
    def bind(self, obj):
        self.stack.append(obj)
        try:
            yield obj
        finally:
            self.stack.pop()

    @property
    def current(self):
        if self.stack:
            return self.stack[-1]
