#!/bin/bash
# -*- coding: utf-8 -*-

#  Copyright (c) 2019-2023 Ramon van der Winkel.
#  All rights reserved.
#  Licensed under BSD-3-Clause-Clear. See LICENSE file for details.

# this line + shebang ensures python is taken from the user's PATH
# python sees this as a string and ignores it
# note: -u = unbuffered stdout/stderr
"exec" "python3" "-u" "$0" "$@"

from django.core.management import execute_from_command_line
import sys
import os

"""
    Django's command-line utility for administrative tasks.
"""


def main():
    """ Run administrative tasks. """

    try:

        try:
            os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'SiteMain.settings')
            execute_from_command_line(sys.argv)

        except (KeyboardInterrupt, SystemExit):  # pragma: no cover
            print('\nInterrupted!')
            sys.exit(3)  # allows test suite to detect test abort


    except BrokenPipeError:
        # Python flushes standard streams on exit; redirect remaining output
        # to devnull to avoid another BrokenPipeError at shutdown
        devnull = os.open(os.devnull, os.O_WRONLY)
        os.dup2(devnull, sys.stdout.fileno())
        sys.exit(1)         # Python exits with error code 1 on EPIPE



if __name__ == '__main__':
    main()
