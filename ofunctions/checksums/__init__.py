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

# python 2.7 compat fixes
from __future__ import unicode_literals

__intname__ = "ofunctions.checksums"
__author__ = "Orsiris de Jong"
__copyright__ = "Copyright (C) 2019-2022 Orsiris de Jong"
__description__ = "SHA256 Checksumming, manifest file creation and verification"
__licence__ = "BSD 3 Clause"
__version__ = "1.1.0"
__build__ = "2022070501"
__compat__ = "python2.7+"


import os
import sys
import hashlib
from datetime import datetime
from ofunctions.file_utils import get_paths_recursive

# python 2.7 compat fixes
if sys.version_info[0] < 3:
    from io import open as open


def sha256sum_data(data):
    # type: (bytes) -> str
    """
    Returns sha256sum of some data
    """
    sha256 = hashlib.sha256()
    sha256.update(data)
    return sha256.hexdigest()


def sha256sum(file):
    # type: (str) -> str
    """
    Returns the sha256 sum of a file

    :param file: (str) path to file
    :return: (str) checksum
    """
    sha256 = hashlib.sha256()

    try:
        with open(file, "rb") as file_handle:
            while True:
                data = file_handle.read(65536)
                if not data:
                    break
                sha256.update(data)
        return sha256.hexdigest()
    except IOError as exc:
        raise IOError('Cannot create SHA256 sum for file "%s": %s' % (file, exc))


def check_file_hash(file, hashsum):
    # type: (str, str) -> bool
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

        raise ValueError(
            'File "%s" has an invalid sha256sum "%s". Reference sum is "%s".'
            % (file, calculated_hashsum, hashsum)
        )

    return False


def create_sha256sum_file(directory, sumfile="SHA256SUMS.TXT", depth=1):
    # type: (str, str, int) -> None
    """
    Create a checksum file for a given directory
    This function creates the file on the fly bacause we yield results

    :param directory: (str) path to the directory to create the sumfile for
    :param sumfile: (str) alternative sumfile name
    :param depth: (int) recursivity depth, 0 = infinite
    :return:
    """

    directory = os.path.normpath(directory)
    files = get_paths_recursive(directory, exclude_dirs=True, max_depth=depth)
    try:
        sumfile = os.path.join(directory, sumfile)
        with open(sumfile, "w", encoding="utf-8") as file_handle:
            # python 2.7 compat 'u' replaced by unicode_literals
            file_content = "# Generated on %s UTC\n\n" % datetime.utcnow()
            file_handle.write(file_content)

            def _get_file_sum(files):
                for file in files:
                    if file != sumfile:
                        sha256 = sha256sum(file)
                        yield "{}  {}\n".format(
                            sha256, os.path.relpath(file, directory)
                        )

            for line in _get_file_sum(files):
                if sys.version_info[0] < 3:
                    file_handle.write(line.decode("unicode-escape"))
                else:
                    file_handle.write(line)
                file_handle.flush()
    except (IOError, OSError):
        raise OSError('Cannot create sum file in "%s".' % directory)


def create_manifest_from_dict(manifest_file, manifest_dict):
    # type: (str, dict) -> None
    """
    Creates a manifest file in the way sha256sum would do under linux

    :param manifest_file: Target file for manifest
    :param manifest_dict: Manifest dict like {sha256sum : filename}
    :return:
    """
    try:
        with open(manifest_file, "w", encoding="utf-8") as file_handle:
            for key, value in manifest_dict.items():
                # python 2.7 compat 'u' replaced by unicode_literals
                content = "{}  {}\n".format(key, value)
                file_handle.write(content)
    except IOError as exc:
        raise IOError('Cannot write manifest file "%s": %s' % (manifest_file, exc))


def create_manifest_from_dir(
    manifest_file,  # type: str
    path,  # type: str
    remove_prefixes=None,  # type: list
    f_exclude_list=None,  # type: list
    d_exclude_list=None,  # type: list
):
    # type: (...) -> None
    """
    Creates a bash like file manifest with sha256sum and filenames
    Just like create_sha256sum_file() except we keep full paths and may remove prefixes


    :param manifest_file: path of resulting manifest file
    :param path: path of directory to create manifest for
    :param remove_prefixes: optional path prefix to remove from files in manifest
    :param f_exclude_list: optional file exclude list
    :param d_exclude_list: optional directory exclude list
    :return:
    """
    if not os.path.isdir(path):
        raise NotADirectoryError("Path [%s] does not exist." % path)

    files = get_paths_recursive(
        path,
        f_exclude_list=f_exclude_list,
        d_exclude_list=d_exclude_list,
        exclude_dirs=True,
    )
    with open(manifest_file, "w", encoding="utf-8") as file_handle:
        for file in files:
            sha256 = sha256sum(file)
            for prefix in remove_prefixes if remove_prefixes is not None else []:
                if file.startswith(prefix):
                    file = file[len(prefix) :].lstrip(os.sep)
            # python 2.7 compat 'u' replaced by unicode_literals
            file_content = "{}  {}\n".format(sha256, file)
            file_handle.write(file_content)
