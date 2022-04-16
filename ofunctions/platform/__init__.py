#! /usr/bin/env python
#  -*- coding: utf-8 -*-
#
# This file is part of ofunctions package

"""
ofunctions is a general library for basic repetitive tasks that should be no brainers :)

Versioning semantics:
    Major version: backward compatibility breaking changes
    Minor version: New functionality
    Patch version: Backwards compatible bug fixes

"""

__intname__ = "ofunctions.platform"
__author__ = "Orsiris de Jong"
__copyright__ = "Copyright (C) 2014-2022 Orsiris de Jong"
__description__ = "Very basic platform identification"
__licence__ = "BSD 3 Clause"
__version__ = "1.1.1"
__build__ = "2022041601"
__compat__ = "python2.7+"

import os
import sys


def get_os():
    # type: (None) -> str
    """
    Simple windows / linux identification that handles msys too
    """
    if os.name == "nt":
        return "Windows"
    if os.name == "posix":
        # uname property does not exist under windows
        # pylint: disable=E1101
        result = os.uname()[0]

        if result.startswith("MSYS_NT-"):
            result = "Windows"

        return result
    raise OSError("Cannot get os, os.name=[%s]." % os.name)


def python_arch():
    # type: (None) -> str
    """
    Get current python interpreter architecture
    """
    if get_os() == "Windows":
        if "AMD64" in sys.version:
            return "x64"
        return "x86"

    # uname property does not exist under windows
    # pylint: disable=E1101
    arch = os.uname()[4]
    if 'x64' in arch.lower():
        return "x64"
    return "x86"


def is_64bit_python():
    # type: (None) -> bool
    """
    Detect if python is 64 bit but stay OS agnostic
    """
    return sys.maxsize > 2**32
