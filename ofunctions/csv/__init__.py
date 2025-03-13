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

__intname__ = "ofunctions.csv"
__author__ = "Orsiris de Jong"
__copyright__ = "Copyright (C) 2019-2024 Orsiris de Jong"
__description__ = "CSV file reader with header management, fieldnames, delimiters and comment skipping"
__licence__ = "BSD 3 Clause"
__version__ = "1.0.2"
__build__ = "2024090701"
__compat__ = "python2.7+"


import sys
import csv

# python 2.7 compat fixes
try:
    from typing import Iterable
except ImportError:
    pass

if sys.version_info[0] < 3:
    from io import open as open


# Use OrderedDict for Python < 3.6 since csv.DictReader won't have ordered output
if sys.version_info[0] < 3 or (sys.version_info[0] == 3 and sys.version_info[1] < 6):
    from collections import OrderedDict

    use_OrderedDict = True
else:
    use_OrderedDict = False


def csv_dict_reader(file, skip_comment_char=None, encoding="utf-8", **kwargs):
    # type: (str, str, str, dict) -> Iterable
    """
    Reads CSV file and provides a generator for every line and skips commented out lines

    ATTENTION, this gave me headaches:
    Python < 3.6 returns unordered dicts, so it looks like results are random, but only the dict order is
    Python == 3.7 returns OrderedDict instead of dict
    Python >= 3.8 returns dict with ordered results


    :param file: (str) path to csv file to read
    :param skip_comment_char: (str) optional character which, if found on first row, will skip row
    :param delimiter: (char) CSV delimiter char
    :param fieldnames: (list) CSV field names for dictionary creation, implies that no header is present in file
                              If not given, first line is used as header and skipped from results
    :param encoding: Default file encoding
    :param kwargs:
    :return: csv object that can be iterated
    """

    delimiter = kwargs.pop("delimiter", ",")
    fieldnames = kwargs.pop("fieldnames", None)

    with open(file, encoding=encoding) as fp:
        csv_data = csv.DictReader(fp, delimiter=delimiter, fieldnames=fieldnames)

        for row in csv_data:
            if use_OrderedDict:
                # pylint: disable=E0606 (possibly-used-before-assignment)
                row = OrderedDict(
                    sorted(
                        row.items(), key=lambda item: csv_data.fieldnames.index(item[0])
                    )
                )
            row_name = list(row)[0]
            if skip_comment_char:
                if row[row_name].startswith(skip_comment_char):
                    continue
            yield row
            continue
