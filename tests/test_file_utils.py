#! /usr/bin/env python
#  -*- coding: utf-8 -*-
#
# This file is part of command_runner module

"""
command_runner is a quick tool to launch commands from Python, get exit code
and output, and handle most errors that may happen

Versioning semantics:
    Major version: backward compatibility breaking changes
    Minor version: New functionality
    Patch version: Backwards compatible bug fixes

"""

__intname__ = 'tests.ofunctions.file_utils'
__author__ = 'Orsiris de Jong'
__copyright__ = 'Copyright (C) 2020-2021 Orsiris de Jong'
__licence__ = 'BSD 3 Clause'
__build__ = '2021020901'

import sys

from ofunctions.file_utils import *


def test_check_path_access():
    # logging.basicConfig(level=logging.DEBUG)
    # Hopefully does not exist
    result = check_path_access(r'/somedirthathopefullydoesnotexistinthisuniverse2424', check='W')
    assert result is False, 'check_path_access failed'
    if os.name == 'nt':
        # should be readable
        result = check_path_access(r'C:\Windows\system32', check='R')
        assert result is True, 'Access to system32 should be readable'
        # should be writable
        check_path_access(os.path.expandvars('%temp%'), check='W')
        assert result is True, 'Access to current temp {} should be writable'.format(os.path.expandvars('%temp'))
    else:
        result = check_path_access('/usr/bin', check='R')
        assert result is True, 'Access to /usr/bin should be readable'
        result = check_path_access(os.path.expandvars('TMPDIR'), check='W')
        assert result is True, 'Access to current temp {} should be writable'.format(os.path.expandvars('%temp'))


def test_glob_path_match():
    match = glob_path_match(os.path.dirname(__file__), ['*ofunc*'])
    assert match is True, 'glob_path_match test failed'


def print_perm_error(file):
    print('Perm error on: %s' % file)


def test_get_files_recursive():
    files = get_files_recursive(os.path.dirname(__file__), fn_on_perm_error=print_perm_error)

    print('Current files in folder: %s' % files)
    assert isinstance(files, chain)
    for file in files:
        print(file)
    files = get_files_recursive(os.path.dirname(__file__))
    assert 'bisection.py' in [os.path.basename(file) for file in files], 'get_files_recursive test failed'

    # Include directories in output
    files = get_files_recursive(os.path.dirname(__file__), include_dirs=True)
    assert 'json_sanitize.py' in [os.path.basename(file) for file in files], 'get_files_recursive with dirs test failed'

    # Try d_exclude_list
    files = get_files_recursive(os.path.dirname(os.path.dirname(__file__)),
                                d_exclude_list=['tests'], include_dirs=True)
    assert 'tests' + os.sep + 'file_utils.py' not in [os.path.basename(file) for file in
                                 files], 'get_files_recursive with d_exclude_list failed'

    # Try f_exclude_list
    files = get_files_recursive(os.path.dirname(__file__), f_exclude_list=['file_utils.py'])
    assert 'file_utils.py' not in [os.path.basename(file) for file in
                                   files], 'get_files_recursive with f_exclude_list failed'

    # Try ext_exclude_list
    files = get_files_recursive(os.path.dirname(__file__), ext_exclude_list=['.py'])
    for file in files:
        if file.endswith('.py'):
            assert False, 'get_files_recursive failed with ext_exclude_list'

    # Try ext_include_list
    files = get_files_recursive(os.path.dirname(__file__), ext_include_list=['.py'])
    for file in files:
        if not file.endswith('.py'):
            assert False, 'get_files_recursive failed with ext_include_list'


def test_is_file_older_than():
    # Test is_older_than()
    result = is_file_older_than(sys.argv[0], years=0, days=0, hours=0, minutes=0, seconds=5)
    assert result is True, 'Current file should not be newer than 5 seconds'

    result = is_file_older_than(sys.argv[0], years=200, days=0, hours=0, minutes=0, seconds=0)
    assert result is False, 'Ahh see... A file older than 200 years ? Is my code still running in 2220 ?'


if __name__ == '__main__':
    print('Example code for %s, %s' % (__intname__, __build__))
    test_check_path_access()
    test_glob_path_match()
    test_get_files_recursive()
    test_is_file_older_than()
