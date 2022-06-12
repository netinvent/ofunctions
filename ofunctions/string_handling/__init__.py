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

# python 2.7 compat fixes so all strings are considered unicode
from __future__ import unicode_literals

__intname__ = "ofunctions.string_handling"
__author__ = "Orsiris de Jong"
__copyright__ = "Copyright (C) 2014-2022 Orsiris de Jong"
__description__ = "Simple string sanitization functions"
__licence__ = "BSD 3 Clause"
__version__ = "1.2.0"
__build__ = "2022060901"
__compat__ = "python2.7+"


import sys
import unicodedata
import re


def convert_accents(string):
    # type: (str) -> str
    """
    Replace accents by non accents characters when possible

    Original source https://stackoverflow.com/a/44433664/2635443
    """
    return str(
        unicodedata.normalize("NFD", string).encode("ascii", "ignore").decode("utf-8")
    )


def strip_characters(string, regex=r"[]"):
    # type: (str, str) -> str
    """
    Remove everything that is not in the list of allowed chars
    Basically just a regex shorthand
    """
    return re.sub(regex, "", string, re.UNICODE)


def strip_special_characters(string, regex=r"[^a-zA-Z0-9 \n\._]"):
    # type: (str, str) -> str
    """
    Remove special characters except the ones allowed in the regex
    Basically just a regex shorthand
    """
    return strip_characters(string, regex)


def strip_non_alnum_characters(string, keep_accents=True):
    # type: (str, bool) -> str
    """
    Return only alphanumeric strings
    Another regex shorthand
    """
    if keep_accents:
        regex = "[^a-zA-Z0-9À-ÖØ-öø-ÿ]"
    else:
        regex = r"[^a-zA-Z0-9]"

    return strip_characters(string, regex)


def sanitize_filename(string):
    # type: (str) -> str
    """
    Another shorthand for some regex that allows to make filenames windows/linux compatible
    """
    return strip_characters(string, regex=r"[:\\/\*&{}#\$<>@`'\"\|!]")
