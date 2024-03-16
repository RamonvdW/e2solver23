# -*- coding: utf-8 -*-

#  Copyright (c) 2023-2024 Ramon van der Winkel.
#  All rights reserved.
#  Licensed under BSD-3-Clause-Clear. See LICENSE file for details.

from django.core.management.base import BaseCommand
from Pieces2x2.models import TwoSide, TwoSideOptions, Piece2x2
from Pieces2x2.helpers import calc_segment
from WorkQueue.models import ProcessorUsedPieces
from Ring1.models import Ring1


class Command(BaseCommand):

    help = "Load progress from a ring1"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.twoside_border = TwoSide.objects.get(two_sides='XX').nr

        two2nr = dict()
        for two in TwoSide.objects.all():
            two2nr[two.two_sides] = two.nr
        # for
        self.twoside2reverse = dict()
        for two_sides, nr in two2nr.items():
            two_rev = two_sides[1] + two_sides[0]
            rev_nr = two2nr[two_rev]
            self.twoside2reverse[nr] = rev_nr
        # for

        self.processor = 0
        self.do_commit = False
        self.bulk_reduce = dict()       # [segment] = [two_side, ..]

    def add_arguments(self, parser):
        parser.add_argument('nr', type=int, help='Ring1 to load')
        parser.add_argument('processor', type=int, help='Into which processor to load')

    def _reverse_sides(self, options):
        return [self.twoside2reverse[two_side] for two_side in options]

    def _get_loc_side_options(self, loc, side_nr):
        segment = calc_segment(loc, side_nr)
        options = (TwoSideOptions
                   .objects
                   .filter(processor=self.processor,
                           segment=segment)
                   .values_list('two_side', flat=True))
        options = list(options)

        if side_nr >= 3:
            # sides 3 and 4 need to be reversed
            options = self._reverse_sides(options)

        # print('segment %s options: %s' % (segment, repr(options)))
        return options

    def _reduce(self, segment, two_side, side_nr):
        if side_nr in (3, 4):
            two_side = self.twoside2reverse[two_side]

        try:
            self.bulk_reduce[segment].append(two_side)
        except KeyError:
            self.bulk_reduce[segment] = [two_side]

        return

    def handle(self, *args, **options):

        nr = options['nr']
        self.processor = options['processor']
        self.stdout.write('[INFO] Loading ring1 %s into processor %s' % (nr, self.processor))

        try:
            ring1 = Ring1.objects.get(nr=nr)
        except Ring1.DoesNotExist:
            self.stderr.write('[ERROR] Ring1 not found')
            return

        try:
            processor = ProcessorUsedPieces.objects.get(processor=self.processor)
        except ProcessorUsedPieces.DoesNotExist:
            self.stderr.write('[ERROR] Processor not found')
            return

        locs = (1, 2, 3, 4, 5, 6, 7, 8,
                9, 10, 11, 14, 15, 16,
                17, 18, 23, 24,
                25, 32,
                33, 40,
                41, 42, 47, 48,
                49, 50, 51, 54, 55, 56,
                57, 58, 59, 60, 61, 62, 63, 64)

        for loc in locs:

            field_str = 'nr%s' % loc
            p2x2_nr = getattr(ring1, field_str)
            # print('loc %s ring1 %s = %s' % (loc, field_str, p2x2_nr))
            if p2x2_nr > 0:

                field_str = 'loc%s' % loc
                setattr(processor, field_str, p2x2_nr)
                p2x2 = Piece2x2.objects.get(nr=p2x2_nr)

                for base_nr in (p2x2.nr1, p2x2.nr2, p2x2.nr3, p2x2.nr4):
                    field_str = 'nr%s' % base_nr
                    setattr(processor, field_str, True)
                # for

                # reduce the segment options
                for side_nr in (1, 2, 3, 4):
                    segment = calc_segment(loc, side_nr)
                    # self.stdout.write('[INFO] Side %s is segment %s' % (side_nr, segment))

                    side_options = self._get_loc_side_options(loc, side_nr)  # gets reversed for side 3 and 4

                    side_field = 'side%s' % side_nr
                    side_new = getattr(p2x2, side_field, self.twoside_border)

                    for side in side_options:
                        if side != side_new:
                            self._reduce(segment, side, side_nr)  # reverses back for side 3 and 4
                    # for
                # for

        # for

        processor.from_ring1 = ring1.nr
        processor.save()

        for segment, two_sides in self.bulk_reduce.items():
            qset = TwoSideOptions.objects.filter(processor=self.processor, segment=segment, two_side__in=two_sides)
            qset.delete()
        # for


# end of file
