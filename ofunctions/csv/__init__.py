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
__version__ = '0.4.0'
__build__ = '2021070201'


import csv
from typing import Iterable


def csv_dict_reader(file: str, skip_comment_char: str = None, encoding: str = 'utf-8',
                    **kwargs) -> Iterable:
    """
    Reads CSV file and provides a generator for every line and skips commented out lines

    ATTENTION, this gave me headaches:
    Python < 3.6 returns unordered dicts, so it looks like results are random, but only the dict order is
    Python == 3.7 returns OrderedDict instead of dict
    Python >= 3.8 returns dict with ordered results


    :param file: (str) path to csv file to read
    :param skip_comment_char: (str) optional character which, if found on first row, will skip row
    :param delimiter: (char) CSV delimiter char
    :param fieldnames: (list) CSV field names for dictionnary creation, implies that no header is present in file
                              If not given, first line is used as header and skipped from results
    :param encoding: Default file encoding
    :param kwargs:
    :return: csv object that can be iterated
    """

    delimiter = kwargs.pop('delimiter', ',')
    fieldnames = kwargs.pop('fieldnames', None)

    with open(file, encoding=encoding) as fp:
        csv_data = csv.DictReader(fp, delimiter=delimiter, fieldnames=fieldnames)

        for row in csv_data:
            row_name = list(row)[0]
            if skip_comment_char:
                if row[row_name].startswith(skip_comment_char):
                    continue
            yield row
            continue
