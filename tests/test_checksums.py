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

__intname__ = "tests.ofunctions.checksums"
__author__ = "Orsiris de Jong"
__copyright__ = "Copyright (C) 2020-2021 Orsiris de Jong"
__licence__ = "BSD 3 Clause"
__build__ = "2021020901"

from ofunctions.checksums import *
from ofunctions.file_utils import remove_file
from ofunctions.random import random_string


def prepare_temp_file():
    filename = "ofunctions.checksum_file." + random_string(16) + ".file"
    test_directory = os.path.abspath(os.path.dirname(__file__))
    path = os.path.join(test_directory, filename)
    remove_file(path)
    return path


def create_test_file():
    """
    Creates a test file which sha256sum should be 4c77f1bd193cac476cea5af2225e8c0177d5a009390aa6e119c211a00cf325c9
    """
    file = prepare_temp_file()
    with open(file, "wb") as fp:
        fp.write(b"haxx0r3000")
    return file


def test_sha256sum():
    test_file = create_test_file()
    sum = sha256sum(test_file)
    assert (
        sum == "4c77f1bd193cac476cea5af2225e8c0177d5a009390aa6e119c211a00cf325c9"
    ), "Bogus checksum"
    remove_file(test_file)


def test_check_file_hash():
    test_file = create_test_file()
    result = check_file_hash(
        test_file, "4c77f1bd193cac476cea5af2225e8c0177d5a009390aa6e119c211a00cf325c9"
    )
    assert result is True, "Bogus file hash check"
    remove_file(test_file)


def test_create_sha256sum_file():
    test_file = create_test_file()
    filename = os.path.basename(test_file)
    test_directory = os.path.abspath(os.path.dirname(test_file))
    create_sha256sum_file(test_directory)
    sum_file = os.path.join(test_directory, "SHA256SUMS.TXT")
    with open(sum_file, "r") as fp:
        data = fp.read()
        assert (
            "{}  {}".format(
                "4c77f1bd193cac476cea5af2225e8c0177d5a009390aa6e119c211a00cf325c9",
                filename,
            )
            in data
        ), "sha256file does not contain my favorite file"
    remove_file(sum_file)
    remove_file(test_file)


def test_create_manifest_from_dir():
    """
    Does not test prefixes
    """
    manifest_file = prepare_temp_file()
    test_file = create_test_file()
    create_manifest_from_dir(manifest_file, os.path.dirname(manifest_file))
    with open(manifest_file, "r") as fp:
        data = fp.read()
        print(
            "{}  {}".format(
                "4c77f1bd193cac476cea5af2225e8c0177d5a009390aa6e119c211a00cf325c9",
                test_file,
            )
        )
        print(data)
        assert (
            "{}  {}".format(
                "4c77f1bd193cac476cea5af2225e8c0177d5a009390aa6e119c211a00cf325c9",
                test_file,
            )
            in data
        ), "sha256file does not contain my favorite file"
    remove_file(manifest_file)
    remove_file(test_file)


if __name__ == "__main__":
    print("Example code for %s, %s" % (__intname__, __build__))
    test_sha256sum()
    test_check_file_hash()
    test_create_sha256sum_file()
    test_create_manifest_from_dir()
