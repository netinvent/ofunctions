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

__intname__ = "ofunctions.process"
__author__ = "Orsiris de Jong"
__copyright__ = "Copyright (C) 2014-2025 Orsiris de Jong"
__description__ = "Shorthand for killing an entire process tree"
__licence__ = "BSD 3 Clause"
__version__ = "2.1.0"
__build__ = "2025020401"
__compat__ = "python2.7+"


import os
import psutil
import signal
import logging
from time import sleep
from datetime import datetime


logger = logging.getLogger(__intname__)


# python 2.7 compat fixes
try:
    from typing import Optional, List
except ImportError:
    pass


def is_pid_alive(
    pid,  # type: int or str
):
    #  type: (...) -> bool
    """
    Quick check if pid is alive
    From https://stackoverflow.com/a/74720401/2635443
    """
    try:
        process = psutil.Process(pid)
    except psutil.Error as error:  # includes NoSuchProcess error
        return False
    if psutil.pid_exists(pid) and process.status() not in (
        psutil.STATUS_DEAD,
        psutil.STATUS_ZOMBIE,
    ):
        return True
    return False


def is_pid_dead(
    pid,  # type: int
):
    #  type: (...) -> bool
    """
    Reverse of is_pid_alive, for use in conditions, eg grace timer
    """
    return not is_pid_alive(pid)


