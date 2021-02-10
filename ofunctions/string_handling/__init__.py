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

__intname__ = 'ofunctions.string_handling'
__author__ = 'Orsiris de Jong'
__copyright__ = 'Copyright (C) 2014-2021 Orsiris de Jong'
__licence__ = 'BSD 3 Clause'
__version__ = '0.1.1'
__build__ = '2021020901'


import unicodedata
import re


def convert_accents(string: str) -> str:
    """
    Replace accents by non accents characters when possible

    Original source https://stackoverflow.com/a/44433664/2635443
    """
    return str(unicodedata.normalize('NFD', string).encode('ascii', 'ignore').decode("utf-8"))


def strip_special_characters(string: str, regex: str = r'[^a-zA-Z0-9 \n\._]') -> str:
    """
    Remove special characters except the ones allowed in the regex
    """
    return re.sub(regex, '', string)

