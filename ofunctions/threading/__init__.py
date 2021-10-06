#! /usr/bin/env python
#  -*- coding: utf-8 -*-
#
# This file is part of ofunctions package

"""
Function decorators for threading
Use with @threaded

Example:

@threaded
def somefunc(arg):
    return 'arg was %s' % arg


thread = somefunc('foo')
while thread.done() is False:
    time.sleep(1)

print(thread.result())


Versioning semantics:
    Major version: backward compatibility breaking changes
    Minor version: New functionality
    Patch version: Backwards compatible bug fixes

"""

__intname__ = "ofunctions.threading"
__author__ = "Orsiris de Jong"
__copyright__ = "Copyright (C) 2019-2021 Orsiris de Jong"
__description__ = "Threading decorator to run functions as threads"
__licence__ = "BSD 3 Clause"
__version__ = "0.1.0"
__build__ = "2019081101"


from threading import Thread
from concurrent.futures import Future
from functools import wraps


def call_with_future(fn, future, args, kwargs):
    """
    Threading a function with return info using Future
    from https://stackoverflow.com/a/19846691/2635443

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
        future = Future()
        Thread(target=call_with_future, args=(fn, future, args, kwargs)).start()
        return future

    return wrapper
