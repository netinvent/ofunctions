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
__copyright__ = "Copyright (C) 2019-2022 Orsiris de Jong"
__description__ = "Threading decorator to run functions as threads"
__licence__ = "BSD 3 Clause"
__version__ = "1.0.1"
__build__ = "2022071001"
__compat__ = "python2.7+"


import sys
import threading

# Python 2.7 compat fixes
try:
    from concurrent.futures import Future
except ImportError:
    pass
from functools import wraps


# python 2.7 compat where we will use @threaded
if sys.version_info[0] < 3:

    def threaded(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
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
            thread = threading.Thread(
                target=call_with_future, args=(fn, future, args, kwargs)
            )
            thread.daemon = True
            thread.start()
            return future

        return wrapper
