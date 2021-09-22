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
__version__ = '1.0.0'
__build__ = '2021092201'


import os
import sys
import psutil
import signal
from typing import Optional, Union, List


def kill_childs(
    pid=None,  # type: int
    itself=False,  # type: bool
    soft_kill=False,  # type: bool
):
    # type: (...) -> bool
    """
    Inline version of ofunctions.kill_childs that has no hard dependency on psutil

    Kills all childs of pid (current pid can be obtained with os.getpid())
    If no pid given current pid is taken
    Good idea when using multiprocessing, is to call with atexit.register(ofunctions.kill_childs, os.getpid(),)

    Beware: MS Windows does not maintain a process tree, so child dependencies are computed on the fly
    Knowing this, orphaned processes (where parent process died) cannot be found and killed this way

    Prefer using process.send_signal() in favor of process.kill() to avoid race conditions when PID was reused too fast

    :param pid: Which pid tree we'll kill
    :param itself: Should parent be killed too ?
    """
    sig = None

    """
    Extract from Python3 doc
    On Windows, signal() can only be called with SIGABRT, SIGFPE, SIGILL, SIGINT, SIGSEGV, SIGTERM, or SIGBREAK.
    A ValueError will be raised in any other case. Note that not all systems define the same set of signal names;
    an AttributeError will be raised if a signal name is not defined as SIG* module level constant.
    """

    try:
        if not soft_kill and hasattr(signal, "SIGKILL"):
            # Don't bother to make pylint go crazy on Windows
            # pylint: disable=E1101
            sig = signal.SIGKILL
        else:
            sig = signal.SIGTERM
    # Handle situation where no signal is defined
    except NameError:
        sig = None

    def _process_killer(
        process,  # type: Union[subprocess.Popen, psutil.Process]
        sig,  # type: signal.valid_signals
        soft_kill,  # type: bool
    ):
        # (...) -> None
        """
        Simple abstract process killer that works with signals in order to avoid reused PID race conditions
        and can prefers using terminate than kill
        """
        if sig:
            try:
                process.send_signal(sig)
            # psutil.NoSuchProcess might not be available, let's be broad
            # pylint: disable=W0703
            except Exception:
                pass
        else:
            if soft_kill:
                process.terminate()
            else:
                process.kill()

    # If we cannot identify current process using psutil, fallback to os.kill()
    try:
        current_process = psutil.Process(pid if pid is not None else os.getpid())
    # psutil.NoSuchProcess might not be available, let's be broad
    # pylint: disable=W0703
    except Exception:
        if itself:
            os.kill(
                pid, 15
            )  # 15 being signal.SIGTERM or SIGKILL depending on the platform
        return False

    for child in current_process.children(recursive=True):
        _process_killer(child, sig, soft_kill)

    if itself:
        _process_killer(current_process, sig, soft_kill)
    return True


def get_processes_by_name(name: str) -> Optional[List[psutil.Process]]:
    """
    Get a process by name
    """

    process_list = []

    for process in psutil.process_iter():
        if process.name() == name:
            process_list.append(process)

    return process_list
