# -*- coding: utf-8 -*-

#  Copyright (c) 2024 Ramon van der Winkel.
#  All rights reserved.
#  Licensed under BSD-3-Clause-Clear. See LICENSE file for details.

from django.core.management.base import BaseCommand
from Ring1.models import Ring1


class Command(BaseCommand):

    help = "Set the Ring1 is_processed flag"

    def add_arguments(self, parser):
        parser.add_argument('nr', type=int, help='Ring1 to set')
        parser.add_argument('--true', action='store_true', help='Set Ring1 status is_processed = True')

    def handle(self, *args, **options):
        if options['true']:
            nr = options['nr']
            try:
                ring = Ring1.objects.get(nr=nr)
            except Ring1.DoesNotExist:
                self.stdout.write('[ERROR] Cannot find Ring1 with nr=%s' % nr)
            else:
                ring.is_processed = True
                ring.save(update_fields=['is_processed'])


# end of file
