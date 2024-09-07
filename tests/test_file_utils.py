#! /usr/bin/env python
#  -*- coding: utf-8 -*-
#
# This file is part of command_runner module

"""
Versioning semantics:
    Major version: backward compatibility breaking changes
    Minor version: New functionality
    Patch version: Backwards compatible bug fixes

"""

__intname__ = "tests.ofunctions.file_utils"
__author__ = "Orsiris de Jong"
__copyright__ = "Copyright (C) 2020-2024 Orsiris de Jong"
__licence__ = "BSD 3 Clause"
__build__ = "2021052601"

import sys
from time import sleep

from ofunctions.file_utils import *
from ofunctions.random import random_string


def test_check_path_access():
    # logging.basicConfig(level=logging.DEBUG)
    # Hopefully does not exist
    result = check_path_access(
        r"/somedirthathopefullydoesnotexistinthisuniverse2424", check="W"
    )
    assert result is False, "check_path_access failed"
    if os.name == "nt":
        bin_dir = r"C:\Windows\system32"
        tmp_dir = os.path.expandvars("%temp%")
    else:
        bin_dir = "/usr/bin"
        tmp_dir = "/tmp"
    # should be readable
    result = check_path_access(bin_dir, check="R")
    assert result is True, "Access to bin dir {} should be readable".format(bin_dir)
    # should be writable
    check_path_access(tmp_dir, check="W")
    assert result is True, 'Access to current temp "{}" should be writable'.format(
        tmp_dir
    )


def test_glob_path_match():
    """
    Check that "*est*" matches current "tests" dir
    """
    match = glob_path_match(os.path.dirname(__file__), ["*est*"])
    assert match is True, "glob_path_match test failed"


def print_perm_error(file):
    """
    This function solely exists for test_get_paths_recursive
    """
    print("Perm error on: %s" % file)


def test_get_paths_recursive():
    test_directory = os.path.abspath(os.path.dirname(__file__))
    files = get_paths_recursive(test_directory, fn_on_perm_error=print_perm_error)

    assert isinstance(files, chain)
    print('BEGIN FILE LIST IN "{}"'.format(test_directory))
    for file in files:
        print(file)
    print("END FILE LIST")

    files = get_paths_recursive(test_directory)
    result_list = [os.path.basename(file) for file in files]
    assert (
        "test_bisection.py" in result_list
    ), "get_paths_recursive test failed to find test_bisection.py"
    assert (
        len(result_list) > 10
    ), "test dir file list should contain more than 10 entries for ofunctions package"

    # Include directories in output
    files = get_paths_recursive(test_directory, exclude_dirs=False)
    assert "test_json_sanitize.py" in [
        os.path.basename(file) for file in files
    ], "get_paths_recursive with dirs test failed"

    # Try d_exclude_list on ..\tests
    files = get_paths_recursive(
        os.path.join(test_directory, os.pardir),
        d_exclude_list=["tests"],
        exclude_dirs=False,
    )
    assert "tests" + os.sep + "file_utils.py" not in [
        os.path.basename(file) for file in files
    ], "get_paths_recursive with d_exclude_list failed"

    # Try f_exclude_list
    files = get_paths_recursive(test_directory, f_exclude_list=["test_file_utils.py"])
    assert "test_file_utils.py" not in [
        os.path.basename(file) for file in files
    ], "get_paths_recursive with f_exclude_list failed"

    # Try ext_exclude_list
    files = get_paths_recursive(test_directory, ext_exclude_list=[".py"])
    for file in files:
        if file.endswith(".py"):
            assert False, "get_paths_recursive failed with ext_exclude_list"

    # Try f_include_list
    files = get_paths_recursive(
        test_directory, f_include_list=["test_fi*utils.py"], exclude_dirs=True
    )
    result_list = [os.path.basename(file) for file in files]
    assert (
        "test_file_utils.py" in result_list
    ), "get_paths_recursive with f_include_list failed"
    assert len(result_list) == 1, "get_paths_recursive with f_include_list failed"

    # Try ext_include_list
    files = get_paths_recursive(
        test_directory, ext_include_list=[".py"], exclude_dirs=True
    )
    for file in files:
        if not file.endswith(".py"):
            assert False, "get_paths_recursive failed with ext_include_list"

    # Try min_depth & max_depth
    # We should see tests/file_utils.py but not ./__init__.py
    files = get_paths_recursive(
        os.path.join(test_directory, os.pardir),
        min_depth=2,
        max_depth=2,
        exclude_dirs=True,
    )
    result_list = list(files)
    # Let's first check that we don't have a <root_dir>/__init__.py file
    if "__init__.py" in result_list:
        assert (
            False
        ), "get_paths_recursive failed with min & max depth, root __init__.py file found"

    # Now let's check for subdirectory test_file_utils file
    basename_result_list = [os.path.basename(file) for file in result_list]
    if not os.path.normpath("test_file_utils.py") in basename_result_list:
        assert (
            False
        ), "get_paths_recursive failed with min & max depth, file_utils.py not found"


