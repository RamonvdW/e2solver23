# -*- coding: utf-8 -*-

#  Copyright (c) 2023-2024 Ramon van der Winkel.
#  All rights reserved.
#  Licensed under BSD-3-Clause-Clear. See LICENSE file for details.

from django.core.management.base import BaseCommand
from Pieces2x2.models import TwoSideOptions
from WorkQueue.models import ProcessorUsedPieces


class Command(BaseCommand):

    help = "Duplicate work (TwoSideOptions + ProcessorUsedPieces) from specific source to next free number"

    def add_arguments(self, parser):
        parser.add_argument('source', type=int, help='Processor number to copy from')

    def handle(self, *args, **options):

        source = options['source']

        # automatically decide the next processor number
        last_proc = ProcessorUsedPieces.objects.order_by('processor').last()
        new_processor = last_proc.processor + 1

        # clean-up (just in case)
        TwoSideOptions.objects.filter(processor=new_processor).all().delete()

        # copy all the TwoSideOptions
        bulk = []
        for options in TwoSideOptions.objects.filter(processor=source):
            option = TwoSideOptions(
                        processor=new_processor,
                        segment=options.segment,
                        two_side=options.two_side)
            bulk.append(option)
        # for
        TwoSideOptions.objects.bulk_create(bulk)

        work = ProcessorUsedPieces.objects.get(processor=source)
        work.pk = None
        work.processor = new_processor
        work.created_from = source
        work.save()

        # output only 1 thing: the new processor number
        self.stdout.write(str(new_processor))


# end of file
