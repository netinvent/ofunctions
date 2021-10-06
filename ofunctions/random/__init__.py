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

__intname__ = "ofunctions.random"
__author__ = "Orsiris de Jong"
__copyright__ = "Copyright (C) 2014-2021 Orsiris de Jong"
__description__ = "Simple random string generator including password generator"
__licence__ = "BSD 3 Clause"
__version__ = "0.1.1"
__build__ = "2020102801"


import string
import random


def random_string(
    size: int = 8, chars: list = string.ascii_letters + string.digits
) -> str:
    """
    Simple password generator function
    """
    return "".join(random.choice(chars) for _ in range(size))


def pw_gen(size: int = 16, chars: list = string.ascii_letters + string.digits) -> str:
    return random_string(size, chars)
