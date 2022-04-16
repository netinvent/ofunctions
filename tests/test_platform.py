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

__intname__ = "tests.ofunctions.platform"
__author__ = "Orsiris de Jong"
__copyright__ = "Copyright (C) 2020-2022 Orsiris de Jong"
__licence__ = "BSD 3 Clause"
__build__ = "2022041501"

from ofunctions.platform import *


def test_get_os():
    os = get_os()
    print(os)
    assert os in ["Windows", "Linux"], "Undefined OS"


def test_python_arch():
    arch = python_arch()
    print(arch)
    assert arch in ["x86", "x64"], "Undefined arch"


def test_is_64bit_python():
    is64 = is_64bit_python()
    print(is64)
    assert isinstance(is64, bool), "is_64bit_python() should return a bool"


if __name__ == "__main__":
    print("Example code for %s, %s" % (__intname__, __build__))
    test_get_os()
    test_python_arch()
    test_is_64bit_python()
