from __future__ import division
import time

from detest import generator, test


@generator
def numbers(number):
    for x in range(10):
        yield number(x + 1)


@test
def accelerating(number):
    time.sleep(1 / number)
    assert number != 3


@test
def decelerating(number):
    time.sleep(number / 10)
    assert number != 7
