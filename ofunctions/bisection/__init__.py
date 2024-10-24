#! /usr/bin/env python
#  -*- coding: utf-8 -*-
#
# This file is part of ofunctions package

"""
Bisection tool takes a function and and argument list for that function, and will proceed to find
which is the last argument that produces a 'True' result for the given function
The argument list should be ordered (ie no random results), ex of expected results [True, True, True, False, False]

Versioning semantics:
    Major version: backward compatibility breaking changes
    Minor version: New functionality
    Patch version: Backwards compatible bug fixes

"""

__intname__ = "ofunctions.bisection"
__author__ = "Orsiris de Jong"
__copyright__ = "Copyright (C) 2020-2024 Orsiris de Jong"
__description__ = "Bisection that allows callables to be tested with arguments"
__licence__ = "BSD 3 Clause"
__version__ = "1.0.0"
__build__ = "2022041401"
__compat__ = "python2.7+"


# python 2.7 compat fixes
try:
    from typing import Callable, Any, Iterable
except ImportError:
    pass


def bisect(
    func,
    args_list,
    expected_result=True,
    allow_all_expected=False,
):
    # type: (Callable, Iterable, Any, bool) -> Any
    """
    Finds which is the last argument in list that made func return the expected_result (True/False/Whatever)

    func args can be a single argument, or a tuple of arguments
    Argument list must be ordered from left to right or right to left (no random results)

    allow_all_expected: shall we allow only expected results from all arguments ? (non strict bisection)
                        If so, we'll consider arguments are ordered left to right
    See the examples in _selftest function
    """

    # First, let's fix the argument list when people pass direct iterable list of one argument
    # in order to call function with expansion, eg fn(*arg_list)
    fixed_args = None
    try:
        if len(args_list[0]) < 2:
            fixed_args = [(arg,) for arg in args_list]
            args_list = fixed_args
    # TypeError will happen if a list of int is given
    except TypeError:
        fixed_args = [(arg,) for arg in args_list]
        args_list = fixed_args

    index_left = 0
    index_right = len(args_list) - 1
    left_result = func(*args_list[index_left])
    right_result = func(*args_list[index_right])

    if left_result == expected_result and right_result == expected_result:
        if not allow_all_expected:
            raise ValueError("Both sides of the argument list produced expected results")
        # if all valid results are allowed, we'll consider that any ordering is ascending, hence return right index
        # This is allowed in order to use bisection for min=x, max=y schemas where result could be max
        if fixed_args is None:
            return args_list[index_right]
        return args_list[index_right][0]
    elif left_result != expected_result and right_result != expected_result:
        raise ValueError("Both sides of the argument list produced unexpected results")
    elif left_result == expected_result and right_result != expected_result:
        # The argument list is supposed to provide the expected result left, and not expected result right
        left_to_right_ordered = True
        index_last_expected_result = index_left
    elif left_result != expected_result and right_result == expected_result:
        left_to_right_ordered = False
        index_last_expected_result = index_right
    else:
        raise ValueError(
            "Argument list extremities give results different than expected results."
            " Most left result = {}, Most right result = {}".format(
                left_result, right_result
            )
        )

    # count = 0
    while index_left < index_right:
        index_middle = int((index_left + index_right) / 2)
        result = func(*args_list[index_middle])
        if result == expected_result:
            index_last_expected_result = index_middle
        if (result == expected_result and left_to_right_ordered) or (
            result != expected_result and not left_to_right_ordered
        ):
            if index_middle > index_left:
                index_left = index_middle
            else:
                index_left = index_middle + 1
        if (result == expected_result and not left_to_right_ordered) or (
            result != expected_result and left_to_right_ordered
        ):
            if index_middle < index_right:
                index_right = index_middle
            else:
                index_right = index_middle - 1

        # count += 1
    # print('Resolved in {} counts, result = {}'.format(count, args_list[index_last_expected_result]))
    if index_last_expected_result is not None:
        if fixed_args is None:
            return args_list[index_last_expected_result]
        return args_list[index_last_expected_result][0]
    return None
