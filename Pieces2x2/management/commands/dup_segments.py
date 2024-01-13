# -*- coding: utf-8 -*-

#  Copyright (c) 2023-2024 Ramon van der Winkel.
#  All rights reserved.
#  Licensed under BSD-3-Clause-Clear. See LICENSE file for details.

from django.core.management.base import BaseCommand
from Pieces2x2.models import TwoSideOptions
from WorkQueue.models import ProcessorUsedPieces


class Command(BaseCommand):

    help = "Duplicate the latest TwoSideOptions"

    def add_arguments(self, parser):
        parser.add_argument('processor', nargs=1, type=int, help='New processor number')

    def handle(self, *args, **options):

        processor = options['processor'][0]

        if TwoSideOptions.objects.filter(processor=processor).count() > 0:
            self.stderr.write('[ERROR] Processor %s already exists' % processor)
            return

        last_rec = TwoSideOptions.objects.distinct('processor').order_by('processor').last()
        if not last_rec:
            self.stderr.write('[ERROR] Nothing to duplicate')
            return

        max_processor = last_rec.processor
        self.stdout.write('[INFO] Duplicating processor %s to %s' % (max_processor, processor))

        bulk = list()
        for options in TwoSideOptions.objects.filter(processor=max_processor):
            option = TwoSideOptions(
                        processor=processor,
                        segment=options.segment,
                        two_side=options.two_side)
            bulk.append(option)
        # for

        self.stdout.write('[INFO] Creating %s records' % len(bulk))
        TwoSideOptions.objects.bulk_create(bulk)

        ProcessorUsedPieces(processor=processor).save()


# end of file
