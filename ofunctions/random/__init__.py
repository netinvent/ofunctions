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
__copyright__ = "Copyright (C) 2014-2024 Orsiris de Jong"
__description__ = "Simple random string generator including password generator"
__licence__ = "BSD 3 Clause"
__version__ = "0.4.0"
__build__ = "2024090701"
__compat__ = "python2.7+"


import string
import random
from ofunctions.string_handling import accent_chars, ambiguous_chars


def random_string(size=8, chars=string.ascii_letters + string.digits):
    # type: (int, list) -> str
    """
    Simple password generator function
    """
    return "".join(random.choice(chars) for _ in range(size))


def pw_gen(size=16, chars=string.ascii_letters + string.digits):
    """
    Shorthand for random_string
    """
    # type: (int, list) -> str
    return random_string(size, chars)


def password_gen(
    size=16,
    alpha=True,
    numeric=True,
    special_chars=True,
    no_accents=True,
    ambiguous_filter=True,
):
    """
    Basic password generator
    """
    chars = ""
    if alpha:
        chars += string.ascii_letters
        if not no_accents:
            chars += "".join(accent_chars)
    chars += string.digits if numeric else ""
    chars += string.punctuation if special_chars else ""

    if ambiguous_filter:
        """
        Remove Linux / Windows specific chars from possible char list
        Remove ambiguous letters like 'O' (leave 0)
        """
        for char in ambiguous_chars:
            chars = chars.replace(char, "")

    return pw_gen(size, chars)
