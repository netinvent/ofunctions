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


__intname__ = 'tests.ofunctions.string_handling'
__author__ = 'Orsiris de Jong'
__copyright__ = 'Copyright (C) 2020-2021 Orsiris de Jong'
__licence__ = 'BSD 3 Clause'
__build__ = '2021032901'

from ofunctions.string_handling import *


def test_string_handling():
    test_string = 'ABCDxyz1234&é"-è_çà)"ééà()\'"éài^^$¨IÎiï?./%X'
    assert convert_accents(test_string) == 'ABCDxyz1234&e"-e_ca)"eea()\'"eai^^$IIii?./%X', 'Strip accents failed'
    assert strip_special_characters(test_string) == 'ABCDxyz1234_iIi.X', 'Strip special chars failed'
    assert strip_characters(test_string, r'[ABX]') == 'CDxyz1234&é"-è_çà)"ééà()\'"éài^^$¨IÎiï?./%',\
        'Should return test_string with A, B and X stripped'
    assert strip_non_alnum_characters(test_string, include_accents=False) == 'ABCDxyz1234iIiX'
    assert strip_non_alnum_characters(test_string, include_accents=True) == 'ABCDxyz1234éè_çàééàéàiIÎiïX'

if __name__ == '__main__':
    print('Example code for %s, %s' % (__intname__, __build__))
    test_string_handling()
