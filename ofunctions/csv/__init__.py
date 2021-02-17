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

__intname__ = 'ofunctions.csv'
__author__ = 'Orsiris de Jong'
__copyright__ = 'Copyright (C) 2019-2021 Orsiris de Jong'
__description__ = 'CSV file reader with header management, fieldnames, delimiters and comment skipping'
__licence__ = 'BSD 3 Clause'
__version__ = '0.2.0'
__build__ = '2020032701'


import csv
from typing import Iterable


def csv_dict_reader(file: str, has_header: bool = False, skip_comment_char: str = None, **kwargs) -> Iterable:
    """
    Reads CSV file and provides a generator for every line in order to save memory


    :param file: (str) path to csv file to read
    :param has_header: (bool) skip first line
    :param skip_comment_char: (str) optional character which, if found on first row, will skip row
    :param delimiter: (char) CSV delimiter char
    :param fieldnames: (list) CSV field names for dictionnary creation
    :param kwargs:
    :return: csv object that can be iterated
    """
    with open(file) as fp:
        csv_data = csv.DictReader(fp, **kwargs)
        # Skip header
        if has_header:
            next(csv_data)

        fieldnames = kwargs.get('fieldnames')
        for row in csv_data:
            # Skip commented out entries
            if fieldnames is not None:
                if skip_comment_char is not None:
                    if not row[fieldnames[0]].startswith(skip_comment_char):
                        yield row
                else:
                    yield row
            else:
                # list(row)[0] is key from row, works with Python 3.7+
                if skip_comment_char is not None:
                    if not row[list(row)[0]].startswith(skip_comment_char):
                        yield row
                else:
                    yield row
