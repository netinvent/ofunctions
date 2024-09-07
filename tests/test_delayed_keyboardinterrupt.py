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

__intname__ = "tests.ofunctions.delayed_keyboardinterrupt"
__author__ = "Orsiris de Jong"
__copyright__ = "Copyright (C) 2020-2024 Orsiris de Jong"
__licence__ = "BSD 3 Clause"
__build__ = "2022150401"


from time import sleep
from ofunctions.delayed_keyboardinterrupt import *


# TODO: How to write an automatic CTRL+C test without doing a lot of threading stuff ???
def test_delayed_keyboard_interrupt():
    with DelayedKeyboardInterrupt():
        print(
            "This is a manual test where you shouldn't be able to use CTRL+C for 2 seconds"
        )
        sleep(2)
        print("done")


if __name__ == "__main__":
    print("Example code for %s, %s" % (__intname__, __build__))
    test_delayed_keyboard_interrupt()
