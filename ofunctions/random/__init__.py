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
__copyright__ = "Copyright (C) 2014-2022 Orsiris de Jong"
__description__ = "Simple random string generator including password generator"
__licence__ = "BSD 3 Clause"
__version__ = "0.2.0"
__build__ = "2022041401"
__compat__ = "python2.7+"


import string
import random


def random_string(size=8, chars=string.ascii_letters + string.digits):
    # type: (int, list) -> str
    """
    Simple password generator function
    """
    return "".join(random.choice(chars) for _ in range(size))


def pw_gen(size=16, chars=string.ascii_letters + string.digits):
    # type: (int, list) -> str
    return random_string(size, chars)
