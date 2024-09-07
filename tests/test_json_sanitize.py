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

__intname__ = "tests.ofunctions.json_sanitize"
__author__ = "Orsiris de Jong"
__copyright__ = "Copyright (C) 2020-2024 Orsiris de Jong"
__licence__ = "BSD 3 Clause"
__build__ = "2021020901"


from ofunctions.json_sanitize import *


def test_json_sanitize():
    test_json = {"some.var": "some\nvalue\0without\x00special\tchars"}
    sanitized = json_sanitize(test_json)
    print("Sanitized json: %s" % sanitized)
    for key, value in sanitized.items():
        assert "." not in key, "JSON key should not contain dots"
        assert "\n" not in value, "JSON value should not contain control chars"


if __name__ == "__main__":
    print("Example code for %s, %s" % (__intname__, __build__))
    test_json_sanitize()
