# -*- coding: utf-8 -*-

#  Copyright (c) 2023 Ramon van der Winkel.
#  All rights reserved.
#  Licensed under BSD-3-Clause-Clear. See LICENSE file for details.

from django.core.management.base import BaseCommand
from Pieces2x2.models import TwoSideOptions


class Command(BaseCommand):

    help = "Duplicate the latest TwoSideOptions"

    def add_arguments(self, parser):
        parser.add_argument('processor', nargs=1, type=int, help='New processor number')

    def handle(self, *args, **options):

        processor = options['processor'][0]

        qset = TwoSideOptions.objects.filter(processor=processor)
        count = qset.count()

        if count == 0:
            self.stderr.write('[ERROR] Processor %s not found' % processor)
        else:
            self.stdout.write('[INFO] Deleting %s records' % count)
            qset.delete()

# end of file
