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


__intname__ = 'tests.ofunctions.service_control'
__author__ = 'Orsiris de Jong'
__copyright__ = 'Copyright (C) 2021 Orsiris de Jong'
__licence__ = 'BSD 3 Clause'
__build__ = '2021052601'


import os
from ofunctions.service_control import *


def test_system_service_handler():
    """
    This checks whether we can start / stop services
    Needs to ne run as administrator in order to succeed

    Assumes the given services are started
    """
    os_name = os.name

    # Let's pick a default service to test (may fail depending on environment)
    if os_name == 'nt':
        test_service = 'themes'
    else:
        test_service = 'crond'


    status = system_service_handler(test_service, 'status')
    assert status, '{} service is not started'.format(test_service)

    try:
        result = system_service_handler(test_service, 'stop')
        assert result, '{} service could not be stopped'.format(test_service)
    except OSError as exc:
        assert False, 'Stopping {} service raised an OSError'.format(test_service, exc)

    try:
        result = system_service_handler(test_service, 'start')
        assert result, '{} service could not be started'.format(test_service)
    except OSError as exc:
        assert False, 'Starting {} service raised an OSError'.format(test_service, exc)


if __name__ == '__main__':
    print('Example code for %s, %s' % (__intname__, __build__))
    test_system_service_handler()
