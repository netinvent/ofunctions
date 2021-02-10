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
__licence__ = 'BSD 3 Clause'
__version__ = '0.1.2'
__build__ = '2021020901'

import logging
import os
from time import sleep

from command_runner import command_runner

# Module pywin32
if os.name == 'nt':
    import win32serviceutil


logger = logging.getLogger(__intname__)


def system_service_handler(service: str, action: str) -> bool:
    """Handle Windows / Unix services
    Valid actions are start, stop, restart, status
    Returns True if action succeeded or service is running, False if service does not run
    """

    loops = 0  # Number of seconds elapsed since we started Windows service
    max_wait = 6  # Number of seconds we'll wait for Windows service to start

    msg_already_running = 'Service "{}" already running.'.format(service)
    msg_not_running = 'Service "{}" is not running.'.format(service)
    msg_action = 'Action {} for service "{}".'.format(action, service)
    msg_success = 'Action {} succeeded.'.format(service)
    msg_failure = 'Action {} failed.'.format(service)
    msg_too_long = 'Action {} took more than {} seconds and seems to have failed.'.format(action, max_wait)

    def nt_service_status(service):
        # Returns list. If second entry = 4, service is running
        # TODO: handle other service states than 4
        service_status = win32serviceutil.QueryServiceStatus(service)
        if service_status[1] == 4:
            return True
        return False

    if os.name == 'nt':
        is_running = nt_service_status(service)

        if action == "start":
            if is_running:
                logger.info(msg_already_running)
                return True
            logger.info(msg_action)
            try:
                # Does not provide return code, so we need to check manually
                win32serviceutil.StartService(service)
                while not is_running and loops < max_wait:
                    is_running = nt_service_status(service)
                    if is_running:
                        logger.info(msg_success)
                        return True
                    else:
                        sleep(2)
                        loops += 2
                logger.error(msg_too_long)
                raise Exception
            except Exception:
                logger.error(msg_failure)
                logger.debug('Trace', exc_info=True)
                raise OSError('Cannot start service')

        elif action == "stop":
            if not is_running:
                logger.info(msg_not_running)
                return True
            logger.info(msg_action)
            try:
                win32serviceutil.StopService(service)
                logger.info(msg_success)
                return True
            except Exception:
                logger.error(msg_failure)
                logger.debug('Trace:', exc_info=True)
                raise OSError('Cannot stop service')

        elif action == "restart":
            system_service_handler(service, 'stop')
            sleep(1)  # arbitrary sleep between
            system_service_handler(service, 'start')

        elif action == "status":
            return is_running

    else:
        # Using lsb service X command on Unix variants, hopefully the most portable

        # service_status = os.system("service " + service + " status > /dev/null 2>&1")

        # Valid exit code are 0 and 3 (because of systemctl using a service redirect)
        service_status, _ = command_runner('service "{}" status'.format(service))
        if service_status in [0, 3]:
            is_running = True
        else:
            is_running = False

        if action == "start":
            if is_running:
                logger.info(msg_already_running)
                return True
        if action == "stop":
            if not is_running:
                logger.info(msg_not_running)
                return True

        if action in ['start', 'stop']:
            logger.info(msg_action)
            result, output = command_runner('service "{}" {}}'.format(service, action))
            if result == 0:
                logger.info(msg_success)
                return True
            logger.error('Could not {} service, code [{}].'.format(action, result))
            logger.error('Output:\n{}'.format(output))
            raise OSError('Cannot {} service'.format(action))

        elif action == "restart":
            system_service_handler(service, 'stop')
            system_service_handler(service, 'start')

        elif action == "status":
            return is_running
