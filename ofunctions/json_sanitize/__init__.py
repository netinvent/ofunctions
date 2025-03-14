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

__intname__ = "ofunctions.json_sanitize"
__author__ = "Orsiris de Jong"
__copyright__ = "Copyright (C) 2020-2024 Orsiris de Jong"
__description__ = "Simple tool that filters unwanted characters including non printable from JSON objects"
__licence__ = "BSD 3 Clause"
__version__ = "0.2.0"
__build__ = "2024102401"
__compat__ = "python2.7+"


import re

# python 2.7 compat fixes
try:
    from typing import Union
except ImportError:
    pass


def json_sanitize(value, is_value=True):
    # type: (Union[str, dict, dict], bool) -> Union[str, dict, list]
    """
    Modified version of https://stackoverflow.com/a/45526935/2635443

    Recursive function that allows to remove any special characters from json,
    especially unknown control characters

    Names may contain whatever but dots
    Values are sanitized in order to not contain any control characters
    Extended sanitization will also remove any BOM
    """
    name_sanitize_re = re.compile(r"[.\x00-\x1f\x7f-\x9f]")
    value_sanitize_re = re.compile(r"[\x00-\x1f\x7f-\x9f]")

    if isinstance(value, dict):
        value = {
            json_sanitize(k, False): json_sanitize(v, True) for k, v in value.items()
        }
    elif isinstance(value, list):
        value = [json_sanitize(v, True) for v in value]
    elif isinstance(value, str):
        if not is_value:
            # Remove dots from value names
            value = re.sub(name_sanitize_re, "", value)
        else:
            # Windows eventID messages may have newlines / other special chars in them
            # We remove anything that's not printable character (this includes all control characters, BOM, etc)
            value = re.sub(value_sanitize_re, " ", value)
    return value
