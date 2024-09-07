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


__intname__ = "tests.ofunctions.random"
__author__ = "Orsiris de Jong"
__copyright__ = "Copyright (C) 2020-2021 Orsiris de Jong"
__licence__ = "BSD 3 Clause"
__build__ = "2021020901"

from ofunctions.string_handling import accent_chars, ambiguous_chars
from ofunctions.random import *


def test_pw_gen():
    password = pw_gen(20)
    print("Generated password: %s" % password)
    assert len(password) == 20, "Password should be 20 char long"
    for char in password:
        assert (
            char in string.ascii_letters or char in string.digits
        ), "Password is not compliant"


def test_password_gen():
    """
    Since we're doing randum stuff, we need 
    to run the test multiple times to lower error probability
    """
    for i in range(50):
        password = password_gen(20, alpha=True, numeric=True, special_chars=True, no_accents=True, ambiguous_filter=True)
        print("Generated password: %s" % password)
        assert len(password) == 20, "Password should be 20 char long"
        for char in password:
            assert (
                char not in accent_chars and \
                char not in ambiguous_chars  
            ), "Password is not compliant"



if __name__ == "__main__":
    print("Example code for %s, %s" % (__intname__, __build__))
    test_pw_gen()
    test_password_gen()
