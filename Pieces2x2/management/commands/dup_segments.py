# -*- coding: utf-8 -*-

#  Copyright (c) 2023-2024 Ramon van der Winkel.
#  All rights reserved.
#  Licensed under BSD-3-Clause-Clear. See LICENSE file for details.

from django.core.management.base import BaseCommand
from Pieces2x2.models import TwoSideOptions
from WorkQueue.models import ProcessorUsedPieces
from WorkQueue.operations import used_note_add


class Command(BaseCommand):

    help = "Duplicate work (TwoSideOptions + ProcessorUsedPieces) from specific source to selected number"

    def add_arguments(self, parser):
        parser.add_argument('source', type=int, help='Processor number to copy from')
        parser.add_argument('processor', type=int, help='New processor number')

    def handle(self, *args, **options):

        processor = options['processor']

        if TwoSideOptions.objects.filter(processor=processor).count() > 0:
            self.stderr.write('[ERROR] Processor %s already exists' % processor)
            return

        source = options['source']
        count = TwoSideOptions.objects.filter(processor=source).count()
        if count == 0:
            self.stderr.write('[ERROR] Nothing to copy')
            return

        self.stdout.write('[INFO] Duplicating processor %s to %s' % (source, processor))

        bulk = []
        for options in TwoSideOptions.objects.filter(processor=source):
            option = TwoSideOptions(
                        processor=processor,
                        segment=options.segment,
                        two_side=options.two_side)
            bulk.append(option)
        # for

        self.stdout.write('[INFO] Creating %s records' % len(bulk))
        TwoSideOptions.objects.bulk_create(bulk)

        try:
            work = ProcessorUsedPieces.objects.get(processor=source)
        except ProcessorUsedPieces.DoesNotExist:
            self.stdout.write('[WARNING] Could not load used pieces for processor %s; creating new' % source)
            work = ProcessorUsedPieces()
        else:
            # force creation of a new record
            work.pk = None

        work.processor = processor
        work.created_from = source
        work.save()

        used_note_add(work.processor, 'Dup from %s' % source)


# end of file
