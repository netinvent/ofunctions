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

__intname__ = "ofunctions.logger_utils"
__author__ = "Orsiris de Jong"
__copyright__ = "Copyright (C) 2014-2022 Orsiris de Jong"
__description__ = "Shorthand for logger initialization, recording worst called loglevel and handling nice console output"
__licence__ = "BSD 3 Clause"
__version__ = "2.3.0"
__build__ = "2022110711"
__compat__ = "python2.7+"

import logging
import os
import sys
import tempfile
from logging.handlers import RotatingFileHandler

# python 2.7 compat fixes
try:
    from typing import Union, Tuple, Optional
except ImportError:
    pass

# Logging functions ########################################################

FORMATTER = "%(asctime)s :: %(levelname)s :: ##OPTINAL_STRING##%(message)s"


class FixPython2Logging(logging.Filter):
    def __init__(self):
        self._worst_level = logging.INFO
        if sys.version_info[0] < 3:
            # pylint: disable=E1003 (bad-super-call)
            super(logging.Filter, self).__init__()
        else:
            super().__init__()

    def filter(self, record):
        # type: (str) -> bool
        # Fix python2 unicodedecodeerrors when non unicode strings are sent to logger
        if sys.version_info[0] < 3:
            record.msg = safe_string_convert(record.msg)
        return True


class ContextFilterWorstLevel(logging.Filter):
    """
    This class records the worst loglevel that was called by logger
    Allows to change default logging output or record events
    """

    def __init__(self):
        self._worst_level = logging.INFO
        if sys.version_info[0] < 3:
            # pylint: disable=E1003 (bad-super-call)
            super(logging.Filter, self).__init__()
        else:
            super().__init__()

    @property
    def worst_level(self):
        """
        Returns worst log level called
        """
        return self._worst_level

    @worst_level.setter
    def worst_level(self, value):
        # type: (int) -> None
        if isinstance(value, int):
            self._worst_level = value

    def filter(self, record):
        # type: (str) -> bool
        """
        A filter can change the default log output
        This one simply records the worst log level called
        """
        # Examples
        # record.msg = f'{record.msg}'.encode('ascii', errors='backslashreplace')
        # When using this filter, something can be added to logging.Formatter like '%(something)s'
        # record.something = 'value'
        if record.levelno > self.worst_level:
            self.worst_level = record.levelno
        return True


def get_logger_formatter(formatter_insert=None):
    # type: (Optional[str]) -> logging.Formatter
    if formatter_insert:
        return logging.Formatter(FORMATTER.replace('##OPTINAL_STRING##', '{} :: '.format(formatter_insert)))
    else:
        return logging.Formatter(FORMATTER.replace('##OPTINAL_STRING##', ""))



def logger_get_console_handler(
    formatter_insert=None,
):
    # type: (Optional[str]) -> Union[logging.StreamHandler, None]
    """
    Returns a console handler that outputs as UTF-8 regardless of the platform
    """
    formatter = get_logger_formatter(formatter_insert)
    # When Nuitka compiled under Windows, calls to subshells are opened as cp850 / other system locale
    # This behavior makes logging popen output to stdout/stderr fail
    # Let's force stdout and stderr to always be utf-8
    if os.name == "nt":
        # https: // stackoverflow.com / a / 52372390 / 2635443
        try:
            sys.stdout.reconfigure(encoding="utf-8", errors="backslashreplace")
            sys.stderr.reconfigure(encoding="utf-8", errors="backslashreplace")
            # Alternative
            # import codecs
            # sys.stdout = codecs.getwriter('utf-8')(sys.stdout)
        except AttributeError:
            pass
            # print("Cannot force console encoding.")
            # Python2 does not have ssys.stdout.reconfigure
            # IPython interpreter does not know about sys.stdout.reconfigure function
            # Neither does it now detach or fileno()
            # sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf-8', errors='backslashreplace', buffering=1)
            # sys.stderr = open(sys.stderr.fileno(), mode='w', encoding='utf-8', errors='backslashreplace', buffering=1)

    try:
        console_handler = logging.StreamHandler(sys.stdout)
    except OSError as exc:
        print("Cannot log to stdout, trying stderr. Message %s" % exc)
        try:
            console_handler = logging.StreamHandler(sys.stderr)
            console_handler.setFormatter(formatter)
            return console_handler
        except OSError as exc:
            print("Cannot log to stderr neither. Message %s" % exc)
            return None
    else:
        console_handler.setFormatter(formatter)
        return console_handler


