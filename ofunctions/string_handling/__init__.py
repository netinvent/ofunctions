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
__copyright__ = "Copyright (C) 2014-2025 Orsiris de Jong"
__description__ = "Simple string sanitization functions"
__licence__ = "BSD 3 Clause"
__version__ = "1.3.1"
__build__ = "2025070301"
__compat__ = "python2.7+"


import sys
import unicodedata
import re


# python 2.7 compat fixes
if sys.version_info[0] < 3:
    accent_chars = [
        "à",
        "á",
        "â",
        "ã",
        "ä",
        "å",
        "è",
        "é",
        "ê",
        "ë",
        "ì",
        "í",
        "î",
        "ï",
        "ò",
        "ó",
        "ô",
        "õ",
        "ö",
        "ù",
        "ú",
        "û",
        "ü",
    ]
else:
    accent_chars = [chr(code) for code in range(int(0x00C0), int(0x01F7))]
# Ambiguous characters that could be mistaken for each other or have special functions in os
ambiguous_chars = ["O", "o", "0", "I", "l", "1"]


def convert_accents(string):
    # type: (str) -> str
    """
    Replace accents by non accents characters when possible

    Original source https://stackoverflow.com/a/44433664/2635443

    Aonther elegant implementation
    From https://stackoverflow.com/a/518232/2635443

    return "".join(
        c
        for c in unicodedata.normalize("NFD", string)
        if unicodedata.category(c) != "Mn"
    )

    """
    if isinstance(string, str):
        return str(
            unicodedata.normalize("NFD", string)
            .encode("ascii", "ignore")
            .decode("utf-8")
        )
    return string


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
