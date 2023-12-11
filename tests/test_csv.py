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

__intname__ = "tests.ofunctions.csv"
__author__ = "Orsiris de Jong"
__copyright__ = "Copyright (C) 2020-2021 Orsiris de Jong"
__licence__ = "BSD 3 Clause"
__build__ = "2021070201"

import sys
from ofunctions.csv import *
from ofunctions.file_utils import remove_file, get_writable_random_file

# python 2.7 compat fixes
if sys.version_info[0] < 3:
    from io import open as open


def test_csv_dict_reader():
    file = get_writable_random_file("csv_dict_reader")
    # Prepare a basic CSV file

    with open(file, "wt", encoding="utf-8") as fp:
        # python 2.7 compat fixes
        if sys.version_info[0] < 3:
            csv_content = (
                "SOME;CSV HEADER;WITH COLUMNS\n1;2;3\n#commented;out;line\nA;B;C\n4;5;6"
            )
        else:
            csv_content = (
                "SOME;CSV HEADER;WITH COLUMNS\n1;2;3\n#commented;out;line\nA;B;C\n4;5;6"
            )
        fp.write(csv_content)
        fp.flush()

    data = csv_dict_reader(file, skip_comment_char="#", delimiter=";", fieldnames=None)
    for index, line in enumerate(data):
        print(index, line)
        if index == 0:
            assert line["SOME"] == "1"
            assert line["CSV HEADER"] == "2"
            assert line["WITH COLUMNS"] == "3"
        if index == 1:
            assert line["SOME"] == "A"
            assert line["CSV HEADER"] == "B"
            assert line["WITH COLUMNS"] == "C"
        if index == 2:
            assert line["SOME"] == "4"
            assert line["CSV HEADER"] == "5"
            assert line["WITH COLUMNS"] == "6"
    remove_file(file)


if __name__ == "__main__":
    print("Example code for %s, %s" % (__intname__, __build__))
    test_csv_dict_reader()