def kill_childs(
    pid=None,  # type: int
    itself=False,  # type: bool
    children=True,  # type: bool
    verbose=False,  # type: bool
    grace_period=1,  # type: int
    fast_kill=False,  # type: bool
    process_name=None,  # type: Optional[str]
):
    # type: (...) -> bool
    """
    Kills pid or all childs of pid (current pid can be obtained with os.getpid())
    If no pid given current pid is taken
    Good idea when using multiprocessing, is to call with atexit.register(ofunctions.kill_childs, os.getpid(),)

    fast_kill will allow to use threads to kill quicker

    Beware: MS Windows does not maintain a process tree, so child dependencies are computed on the fly
    Knowing this, orphaned processes (where parent process died) cannot be found and killed this way

    Prefer using process.send_signal() in favor of process.kill() to avoid race conditions when PID was reused too fast

    :param pid: Which pid tree we'll kill
    :param itself: Should parent be killed too ?
    :param process_name: Only kill childs corresponding to name

    Attention: on windows, process name has extension, eg "restic.exe" instead of restic under Unix

    Extract from Python3 doc
    On Windows, signal() can only be called with SIGABRT, SIGFPE, SIGILL, SIGINT, SIGSEGV, SIGTERM, or SIGBREAK.
    A ValueError will be raised in any other case. Note that not all systems define the same set of signal names;
    an AttributeError will be raised if a signal name is not defined as SIG* module level constant.
    """

    if not pid:
        pid = os.getpid()

    if fast_kill:
        from ofunctions.threading import threaded, wait_for_threaded_result
    else:

        def threaded(fn):
            """
            Just an empty decorator so we don't actually need ofunctions.theading
            This exists for compat reasons for earlier versions of kill_childs without fast_kill option
            """

            def wrapper(*args, **kwargs):
                kwargs.pop("__no_threads")
                return fn(*args, **kwargs)

            return wrapper

    try:
        sigterm = signal.SIGTERM
        if hasattr(signal, "SIGKILL"):
            # Don't bother to make pylint go crazy on Windows
            # pylint: disable=E1101
            sigkill = signal.SIGKILL
        else:
            sigkill = None
    # Handle situation where no signal is defined
    except NameError:
        sigkill = sigterm = None

    def _grace_period_timer(condition_fn, *args, **kwargs):
        #  type: (...) -> None
        """
        Wait for grace period or condition to be true$
        """
        start_time = datetime.utcnow()
        while True:
            if (datetime.utcnow() - start_time).total_seconds() > grace_period:
                logger.warning(
                    "kill_childs grace period of {} seconds reached. Now being merciless process-killer".format(
                        grace_period
                    )
                )
                break
            try:
                if condition_fn:
                    if condition_fn(*args, **kwargs):
                        break
            # pylint: disable=W0703
            except Exception as exc:
                logger.debug("Conditional grace timer stopped: {}".format(exc))
                break
            # Arbitrary time to avoid CPU hogging
            sleep(0.1)

    @threaded
    def _process_killer(
        process,  # type: psutil.Process
        is_child=False,  # type: bool
    ):
        # (...) -> None
        """
        Simple abstract process killer that works with signals in order to avoid reused PID race conditions
        and can prefers using terminate than kill
        """
        if sigterm:  # sigterm should exist on all oses
            try:
                _grace_period_timer(is_pid_dead, process.pid)
                if verbose:
                    logger.info(
                        "Asking {} process pid {} nicely to terminate".format(
                            "child" if is_child else "", process.pid
                        )
                    )
                try:
                    process.send_signal(sigterm)
                except psutil.NoSuchProcess:
                    pass
                except Exception as exc:
                    logger.warning(
                        "Cannot send sigterm to process with pid {}: {}".format(
                            process.pid, exc
                        )
                    )

                if sigkill and is_pid_alive(process.pid):
                    _grace_period_timer(is_pid_dead, process.pid)
                    if verbose:
                        logger.warning(
                            "Killing: {} with sigkill {}".format(process, sigkill)
                        )
                    try:
                        process.send_signal(sigkill)
                    except psutil.NoSuchProcess:
                        pass
                    except Exception as exc:
                        logger.error(
                            "Cannot send sigterm to process with pid {}: {}".format(
                                process.pid, exc
                            )
                        )
                else:
                    _grace_period_timer(is_pid_dead, process.pid)
                    try:
                        process.kill()
                    except psutil.NoSuchProcess:
                        pass
                    # pylint: disable=W0703
                    except Exception as exc:
                        logger.error(
                            "Process with pid {} seems impossible to kill.: {}".format(
                                process.pid, exc
                            )
                        )
            # psutil.NoSuchProcess might not be available, let's be broad
            # pylint: disable=W0703
            except Exception as exc:
                logger.error("Cannot send signals to process: {}".format(exc))
        else:
            if is_pid_alive(process.pid):
                try:
                    process.terminate()
                except psutil.NoSuchProcess:
                    pass
                # pylint: disable=W0703
                except Exception as exc:
                    logger.warning(
                        "Cannot send terminate to process with pid {}: {}".format(
                            process.pid, exc
                        )
                    )
                if is_pid_alive(process.pid):
                    _grace_period_timer(is_pid_dead, process.pid)
                    try:
                        process.kill()
                    except psutil.NoSuchProcess:
                        pass
                    # pylint: disable=W0703
                    except Exception as exc:
                        logger.error(
                            "Process with pid {} seems impossible to kill via kill...: {}".format(
                                process.pid, exc
                            )
                        )

    # Let's first wait some arbitrary time for processes to close
    try:
        current_process = psutil.Process(pid)
    # psutil.NoSuchProcess might not be available, let's be broad
    # pylint: disable=W0703
    except Exception:
        current_process = None

    # If we cannot identify current process using psutil, fallback to os.kill()
    if current_process:
        if children:
            thread_list = []
            for child in current_process.children(recursive=True):
                if process_name:
                    if child.name() != process_name:
                        continue
                try:
                    thread_list.append(
                        _process_killer(
                            child, is_child=True, __no_threads=not fast_kill
                        )
                    )
                # pylint: disable=W0703
                except Exception as exc:
                    logger.error(
                        "Cannot kill child process with pid {}: {}".format(
                            child.pid, exc
                        )
                    )
            if fast_kill:
                wait_for_threaded_result(thread_list)

        if itself:
            try:
                _process_killer(current_process)
            # pylint: disable=W0703
            except Exception as exc:
                logger.error(
                    "Cannot kill parent process with pid {}: {}".format(pid, exc)
                )
    else:
        if children:
            logger.error("Cannot kill process child subtree. Sorry")
        if itself:
            _grace_period_timer(is_pid_dead, pid)
            try:
                if is_pid_alive(pid):
                    os.kill(
                        pid, 15
                    )  # 15 being signal.SIGTERM or SIGKILL depending on the platform
            except OSError as exc:
                if os.name == "nt":
                    # We'll do an ugly hack since os.kill() has some pretty big caveats on Windows
                    # especially for Python 2.7 where we can get Access Denied
                    try:
                        os.system("taskkill /F /pid {}".format(pid))
                    except Exception as exc:
                        logger.error(
                            "Process with pid {} exists but cannot be killed by taskkill: {}".format(
                                pid, exc
                            )
                        )
                else:
                    logger.error(
                        "Process with pid {} exists but cannot be killed by os.kill: {}".format(
                            pid, exc
                        ),
                    )
            except Exception as exc:
                logger.error(
                    "Unknown error while trying to kill process: {}".format(exc)
                )
        return False
    return True


def get_processes_by_name(name, ignorecase=None):
    # type: (str, bool) -> Optional[List[psutil.Process]]
    """
    Get a list of processes by name
    """

    if ignorecase is None:
        if os.name == "nt":
            ignorecase = True
        else:
            ignorecase = False

    process_list = []

    for process in psutil.process_iter():
        if ignorecase:
            if process.name().upper() == name.upper():
                process_list.append(process)
        else:
            if process.name() == name:
                process_list.append(process)

    return process_list


def get_absolute_path(executable):
    # type: (str) -> str
    """
    Search for full executable path in preferred shell paths
    This allows avoiding usage of shell=True with subprocess
    """
    executable_path = None

    if os.name == "nt":
        split_char = ";"
    else:
        split_char = ":"
    for path in os.environ.get("PATH", "").split(split_char):
        if os.path.isfile(os.path.join(path, executable)):
            executable_path = os.path.join(path, executable)
    return executable_path
