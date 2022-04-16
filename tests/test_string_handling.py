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


__intname__ = "tests.ofunctions.string_handling"
__author__ = "Orsiris de Jong"
__copyright__ = "Copyright (C) 2020-2022 Orsiris de Jong"
__licence__ = "BSD 3 Clause"
__build__ = "2022041601"

import sys
from ofunctions.string_handling import *


def test_string_handling():
    """
    Since we're dealing potentielly with python2, let's have unicode strings for comparaison
    """
    if sys.version_info[0] < 3:
        test_string = u'ABCDxyz1234&é"-è_çà)"ééà()\'"éài^^$¨IÎiï?./%X'
    else:
        test_string = 'ABCDxyz1234&é"-è_çà)"ééà()\'"éài^^$¨IÎiï?./%X'

    assert (
        convert_accents(test_string) == 'ABCDxyz1234&e"-e_ca)"eea()\'"eai^^$IIii?./%X'
    ), "Strip accents failed"
    assert (
        strip_special_characters(test_string) == "ABCDxyz1234_iIi.X"
    ), "Strip special chars failed"

    if sys.version_info[0] < 3:
        strip_characters_result = u'CDxyz1234&é"-è_çà)"ééà()\'"éài^^$¨IÎiï?./%'
    else:
        strip_characters_result = 'CDxyz1234&é"-è_çà)"ééà()\'"éài^^$¨IÎiï?./%'
    assert (
        strip_characters(test_string, r"[ABX]") == strip_characters_result
    ), "Should return test_string with A, B and X stripped"
    assert (
        strip_non_alnum_characters(test_string, keep_accents=False) == "ABCDxyz1234iIiX"
    )
    if sys.version_info[0] < 3:
        strip_non_alnum_characters_result = u"ABCDxyz1234éèçàééàéàiIÎiïX"
    else:
        strip_non_alnum_characters_result = "ABCDxyz1234éèçàééàéàiIÎiïX"

    assert (
        strip_non_alnum_characters(test_string, keep_accents=True)
        == strip_non_alnum_characters_result
    )


if __name__ == "__main__":
    print("Example code for %s, %s" % (__intname__, __build__))
    test_string_handling()
