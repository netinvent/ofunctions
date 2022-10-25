#! /usr/bin/env python
#  -*- coding: utf-8 -*-
#
# This file is part of ofunctions module

"""
Versioning semantics:
    Major version: backward compatibility breaking changes
    Minor version: New functionality
    Patch version: Backwards compatible bug fixes
"""

__intname__ = "tests.ofunctions.threading"
__author__ = "Orsiris de Jong"
__copyright__ = "Copyright (C) 2021-2022 Orsiris de Jong"
__licence__ = "BSD 3 Clause"
__build__ = "2022102501"


from re import M
import sys
import os
from time import sleep
from datetime import datetime
from unittest import result
from ofunctions.threading import *


FLOODER_RUNS = 0  # Required global variable so we keep compat with Python 2.7


def test_threading():
    # Nothing really insane to test here, we just can check wether we get handling back before sleeper_function is finished

    @threaded
    def sleeper_function():
        sleep(1)
        return "I slept"

    begin_time = datetime.utcnow()
    thread = sleeper_function()
    elapsed_time = (datetime.utcnow() - begin_time).total_seconds()
    print("It took {} seconds to run sleeper".format(elapsed_time))

    if sys.version_info[0] < 3:
        # Python 2.7 cannot use future, hence we won't get a result
        try:
            print(thread.result())
        except AttributeError:
            assert True, "We should get an AttributeError here"
        else:
            assert False, "We didn't get an AttributeError as awaited"
    else:
        result = thread.result()
        assert result == "I slept", "We should get a proper result"


def test_no_flood_without_arguments():
    # We will run function multiple times, but it should only be run once in less than 5 seconds

    global FLOODER_RUNS
    FLOODER_RUNS = 0

    @no_flood(5)
    def flooder_function():
        global FLOODER_RUNS
        FLOODER_RUNS += 1

    for _ in range(0, 5):
        flooder_function()

    assert FLOODER_RUNS == 1, "flooder_function should not have been run more than once"


def test_no_flood_with_arguments():
    # We will run function multiple times, but it should only be run once in less than 5 seconds with the same arguments
    # and run 5 times with different arguments
    print("Running antiflooding tests")

    global FLOODER_RUNS

    @no_flood(2, multiple_instances_diff_args=True)
    def flooder_function_with_diff_args(var=None, var2=None):
        global FLOODER_RUNS
        FLOODER_RUNS += 1

    @no_flood(2, multiple_instances_diff_args=False)
    def flooder_function_without_diff_args(var=None, var2=None):
        global FLOODER_RUNS
        FLOODER_RUNS += 1

    FLOODER_RUNS = 0
    for i in range(0, 5):
        flooder_function_with_diff_args(i)

    assert (
        FLOODER_RUNS == 5
    ), "flooder_function with different arguments should have been run 5 times, not being intercepted by @no_flood since we allow multuple instances with different arguments"

    FLOODER_RUNS = 0
    for i in range(0, 5):
        flooder_function_without_diff_args(i)

    assert (
        FLOODER_RUNS == 1
    ), "flooder_function without different args should not have been run more than once, being intercepted by @no_flood since we don't allow multiple instances even with different arguments"

    sleep(2)
    flooder_function_without_diff_args(i)
    assert (
        FLOODER_RUNS == 2
    ), "After 2 seconds timeout given to decorator, we should be able to execute function again without being intercepted by @no_flood"


if __name__ == "__main__":
    print("Example code for %s, %s" % (__intname__, __build__))
    test_threading()
    test_no_flood_without_arguments()
    test_no_flood_with_arguments()