def logger_get_file_handler(log_file, formatter_insert=None):
    # type: (str, Optional[None]) -> Tuple[Union[RotatingFileHandler, None], Union[str, None]]
    """
    Returns a log file handler
    On failire, will return a temporary file log handler
    """
    formatter = get_logger_formatter(formatter_insert)
    err_output = None
    try:
        file_handler = RotatingFileHandler(
            log_file, mode="a", encoding="utf-8", maxBytes=1048576, backupCount=3
        )
    except (OSError, IOError) as exc:
        try:
            print(
                "Cannot create logfile. Trying to obtain temporary log file.\nMessage: %s"
                % exc
            )
            err_output = str(exc)
            temp_log_file = tempfile.gettempdir() + os.sep + __name__ + ".log"
            print("Trying temporary log file in " + temp_log_file)
            file_handler = RotatingFileHandler(
                temp_log_file,
                mode="a",
                encoding="utf-8",
                maxBytes=1048576,
                backupCount=1,
            )
            file_handler.setFormatter(formatter)
            err_output += "\nUsing [%s]" % temp_log_file
            return file_handler, err_output
        except OSError as exc:
            msg = (
                "Cannot create temporary log file either. Will not log to file. Message: %s"
                % exc
            )
            print(msg)
            return None, msg
    else:
        file_handler.setFormatter(formatter)
        return file_handler, err_output


def logger_get_logger(
    log_file=None,  # type: str
    temp_log_file=None,  # type: str
    console=True,  # type: bool
    debug=False,  # type: bool
    formatter_insert=None,  # type: str
):
    # type: (...) -> logging.Logger
    """
    Returns a logger instance, just as logger.getLogger(), configured for console and/or file
    """
    # If a name is given to getLogger, than modules can't log to the root logger
    _logger = logging.getLogger()

    # Remove earlier handlers if exist
    while _logger.handlers:
        _logger.handlers.pop()

    # Add context filter
    _logger.addFilter(FixPython2Logging())
    _logger.addFilter(ContextFilterWorstLevel())

    if debug:
        _logger.setLevel(logging.DEBUG)
    else:
        _logger.setLevel(logging.INFO)

    if console:
        console_handler = logger_get_console_handler(
            formatter_insert=formatter_insert
        )
        if console_handler:
            _logger.addHandler(console_handler)
    if log_file:
        file_handler, err_output = logger_get_file_handler(
            log_file, formatter_insert=formatter_insert
        )
        if file_handler:
            _logger.addHandler(file_handler)
            _logger.propagate = False
            if err_output is not None:
                print(err_output)
                _logger.warning(
                    'Failed to use log file "%s", %s.', log_file, err_output
                )
    if temp_log_file:
        if os.path.isfile(temp_log_file):
            try:
                os.remove(temp_log_file)
            except OSError:
                _logger.warning(
                    'Cannot remove temp log file "%s". Is another instance accessing the file ?',
                    temp_log_file,
                )
        file_handler, err_output = logger_get_file_handler(
            temp_log_file, formatter_insert=formatter_insert
        )
        if file_handler:
            _logger.addHandler(file_handler)
            _logger.propagate = False
            if err_output is not None:
                print(err_output)
                _logger.warning(
                    'Failed to use log file "%s", %s.', log_file, err_output
                )
    _logger.propagate = True
    return _logger


def safe_string_convert(string):
    """
    Allows to encode strings for hacky UTF-8 logging in python 2.7
    """
    try:
        return string.decode("utf8")
    except Exception:  # noqa
        try:
            return string.decode("unicode-escape")
        except Exception:  # noqa
            try:
                return string.decode("latin1")
            except Exception:  # noqa
                if sys.version_info[0] < 3:
                    # pylint: disable=E0602 (undefined-variable)
                    if isinstance(string, unicode):  # noqa
                        return string
                try:
                    return (
                        b"logger_utils: Cannot convert logged string. Passing it as binary blob: "
                        + bytes(string)
                    )
                except Exception:  # noqa
                    return string


def get_worst_logger_level(_logger):
    # type (logging.Logger) -> int
    """
    Return the worst log level called
    """
    for flt in _logger.filters:
        if isinstance(flt, ContextFilterWorstLevel):
            return flt.worst_level
    return 0
