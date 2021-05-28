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

__intname__ = 'ofunctions.process'
__author__ = 'Orsiris de Jong'
__copyright__ = 'Copyright (C) 2014-2021 Orsiris de Jong'
__description__ = 'Shorthand for killing an entire process tree'
__licence__ = 'BSD 3 Clause'
__version__ = '0.2.0'
__build__ = '2021052801'


import os
import psutil


def kill_childs(pid: int = None, itself: bool = False) -> None:
    """
    Kills all childs of pid (current pid can be obtained with os.getpid())
    If no pid given current pid is taken
    Good idea when using multiprocessing, is to call with atexit.register(ofunctions.kill_childs, os.getpid(),)

    :param pid: Which pid tree we'll kill
    :param itself: Should parent be killed too ?
    """
    parent = psutil.Process(pid if pid is not None else os.getpid())

    for child in parent.children(recursive=True):
        child.kill()
    if itself:
        parent.kill()
