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

__intname__ = 'ofunctions.delayed_keyboardinterrupt'
__author__ = 'Orsiris de Jong'
__copyright__ = 'Copyright (C) 2019-2021 Orsiris de Jong'
__description__ = 'Intercept CTRL+C signal in your Python code'
__licence__ = 'BSD 3 Clause'
__version__ = '0.1.0'
__build__ = '2020032701'

import signal


class DelayedKeyboardInterrupt(object):
    """
    Allows to catch CTRL+C like
    with DelayedKeyboardInterrupt():
        whatever

    # Thanks to https://stackoverflow.com/a/21919644/2635443
    """

    def __enter__(self):
        self.signal_received = False
        self.old_handler = signal.signal(signal.SIGINT, self.handler)

    def handler(self, sig, frame):
        self.signal_received = (sig, frame)
        print('SIGINT received. Delaying KeyboardInterrupt.')

    def __exit__(self, _type, value, traceback):
        signal.signal(signal.SIGINT, self.old_handler)
        if self.signal_received:
            try:
                self.old_handler(*self.signal_received)
            except KeyboardInterrupt:
                raise KeyboardInterrupt('Now initiating delayed KeyboardInterrupt.')
