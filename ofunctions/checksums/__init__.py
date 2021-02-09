#! /usr/bin/env python
#  -*- coding: utf-8 -*-
#
# This file is part of ofunctions module

"""
ofunctions is a general library for basic repetitive tasks that should be no brainers :)

Versioning semantics:
    Major version: backward compatibility breaking changes
    Minor version: New functionality
    Patch version: Backwards compatible bug fixes

"""

__intname__ = 'ofunctions.checksums'
__author__ = 'Orsiris de Jong'
__copyright__ = 'Copyright (C) 2019-2021 Orsiris de Jong'
__licence__ = 'BSD 3 Clause'
__version__ = '0.2.1'
__build__ = '2020110201'


import os
import hashlib
from datetime import datetime
from ofunctions.file_utils import get_files_recursive


def sha256sum(file: str) -> str:
    """
    Returns the sha256 sum of a file

    :param file: (str) path to file
    :return: (str) checksum
    """
    sha256 = hashlib.sha256()

    try:
        with open(file, 'rb') as file_handle:
            while True:
                data = file_handle.read(65536)
                if not data:
                    break
                sha256.update(data)
        return sha256.hexdigest()
    except IOError:
        raise IOError('Cannot create SHA256 sum for file "%s"' % file) from IOError


def check_file_hash(file: str, hashsum: str) -> bool:
    """
    Checks a file against given sha256sum

    :param file: (str) path to file
    :param hashsum: (str) sha256 sum
    :return: (bool)
    """

    hashsum = hashsum.lower()
    if os.path.isfile(file):
        calculated_hashsum = sha256sum(file).lower()
        if hashsum == calculated_hashsum:
            return True

        raise ValueError('File "%s" has an invalid sha256sum "%s". Reference sum is "%s".'
                         % (file, calculated_hashsum, hashsum))

    return False


def create_sha256sum_file(directory: str, sumfile: str = 'SHA256SUMS.TXT', depth: int = 1) -> None:
    """
    Create a checksum file for a given directory
    This function creates the file on the fly bacause we yield results

    :param directory: (str) path to the directory to create the sumfile for
    :param sumfile: (str) alternative sumfile name
    :param depth: (int) recursivity depth, 0 = infinite
    :return:
    """

    directory = os.path.normpath(directory)
    files = get_files_recursive(directory, depth=depth)
    try:
        sumfile = os.path.join(directory, sumfile)
        with open(sumfile, 'w') as file_handle:
            file_handle.write('# Generated on %s\n\n' % datetime.today())

            def _get_file_sum(files):
                for file in files:
                    if file != sumfile:
                        sha256 = sha256sum(file)
                        yield '%s   %s\n' % (sha256, os.path.relpath(file, directory))

            for line in _get_file_sum(files):
                file_handle.write(line)
                file_handle.flush()
    except (IOError, OSError):
        raise OSError('Cannot create sum file in "%s".' % directory)


def create_manifest_from_dict(manifest_file: str, manifest_dict: dict) -> None:
    """
    Creates a manifest file in the way sha256sum would do under linux

    :param manifest_file: Target file for manifest
    :param manifest_dict: Manifest dict like {sha256sum : filename}
    :return:
    """
    try:
        with open(manifest_file, 'w', encoding='utf-8') as file_handle:
            for key, value in manifest_dict.items():
                file_handle.write('%s  %s\n' % (key, value))
    except IOError:
        raise IOError('Cannot write manifest file "%s".' % manifest_file) from IOError



def create_manifest_from_dir(manifest_file: str, path: str, remove_prefixes : list = None,
                             f_exclude_list: list = None, d_exclude_list: list = None) -> None:
    """
    Creates a bash like file manifest with sha256sum and filenames


    :param manifest_file: path of resulting manifest file
    :param path: path of directory to create manifest for
    :param remove_prefixes: optional path prefix to remove from files in manifest
    :param f_exclude_list: optional file exclude list
    :param d_exclude_list: optional directory exclude list
    :return:
    """
    if not os.path.isdir(path):
        raise NotADirectoryError('Path [%s] does not exist.' % path)

    files = get_files_recursive(path, f_exclude_list=f_exclude_list, d_exclude_list=d_exclude_list)
    with open(manifest_file, 'w', encoding='utf-8') as file_handle:
        for file in files:
            sha256 = sha256sum(file)
            for prefix in remove_prefixes if remove_prefixes is not None else []:
                if file.startswith(prefix):
                    file = file[len(prefix):].lstrip(os.sep)
            file_handle.write('%s  %s\n' % (sha256, file))