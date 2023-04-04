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

__intname__ = "ofunctions.platform"
__author__ = "Orsiris de Jong"
__copyright__ = "Copyright (C) 2014-2023 Orsiris de Jong"
__description__ = "Very basic platform identification"
__licence__ = "BSD 3 Clause"
__version__ = "1.4.1"
__build__ = "2023033001"
__compat__ = "python2.7+"

import os
import sys
import re
import platform


def get_os():
    # type: () -> str
    """
    Simple windows / linux identification that handles msys too
    """
    if os.name == "nt":
        return "Windows"
    if os.name == "posix":
        # uname property does not exist under windows
        # pylint: disable=E1101
        result = os.uname()[0]

        if result.startswith("MSYS_NT-"):
            result = "Windows"

        return result
    raise OSError("Cannot get os, os.name=[%s]." % os.name)


def os_arch():
    # type: () -> str
    """
    Get current machine (python independant) architecture
    """
    # Returns:
    # linux:
    # armv71, aarch64, x86_64
    # windows:
    # AMD64x
    machine = platform.machine() 
    if machine == "AMD64":
        return "x64"
    machine = machine.lower()
    if "x86_64" in machine:
        return "x64"
    elif "aarch64" in machine or "armv8" in machine:
        return "arm64"
    # 32 bit arm
    elif "arm" in machine: 
        return "arm"
    elif "i386" in machine or "i686" in machine:
        return "x86"
    else:
        return machine


def python_arch():
    # type: () -> str
    """
    Get current python interpreter architecture
    """
    if os.name == "nt":
        if "AMD64" in sys.version:
            return "x64"
        return "x86"

    # uname property does not exist under windows
    # pylint: disable=E1101
    arch = os.uname()[4].lower()
    if "x86_64" in arch:
        return "x64"
    # 64 bit arm
    elif "aarch64" in arch or "armv8" in arch:
        return "arm64"
    # 32 bit arm
    elif "arm" in arch:
        return "arm"
    elif "i386" in arch or "i686" in arch:
        return "x86"
    else:
        return arch


def is_64bit_python():
    # type: () -> bool
    """
    Detect if python is 64 bit but stay OS agnostic
    """
    return sys.maxsize > 2**32


def get_distro():
    # type: () -> (str, float, float, float, str)
    """
    Detect distribution and version
    # TODO develop other flavors than RHEL and clones
    """

    RHEL_path = "/etc/redhat-release"
    """
    File content examples:

    Red Hat Enterprise Server release 7.5 (Maipo)
    AlmaLinux release 8.5 (Arctic Sphynx)
    CentOS Linux release 8.4.2105
    """

    flavor = None
    version = None
    major_version = None
    minor_version = None
    build = None

    if os.path.isfile(RHEL_path):
        flavor = "RHEL"
        with open(RHEL_path, "r") as file_handle:
            result = re.search(
                r"(?:(\d+)\.)?(?:(\d+)\.)?(\*|\d+)", file_handle.read(), re.MULTILINE
            )
            try:
                version = result.group(0)
            except AttributeError:
                pass
            try:
                major_version = result.group(1)
            except IndexError:
                pass
            try:
                minor_version = result.group(2)
            except IndexError:
                pass
            try:
                build = result.group(3)
            except IndexError:
                pass

    return flavor, version, major_version, minor_version, build
