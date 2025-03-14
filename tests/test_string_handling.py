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

# python 2.7 compat fixes so all strings are considered unicode
from __future__ import unicode_literals

__intname__ = "tests.ofunctions.string_handling"
__author__ = "Orsiris de Jong"
__copyright__ = "Copyright (C) 2020-2024 Orsiris de Jong"
__licence__ = "BSD 3 Clause"
__build__ = "2022041603"


import sys
import os
from ofunctions.string_handling import *


def running_on_github_actions():
    """
    This is set in github actions workflow with
          env:
        RUNNING_ON_GITHUB_ACTIONS: true
    """
    return os.environ.get("RUNNING_ON_GITHUB_ACTIONS") == "true"  # bash 'true'


def test_string_handling():
    """
    Since we're dealing potentially with python2, let's have unicode strings for comparison
    """
    test_string = 'ABCDxyz1234&é"-è_çà)"ééà()\'"éài^^$¨IÎiï?./%X'

    assert (
        convert_accents(test_string) == 'ABCDxyz1234&e"-e_ca)"eea()\'"eai^^$IIii?./%X'
    ), "Strip accents failed"
    assert (
        strip_special_characters(test_string) == "ABCDxyz1234_iIi.X"
    ), "Strip special chars failed"

    strip_characters_result = 'CDxyz1234&é"-è_çà)"ééà()\'"éài^^$¨IÎiï?./%'
    assert (
        strip_characters(test_string, r"[ABX]") == strip_characters_result
    ), "Should return test_string with A, B and X stripped"
    assert (
        strip_non_alnum_characters(test_string, keep_accents=False) == "ABCDxyz1234iIiX"
    )

    # Python 2 unicode hell on github is worse, just don't worth my time, sorry
    if not running_on_github_actions():
        strip_non_alnum_characters_result = "ABCDxyz1234éèçàééàéàiIÎiïX"
        assert (
            strip_non_alnum_characters(test_string, keep_accents=True)
            == strip_non_alnum_characters_result
        )


if __name__ == "__main__":
    print("Example code for %s, %s" % (__intname__, __build__))
    test_string_handling()
