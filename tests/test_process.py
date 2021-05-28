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

__intname__ = 'tests.ofunctions.process'
__author__ = 'Orsiris de Jong'
__copyright__ = 'Copyright (C) 2020-2021 Orsiris de Jong'
__licence__ = 'BSD 3 Clause'
__build__ = '2021052801'

import multiprocessing
from datetime import datetime
from time import sleep

from ofunctions.process import *


def test_kill_childs():
    """
    We'll check if kill_childs successfully stops multiprocessing childs by checking the execution time
    This test is time based so we don't need to use the child pid logic to test a child pid based function ;)
    """
    workers = 2
    child_exec_time = 30

    process_list = []

    start_time = datetime.utcnow()

    while workers > 0:
        process = multiprocessing.Process(target=sleep, args=(child_exec_time,))
        process.start()
        process_list.append(process)
        workers -= 1

    running_workers = len(process_list)
    print('Running {} workers'.format(running_workers))

    childs_still_run = True
    while childs_still_run:
        childs_still_run = False
        for child in process_list:
            if child.is_alive():
                childs_still_run = True
            # Now let's kill the childs if at least 3 seconds elapsed
            if (datetime.utcnow() - start_time).total_seconds() >= 3:
                kill_childs()
            sleep(.1)

    stop_time = datetime.utcnow()

    exec_time = stop_time - start_time
    print('Executed for {} seconds'.format(exec_time))
    assert exec_time.total_seconds() < 10, 'Execution should have been halted before workers got to finished their job'


if __name__ == '__main__':
    print('Example code for %s, %s' % (__intname__, __build__))
    test_kill_childs()
