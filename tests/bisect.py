#! /usr/bin/env python
#  -*- coding: utf-8 -*-
#
# This file is part of command_runner module

"""
command_runner is a quick tool to launch commands from Python, get exit code
and output, and handle most errors that may happen

Versioning semantics:
    Major version: backward compatibility breaking changes
    Minor version: New functionality
    Patch version: Backwards compatible bug fixes

"""

__intname__ = 'tests.ofunctions.bisect'
__author__ = 'Orsiris de Jong'
__copyright__ = 'Copyright (C) 2020-2021 Orsiris de Jong'
__licence__ = 'BSD 3 Clause'
__build__ = '2021020901'

from ofunctions.bisect import *

def test_bisect():
    # Define two test functions
    def test_func(i: int):

        return i >= 1386

    def test_func_multi_arg(i, some_arg=None):
        if some_arg is None:
            assert False, 'test_func_multi_arg argument x is None'
        return i >= 1386

    result = bisect(test_func, args_list=range(0, 1600))
    print('Bisect result = %s' % result)
    assert result == 1386, 'bisect left to right failed'

    result = bisect(test_func, range(1600, 0, -1))
    print('Bisect result = %s' % result)
    assert result == 1386, 'bisect right to left failed'

    result = bisect(test_func, [1, 5, 1300, 1600, 1800, 1900])
    print('Bisect result = %s' % result)
    assert result == 1600, 'bisect left to right failed'

    result = bisect(test_func, [1900, 1800, 1600, 1300, 5, 1])
    print('Bisect result = %s' % result)
    assert result == 1600, 'bisect right to left failed'

    result = bisect(test_func, [1, 1400, 1700])
    print('Bisect result = %s' % result)
    assert result == 1400, 'bisect left to right for 3 args failed'

    result = bisect(test_func, [1, 1300, 1700])
    print('Bisect result = %s' % result)
    assert result == 1700, 'bisect left to right for 3 args failed'

    result = bisect(test_func, [1900, 1776, 30])
    print('Bisect result = %s' % result)
    assert result == 1776, 'bisect right to left for 3 args failed'

    result = bisect(test_func, [1900, 1200, 30])
    print('Bisect result = %s' % result)
    assert result == 1900, 'bisect right to left for 3 args failed'

    result = bisect(test_func, [1, 1500])
    print('Bisect result = %s' % result)
    assert result == 1500, 'bisect left to right wfor 2 args failed'

    result = bisect(test_func, [1500, 1000])
    print('Bisect result = %s' % result)
    assert result == 1500, 'bisect right to left for 2 args failed'

    try:
        result = bisect(test_func, [1, 1000])
        print('Bisect result = %s' % result)
    except ValueError:
        pass
    else:
        assert False, 'bisect left to right without result should produce a ValueError'

    try:
        result = bisect(test_func, [1000, 100])
        print('Bisect result = %s' % result)
    except ValueError:
        pass
    else:
        assert False, 'bisect right to left without result should produce a ValueError'

    try:
        result = bisect(test_func, [6000, 9000], allow_all_expected=False)
        print('Bisect result = %s' % result)
    except ValueError:
        pass
    else:
        assert False, 'Bisect only valid results with allow_all_expected=False should produce errors'

    result = bisect(test_func, range(100, 1500, 100))
    print('Bisect result = %s' % result)
    assert result == 1400, 'bisect left to right for even number of args'

    result = bisect(test_func, range(1500, 100, -100))
    print('Bisect result = %s' % result)
    assert result == 1400, 'bisect right to left for even number of args'

    result = bisect(test_func, range(100, 1600, 100))
    print('Bisect result = %s' % result)
    assert result == 1400, 'bisect left to right for odd number of args'

    result = bisect(test_func, range(1400, 1000, -100))
    print('Bisect result = %s' % result)
    assert result == 1400, 'bisect right to left for odd number of args'

    try:
        result = bisect(test_func, [1])
        print('Bisect result = %s' % result)
    except ValueError:
        pass
    else:
        assert result is None, 'bisect with one argument should produce a ValueError'

    # Bisect tests for multiple arguments
    result = bisect(test_func_multi_arg, args_list=[(1, 'arg2'), (1500, 'arg2'), (1800, 'arg3')])
    print('Bisect result = {}'.format(result))
    assert result[0] == 1500, 'bisect for multiple arguments failed'

    result = bisect(test_func_multi_arg, args_list=[(x, 'somearg') for x in range(0, 10000)])
    print('Bisect result = {}'.format(result))
    assert result[0] == 1386, 'bisect for multiple arguments failed'

    args = [(x, y) for x, y in zip(range(0, 10000), range(10000, 0, -1))]
    result = bisect(test_func_multi_arg, args_list=args)
    print('Bisect result = {}'.format(result))
    assert result[0] == 1386, 'bisect for multiple arguments failed'

    result = bisect(test_func, range(0, 5000), expected_result=False)
    print('Bisect result = {}'.format(result))
    assert result == 1385, 'bisect last false result left to right failed'

    result = bisect(test_func, range(5000, 0, -1), expected_result=False)
    print('Bisect result = {}'.format(result))
    assert result == 1385, 'bisect last false result right to left failed'

    # Special case when all arguments will be expected results
    result = bisect(test_func, [1386, 1387, 1388], allow_all_expected=True)
    print('Bisect result = {}'.format(result))
    assert result == 1388, 'bisect with only valid results should return most right result'


if __name__ == '__main__':
    print('Example code for %s, %s' % (__intname__, __build__))
    test_bisect()
