#! /usr/bin/env python
#  -*- coding: utf-8 -*-
#
# This file is part of ofunctions package

"""
servce_control allows to interact with windows / unix services

Versioning semantics:
    Major version: backward compatibility breaking changes
    Minor version: New functionality
    Patch version: Backwards compatible bug fixes

"""

__intname__ = 'ofunctions.service_control'
__author__ = 'Orsiris de Jong'
__copyright__ = 'Copyright (C) 2014-2021 Orsiris de Jong'
__description__ = 'Windows & Linux service control functions'
__licence__ = 'BSD 3 Clause'
__version__ = '0.2.0'
__build__ = '2021052601'

import logging
import os
from time import sleep

from command_runner import command_runner

# Module pywin32
if os.name == 'nt':
    import win32serviceutil


logger = logging.getLogger(__intname__)


def nt_service_status(service: str) -> bool:
    """
    #  win32serviceutil.QueryServiceStatus(service) returns a list. If second entry = 4, service is running
    # TODO: handle other service states than 4
    """
    service_status = win32serviceutil.QueryServiceStatus(service)
    if service_status[1] == 4:
        return True
    return False


def unix_service_status(service: str) -> bool:
    """
    Handle unix service using standard lsb commands
    Valid exit code are 0 and 3 (because of systemctl using a service redirect)
    """
    service_status, _ = command_runner('service "{}" status'.format(service), timeout=15)
    if service_status in [0, 3]:
        return True
    return False


def nt_service_action(service: str, action: str) -> bool:
    """
    Handle windows service
    """
    loops = 0  # Number of seconds elapsed since we started Windows service
    max_wait = 15  # Number of seconds we'll wait for Windows service to start

    is_running = nt_service_status(service)

    if action == 'start':
        try:
            win32serviceutil.StartService(service)
            while not is_running and loops < max_wait:
                is_running = nt_service_status(service)
                if is_running:
                    return True
                else:
                    sleep(2)
                    loops += 2
            logger.warning('Starting service {} took longer than {} and may have failed'.format(service, max_wait))
        except Exception:
            logger.debug('Trace:', exc_info=True)
        return False

    if action == 'stop':
        try:
            win32serviceutil.StopService(service)
            return True
        except Exception:
            logger.debug('Trace:', exc_info=True)
        return False


def unix_service_action(service: str, action: str) -> bool:
    """
    Using lsb service X command on Unix variants, hopefully the most portable
    """

    if action in ['start', 'stop']:
        result, output = command_runner('service "{}" {}}'.format(service, action))
        if result == 0:
            return True
        logger.error('Could not {} service, code [{}].'.format(action, result))
        logger.error('Output:\n{}'.format(output))
    return False


def system_service_handler(service: str, action: str) -> bool:
    """
    Handle Windows / Unix services
    Valid actions are start, stop, restart, status
    Returns True if action succeeded or service is running, False if service does not run
    """

    os_name = os.name
    if os_name == 'nt':
        is_running = nt_service_status(service)
    else:
        is_running = unix_service_status(service)

    if action in ['start', 'stop']:
        if action == 'start' and is_running:
            logger.info('Service {} already running.'.format(service))
            return True
        if action == 'stop' and not is_running:
            logger.info('Service {} is not running.'.format(service))
            return True
        logger.info('Action {} for service {}.'.format(action, service))
        if os_name == 'nt':
            result = nt_service_action(service, action)
        else:
            result = unix_service_action(service, action)

        if result:
            logger.info('Action {} succeeded.'.format(service))
            return True

        logger.error('Action {} failed.'.format(service))
        raise OSError('Cannot {} service {}'.format(action, service))

    elif action == "restart":
        system_service_handler(service, 'stop')
        sleep(1)  # arbitrary sleep between stop and start actions
        return system_service_handler(service, 'start')

    elif action == "status":
        return is_running


