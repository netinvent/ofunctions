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

__intname__ = 'tests.ofunctions.string_handling'
__author__ = 'Orsiris de Jong'
__copyright__ = 'Copyright (C) 2020-2021 Orsiris de Jong'
__licence__ = 'BSD 3 Clause'
__build__ = '2021020901'

from ofunctions.string_handling import *


def test_string_handling():
    test_string = 'ABCDxyz1234&é"-è_çà)"ééà()\'"éài^^$¨IÎiï?./%X'
    assert convert_accents(test_string) == 'ABCDxyz1234&e"-e_ca)"eea()\'"eai^^$IIii?./%X', 'Strip accents failed'
    assert strip_special_characters(test_string) == 'ABCDxyz1234_iIi.X', 'Strip special chars failed'


if __name__ == '__main__':
    print('Example code for %s, %s' % (__intname__, __build__))
    test_string_handling()
