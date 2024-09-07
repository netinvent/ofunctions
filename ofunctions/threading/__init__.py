#! /usr/bin/env python
#  -*- coding: utf-8 -*-
#
# This file is part of ofunctions package

"""
Function decorators for threading and antiflooding
Use with @threaded

Versioning semantics:
    Major version: backward compatibility breaking changes
    Minor version: New functionality
    Patch version: Backwards compatible bug fixes

"""

__intname__ = "ofunctions.threading"
__author__ = "Orsiris de Jong"
__copyright__ = "Copyright (C) 2019-2024 Orsiris de Jong"
__description__ = (
    "Threading decorator to run functions as threads, antiflood decorator too"
)
__licence__ = "BSD 3 Clause"
__version__ = "2.3.0"
__build__ = "2024010801"
__compat__ = "python2.7+"


# python 2.7 compat fixes
try:
    from typing import Optional
except ImportError:
    pass
import sys
import threading
from datetime import datetime
from time import sleep


# python 2.7 comapt fixes
try:
    from typing import Union, List, Any
except ImportError:
    pass

# Python 2.7 compat fixes
try:
    from concurrent.futures import Future
except ImportError:
    pass
from functools import wraps


# python 2.7 compat where we will use @threaded
if sys.version_info[0] < 3:

    def threaded(fn):
        """
        Threaded allows to make any funtion a thread
        With python 2.7, there will be no possible return value
        """

        @wraps(fn)
        def wrapper(*args, **kwargs):
            if kwargs.pop("__no_threads", False):
                return fn(*args, **kwargs)
            thread = threading.Thread(target=fn, args=args, kwargs=kwargs)
            thread.daemon = True
            thread.start()
            return thread

        return wrapper

else:

    def call_with_future(fn, future, args, kwargs):
        """
        Threading a function with return info using Future
        from https://stackoverflow.com/a/19846691/2635443

        Example:

        @threaded
        def somefunc(arg):
            return 'arg was %s' % arg


        thread = somefunc('foo')
        while thread.done() is False:
            time.sleep(1)

        print(thread.result())
        """
        try:
            result = fn(*args, **kwargs)
            future.set_result(result)
        except Exception as exc:
            future.set_exception(exc)

    def threaded(fn):
        """
        @threaded wrapper in order to thread any function

        @wraps decorator sole purpose is for function.__name__ to be the real function
        instead of 'wrapper'

        """

        @wraps(fn)
        def wrapper(*args, **kwargs):
            if kwargs.pop("__no_threads", False):
                return fn(*args, **kwargs)
            future = Future()
            thread = threading.Thread(
                target=call_with_future, args=(fn, future, args, kwargs)
            )
            thread.daemon = True
            thread.start()
            return future

        return wrapper


def wait_for_threaded_result(threads, timeout=None):
    #  type: (Union[List[Future], Future], Optional[Union[int, float]]) -> Any
    """
    Simple shorthand to wait for a thread to finish
    Accepts a single thread, or a list of threads
    Returns thread result or result list

    if timeout reached, result list will contain results of done threads and None for unfinished ones

    If a non threaded function or function list is given, we'll just give back results or result lists
    """
    source_is_list = True
    if not isinstance(threads, list):
        threads = [threads]
        source_is_list = False

    threads_alive = True
    timeout_reached = False
    start_time = datetime.utcnow()
    while threads_alive:
        threads_alive = False
        if timeout and (datetime.utcnow() - start_time).total_seconds() > timeout:
            timeout_reached = True
        for thread in threads:
            if hasattr(thread, "done") and hasattr(thread, "cancelled"):
                if not thread.done() and not thread.cancelled():
                    threads_alive = True
                else:
                    if timeout_reached:
                        thread.cancel()
        if timeout_reached:
            break

    # If threaded, return results or list of results
    result_list = []
    for thread in threads:
        if hasattr(thread, "done"):
            if thread.done():
                result_list.append(thread.result())
            else:
                result_list.append(None)
        else:
            result_list.append(thread)
    if not source_is_list:
        return result_list[0]
    return result_list


def no_flood(flood_timespan=5, multiple_instances_diff_args=True):
    """
    This decorator is an antiflood system for a given function
    It prevents running the same function more than once in a given timeframe (flood_timespan seconds)

    Usage:

    Don't run my_funtion more than once in 5 seconds if called multiple times with the same arguments

    @no_flood(5)
    my_function()

    Don't run my_function more than once in 10 seconds, regarless of it's arguments
    @no_flood(10, False)
    my_function()

    Can also be combined with a threaded decorator
    @threaded
    @no_flood(3)
    my_function()

    """

    def decorator(fn):
        def wrapper(*args, **kwargs):
            # We need to create a global variable if it doesn't exist so we can keep track of executions outside of this decorator
            global __NO_FLOOD_TIMEOUT
            try:
                # pylint: disable=E0601 (used-before-assignment)
                __NO_FLOOD_TIMEOUT
            except:
                __NO_FLOOD_TIMEOUT = {}

            if multiple_instances_diff_args:
                fn_identificator = "{}-args.{}-kwargs.{}".format(
                    fn.__name__, args, kwargs
                )
            else:
                fn_identificator = fn.__name__

            if fn_identificator in __NO_FLOOD_TIMEOUT:
                if (
                    datetime.utcnow() - __NO_FLOOD_TIMEOUT[fn_identificator]
                ).total_seconds() < flood_timespan:
                    return

            # Add new execution timestamp
            __NO_FLOOD_TIMEOUT[fn_identificator] = datetime.utcnow()
            return fn(*args, **kwargs)

        return wrapper

    return decorator
