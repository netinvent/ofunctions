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
__copyright__ = "Copyright (C) 2021-2024 Orsiris de Jong"
__licence__ = "BSD 3 Clause"
__build__ = "2024010901"


from re import M
import sys
import os
from time import sleep
from datetime import datetime
from unittest import result
from ofunctions.threading import *


FLOODER_RUNS = 0  # Required global variable so we keep compat with Python 2.7


@threaded
def threaded_sleeper_fn(seconds):
    sleep(seconds)
    return "I slept for {} seconds".format(seconds)

def non_threaded_sleeper_fn(seconds):
    sleep(seconds)
    return "I slept for {} seconds".format(seconds)


def test_threading():
    # Nothing really insane to test here, we just can check wether we get handling back before sleeper_function is finished
    # thread.result() will wait join the thread if not finished

    begin_time = datetime.now()
    thread = threaded_sleeper_fn(2)
    elapsed_time = (datetime.now() - begin_time).total_seconds()
    print("It took {} seconds to run sleeper".format(elapsed_time))

    assert elapsed_time < 1, "We should get handed back control before a second passes"

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
        assert result == "I slept for 2 seconds", "We should get a proper result"


def test_wait_for_threaded_result():
    begin_time = datetime.now()
    thread = threaded_sleeper_fn(2)
    elapsed_time = (datetime.now() - begin_time).total_seconds()
    assert elapsed_time < 1, "We should get handed back control before a second passes"    
    result = wait_for_threaded_result(thread)
    elapsed_time = (datetime.now() - begin_time).total_seconds()
    print("ELAPSED TIME", elapsed_time)
    assert elapsed_time > 2, "At least 2 seconds should have passed since we got our result back"
    print("RESULT:", result)
    assert result == "I slept for 2 seconds", "Bogus result"


def test_wait_for_threaded_result_timeout():
    begin_time = datetime.now()
    thread = threaded_sleeper_fn(5)
    elapsed_time = (datetime.now() - begin_time).total_seconds()
    assert elapsed_time < 1, "We should get handed back control before a second passes"    
    result = wait_for_threaded_result(thread, timeout=2)
    elapsed_time = (datetime.now() - begin_time).total_seconds()
    print("ELAPSED TIME", elapsed_time)
    assert elapsed_time < 3, "Timeout should have kicked in"
    print("RESULT:", result)
    assert result is None, "Bogus result"

    
def test_wait_for_threaded_result_no_thread():
    begin_time = datetime.now()
    thread = non_threaded_sleeper_fn(2)
    elapsed_time = (datetime.now() - begin_time).total_seconds()
    assert elapsed_time > 2, "At least 2 seconds should have passed since we got our result back"    
    result = wait_for_threaded_result(thread)
    print("RESULT:", result)
    assert result == "I slept for 2 seconds", "Bogus result"

def test_wait_for_threaded_result_list():
    begin_time = datetime.now()
    thread_list = []
    for _ in range(0, 4):
        thread_list.append(threaded_sleeper_fn(2))
    elapsed_time = (datetime.now() - begin_time).total_seconds()
    assert elapsed_time < 1, "We should get handed back control before a second passes"    
    result = wait_for_threaded_result(thread_list)
    elapsed_time = (datetime.now() - begin_time).total_seconds()
    print("ELAPSED TIME", elapsed_time)
    assert elapsed_time > 2, "At least 2 seconds should have passed since we got our result back"
    for i in range(0, 4):
        print("RESULT:", i, result[i])
        assert result[i] == "I slept for 2 seconds", "Bogus list result"

def test_wait_for_threaded_result_list_timeout():
    begin_time = datetime.now()
    thread_list = []
    for i in range(2, 6):
        thread_list.append(threaded_sleeper_fn(i))
    elapsed_time = (datetime.now() - begin_time).total_seconds()
    assert elapsed_time < 1, "We should get handed back control before a second passes"    
    result = wait_for_threaded_result(thread_list, timeout=3.5)
    elapsed_time = (datetime.now() - begin_time).total_seconds()
    print("ELAPSED TIME", elapsed_time)
    assert elapsed_time < 4, "timeout should have kicked in after 3 seconds"
    print("RESULT:", result)
    assert isinstance(result, list), "Result should be a dict"
    assert result[0] == "I slept for 2 seconds", "1st result bogus"
    assert result[1] == "I slept for 3 seconds", "2nd result bogus"
    assert result[2] == None, "3rd result bogus"
    assert result[3] == None, "4th result bogus"

    
def test_wait_for_threaded_result_no_thread_list():
    begin_time = datetime.now()
    thread_list = []
    for _ in range(0, 4):
        thread_list.append(non_threaded_sleeper_fn(2))
    elapsed_time = (datetime.now() - begin_time).total_seconds()
    assert elapsed_time > 8, "At least 8 seconds should have passed since we got our result back"    
    result = wait_for_threaded_result(thread_list)
    assert isinstance(result, list), "Result should be a list"
    for i in range(0, 4):
        print("RESULT:", i, result[i])
        assert result[i] == "I slept for 2 seconds", "Bogus list result"
  

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
    test_wait_for_threaded_result()
    test_wait_for_threaded_result_timeout()
    test_wait_for_threaded_result_no_thread()
    test_wait_for_threaded_result_list()
    test_wait_for_threaded_result_list_timeout()
    test_wait_for_threaded_result_no_thread_list()
    test_no_flood_without_arguments()
    test_no_flood_with_arguments()
