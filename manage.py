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
    """Run administrative tasks."""

    try:

        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'SiteMain.settings')
        execute_from_command_line(sys.argv)

    except (KeyboardInterrupt, SystemExit):       # pragma: no cover
        print('\nInterrupted!')
        sys.exit(3)                 # allows test suite to detect test abort


if __name__ == '__main__':
    main()
