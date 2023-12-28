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

__intname__ = "tests.ofunctions.process"
__author__ = "Orsiris de Jong"
__copyright__ = "Copyright (C) 2020-2021 Orsiris de Jong"
__licence__ = "BSD 3 Clause"
__build__ = "2021092201"

import multiprocessing
from datetime import datetime
from time import sleep
import subprocess

from ofunctions.process import *


def test_kill_childs():
    """
    We'll check if kill_childs successfully stops multiprocessing childs by checking the execution time
    This test is time based so we don't need to use the child pid logic to test a child pid based function ;)
    """
    workers = 4
    child_exec_time = 30

    process_list = []

    start_time = datetime.utcnow()

    while workers > 0:
        process = multiprocessing.Process(target=sleep, args=(child_exec_time,))
        process.start()
        process_list.append(process)
        workers -= 1

    running_workers = len(process_list)
    print("Running {} workers".format(running_workers))

    childs_still_run = True
    kill_childs_ran = False
    while childs_still_run:
        childs_still_run = False
        for child in process_list:
            if child.is_alive():
                childs_still_run = True
            # Now let's kill the childs if at least 3 seconds elapsed
            if (datetime.utcnow() - start_time).total_seconds() >= 3:
                if not kill_childs_ran:
                    kill_childs()
                    kill_childs_ran = True
            sleep(0.1)

    stop_time = datetime.utcnow()

    exec_time = stop_time - start_time
    print("Executed for {} seconds".format(exec_time))
    assert (
        exec_time.total_seconds() < 10
    ), "Execution should have been halted before workers got to finished their job"


def test_get_processes_by_name():
    """
    Test that we can identify processes by name
    """
    import subprocess

    if os.name == "nt":
        proc_name = "ping.exe"
        exe_path = get_absolute_path(proc_name)
        command = "{} -n 4 127.0.0.1".format(exe_path)
    else:
        proc_name = "ping"
        exe_path = get_absolute_path(proc_name)
        command = ["{}".format(exe_path), "-c", "1", "127.0.0.1"]

    # Don't create process with shell=True or else it will delay creation
    # Create with subprocess.PIPE redir so we don't wait for execution
    created_processes = []
    for i in range(0, 2):
        print("Running command ", command)
        created_processes.append(
            subprocess.Popen(
                command, shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE
            )
        )

    for process in created_processes:
        print("Created process {} with pid {}".format(process, process.pid))

    found_processes = get_processes_by_name(proc_name)

    print(found_processes)

    # Now let's compare, we should have found both processes by now
    for found_process in found_processes:
        found = False
        for created_process in created_processes:
            if found_process.pid == created_process.pid:
                found = True
        if not found:
            assert False, "Did not find process"


if __name__ == "__main__":
    print("Example code for %s, %s" % (__intname__, __build__))
    test_kill_childs()
    test_get_processes_by_name()
