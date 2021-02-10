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

__intname__ = 'ofunctions.json_sanitize'
__author__ = 'Orsiris de Jong'
__copyright__ = 'Copyright (C) 2020-2021 Orsiris de Jong'
__licence__ = 'BSD 3 Clause'
__version__ = '0.1.1'
__build__ = '2020102801'

import re
from typing import Union


def json_sanitize(value: Union[str, dict, list], is_value=True) -> Union[str, dict, list]:
    """
    Modified version of https://stackoverflow.com/a/45526935/2635443

    Recursive function that allows to remove any special characters from json,
    especially unknown control characters
    """
    if isinstance(value, dict):
        value = {json_sanitize(k, False): json_sanitize(v, True) for k, v in value.items()}
    elif isinstance(value, list):
        value = [json_sanitize(v, True) for v in value]
    elif isinstance(value, str):
        if not is_value:
            # Remove dots from value names
            value = re.sub(r"[.]", "", value)
        else:
            # Convert windows newlines to unix ones, and escape them double
            # eventID messages may have newlines / other special chars in them
            # value = re.sub(r"\r\n", "\\\\n", value)
            # value = re.sub(r"\t", "\\\\t", value)
            # Finally we remove all control characters
            value = re.sub(r'[\x00-\x1f\x7f-\x9f]', ' ', value)
    return value
