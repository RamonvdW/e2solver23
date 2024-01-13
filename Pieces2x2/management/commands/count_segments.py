# -*- coding: utf-8 -*-

#  Copyright (c) 2023-2024 Ramon van der Winkel.
#  All rights reserved.
#  Licensed under BSD-3-Clause-Clear. See LICENSE file for details.

from django.core.management.base import BaseCommand
from Pieces2x2.models import TwoSideOptions


class Command(BaseCommand):

    help = "Count the TwoSideOptions for a specific processor"

    def add_arguments(self, parser):
        parser.add_argument('processor', nargs=1, type=int, help='Processor number')

    def handle(self, *args, **options):

        processor = options['processor'][0]

        count = TwoSideOptions.objects.filter(processor=processor).count()
        self.stdout.write("%s" % count)


# end of file
