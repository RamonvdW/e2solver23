# -*- coding: utf-8 -*-

#  Copyright (c) 2023-2024 Ramon van der Winkel.
#  All rights reserved.
#  Licensed under BSD-3-Clause-Clear. See LICENSE file for details.

from django.core.management.base import BaseCommand
from Pieces2x2.models import TwoSideOptions, TwoSide, Piece2x2
from Pieces2x2.helpers import calc_segment
from Ring1.models import Ring1
from WorkQueue.models import ProcessorUsedPieces


class Command(BaseCommand):

    help = "Convert a Ring1 to a segments set"

    def add_arguments(self, parser):
        parser.add_argument('processor_base', nargs=1, type=int, help='Processor number to use as base')
        parser.add_argument('processor', nargs=1, type=int, help='New processor number')
        parser.add_argument('ring1_nr', nargs=1, type=int, help='Ring1 number')

    def handle(self, *args, **options):

        processor_base = options['processor_base'][0]
        processor = options['processor'][0]
        ring1_nr = options['ring1_nr'][0]

        if TwoSideOptions.objects.filter(processor=processor).count() > 0:
            self.stderr.write('[ERROR] Processor %s already exists' % processor)
            return

        try:
            ring1 = Ring1.objects.get(nr=ring1_nr)
        except Ring1.DoesNotExist:
            self.stderr.write('[ERROR] Ring1 with number %s not found' % ring1_nr)
            return

        self.stdout.write('[INFO] Creating processor %s from Ring1 %s' % (processor, ring1_nr))

        two2nr = dict()
        for two in TwoSide.objects.all():
            two2nr[two.two_sides] = two.nr
        # for
        twoside2reverse = dict()
        for two_sides, nr in two2nr.items():
            two_rev = two_sides[1] + two_sides[0]
            rev_nr = two2nr[two_rev]
            twoside2reverse[nr] = rev_nr
        # for

        bulk = list()
        for loc in range(1, 64+1):
            if loc not in (11, 18, 14, 23, 47, 54, 42, 51, 36):
                nr_str = 'nr%s' % loc
                p_nr = getattr(ring1, nr_str, None)

                if p_nr:
                    p2x2 = Piece2x2.objects.get(nr=p_nr)

                    options = TwoSideOptions(
                                    processor=processor,
                                    segment=calc_segment(loc, 1),
                                    two_side=p2x2.side1)
                    bulk.append(options)

                    options = TwoSideOptions(
                                    processor=processor,
                                    segment=calc_segment(loc, 2),
                                    two_side=p2x2.side2)
                    bulk.append(options)

                    options = TwoSideOptions(
                                    processor=processor,
                                    segment=calc_segment(loc, 3),
                                    two_side=twoside2reverse[p2x2.side3])
                    bulk.append(options)

                    options = TwoSideOptions(
                                    processor=processor,
                                    segment=calc_segment(loc, 4),
                                    two_side=twoside2reverse[p2x2.side4])
                    bulk.append(options)
        # for

        # remove dupes
        bulk2 = list()
        segments_done = list()
        for options in bulk:
            if options.segment not in segments_done:
                bulk2.append(options)
                segments_done.append(options.segment)
        # for

        # amend remaining segments from the base processor
        for base in TwoSideOptions.objects.filter(processor=processor_base).exclude(segment__in=segments_done):
            options = TwoSideOptions(processor=processor,
                                     segment=base.segment,
                                     two_side=base.two_side)
            bulk2.append(options)
        # for

        self.stdout.write('[INFO] Creating %s records' % len(bulk2))
        TwoSideOptions.objects.bulk_create(bulk2)

        self.stdout.write('[INFO] Creating ProcessorUsedPieces')
        ProcessorUsedPieces(processor=processor).save()


# end of file