def test_remove_bom():
    utf8_with_bom_data = b"\xef\xbb\xbf\x13\x37\x00\x12\x05\x01\x12\x01\x05"
    utf8_without_bom_data = b"\x13\x37\x00\x12\x05\x01\x12\x01\x05"

    filename = "ofunctions.test_remove_bom." + random_string(16) + ".file"
    remove_file(filename)

    with open(filename, "wb") as fp:
        fp.write(utf8_with_bom_data)

    remove_bom(filename)

    with open(filename, "rb") as fp:
        file_data = fp.read()
    remove_file(filename)

    assert file_data == utf8_without_bom_data, "Test file does not look like it should"


def test_get_file_time():
    for mac_type in ["ctime", "mtime", "atime"]:
        mac_timestamp = get_file_time(__file__, mac_type)
        print(mac_type, mac_timestamp)
        dt = datetime.fromtimestamp(mac_timestamp)
        assert isinstance(
            dt, datetime
        ), "Timestamp could not be converted to datetime object"
        assert 2021 <= dt.year < 2300, "Code will prabably not run in 200 years, ehh"


def test_check_file_timestamp_delta():
    """
    Windows file creation dates are VERY wrong when requested by python
    The following code will keep earlier file creation dates, even if file is removed
    Hence we'll add some random string to the filename to make sure the tests will not fail
    """
    filename = (
        "ofunctions.test_check_file_timestamp_delta." + random_string(16) + ".file"
    )
    test_directory = os.path.abspath(os.path.dirname(__file__))
    path = os.path.join(test_directory, filename)
    remove_file(path)

    with open(path, "w") as file_handle:
        file_handle.write("test")
    result = check_file_timestamp_delta(
        path, years=0, days=0, hours=0, minutes=0, seconds=-2
    )
    assert result is False, "Just created file should not be older than 2 seconds"
    sleep(3)
    result = check_file_timestamp_delta(
        path, years=0, days=0, hours=0, minutes=0, seconds=-2
    )
    assert result is True, "Just created file should now be older than 2 seconds"
    remove_file(path)

    result = check_file_timestamp_delta(
        sys.argv[0], years=-200, days=0, hours=0, minutes=0, seconds=0
    )
    assert (
        result is False
    ), "Ahh see... A file older than 200 years ? Is my code still running in the year 2221 ?"


def test_hide_file():
    """
    Dumb checks, need to improve tests here
    We need to verifiy that attrib has been run on windows and that file begins with dot on unixes
    """
    filename = "ofunctions.test_hide_file." + random_string(16) + ".file"
    test_directory = os.path.abspath(os.path.dirname(__file__))
    path = os.path.join(test_directory, filename)
    remove_file(path)

    with open(path, "w") as fp:
        fp.write("TEST")

    assert hide_file(path), "File is now hidden"
    assert hide_file(path, False), "File is now visible"

    remove_file(path)


if __name__ == "__main__":
    print("Example code for %s, %s" % (__intname__, __build__))
    test_check_path_access()
    test_glob_path_match()
    test_get_paths_recursive()
    test_remove_bom()
    test_get_file_time()
    test_check_file_timestamp_delta()
    test_hide_file()
