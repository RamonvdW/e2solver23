# -*- coding: utf-8 -*-

#  Copyright (c) 2024 Ramon van der Winkel.
#  All rights reserved.
#  Licensed under BSD-3-Clause-Clear. See LICENSE file for details.

from django.core.management.base import BaseCommand
from WorkQueue.models import Work


class Command(BaseCommand):

    help = "Reduce prio for work orders"

    def add_arguments(self, parser):
        parser.add_argument('processor', nargs=1, type=int, help='Processor number to reduce')

    def handle(self, *args, **options):

        processor = options['processor'][0]

        count = 0
        for work in Work.objects.filter(done=False, processor=processor):
            work.priority += 1      # higher number is lower prio
            work.save(update_fields=['priority'])
            count += 1
        # for

        self.stdout.write('[INFO] Reduce priority of %s jobs for processor %s' % (count, processor))

# end of file
