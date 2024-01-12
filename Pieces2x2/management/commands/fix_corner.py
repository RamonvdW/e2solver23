# -*- coding: utf-8 -*-

#  Copyright (c) 2023-2024 Ramon van der Winkel.
#  All rights reserved.
#  Licensed under BSD-3-Clause-Clear. See LICENSE file for details.

from django.core.management.base import BaseCommand
from Pieces2x2.models import TwoSide, TwoSideOptions, Piece2x2
from Pieces2x2.helpers import calc_segment
from WorkQueue.operations import propagate_segment_reduction


class Command(BaseCommand):

    help = "Fix one of the corners locations to one of the 4 corner pieces"

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
        self.reductions = {1: 0, 2: 0, 3: 0, 4: 0}     # [side_nr] = count

    def add_arguments(self, parser):
        # parser.add_argument('--verbose', action='store_true')
        parser.add_argument('processor', nargs=1, type=int, help='Processor number to use')
        parser.add_argument('loc', nargs=1, type=int, help='Location on board (1, 8, 57, 64)')
        parser.add_argument('base', nargs=1, type=int, help='Corner base piece number (1..4)')

    def _reverse_sides(self, options):
        return [self.twoside2reverse[two_side] for two_side in options]

    def _get_side_options(self, loc, side_nr):
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

        qset = TwoSideOptions.objects.filter(processor=self.processor, segment=segment, two_side=two_side)
        if qset.count() != 1:
            self.stderr.write('[ERROR] Cannot find segment=%s, two_side=%s' % (segment, two_side))
        else:
            self.stdout.write('[INFO] Reduction side%s: %s' % (side_nr, two_side))
            qset.delete()
            self.reductions[side_nr] += 1
            propagate_segment_reduction(self.processor, segment)

    def _reduce_loc_1(self, base_nr):
        loc = 1
        qset = (Piece2x2
                .objects
                .filter(side1=self.twoside_border,
                        side4=self.twoside_border,
                        nr1=base_nr))

        for side_nr in (2, 3):
            side_field = 'side%s' % side_nr
            segment = calc_segment(loc, side_nr)
            side_options = self._get_side_options(loc, side_nr)
            side_new = list(qset.distinct(side_field).values_list(side_field, flat=True))

            for side in side_options:
                if side not in side_new:
                    self._reduce(segment, side, side_nr)
            # for

    def _reduce_loc_8(self, base_nr):
        loc = 8
        qset = (Piece2x2
                .objects
                .filter(side1=self.twoside_border,
                        side2=self.twoside_border,
                        nr2=base_nr))

        for side_nr in (3, 4):
            side_field = 'side%s' % side_nr
            segment = calc_segment(loc, side_nr)
            side_options = self._get_side_options(loc, side_nr)
            side_new = list(qset.distinct(side_field).values_list(side_field, flat=True))

            for side in side_options:
                if side not in side_new:
                    self._reduce(segment, side, side_nr)
            # for

    def _reduce_loc_57(self, base_nr):
        loc = 57
        qset = (Piece2x2
                .objects
                .filter(side3=self.twoside_border,
                        side4=self.twoside_border,
                        nr3=base_nr))

        for side_nr in (1, 2):
            side_field = 'side%s' % side_nr
            segment = calc_segment(loc, side_nr)
            side_options = self._get_side_options(loc, side_nr)
            side_new = list(qset.distinct(side_field).values_list(side_field, flat=True))

            for side in side_options:
                if side not in side_new:
                    self._reduce(segment, side, side_nr)
            # for

    def _reduce_loc_64(self, base_nr):
        loc = 64
        qset = (Piece2x2
                .objects
                .filter(side2=self.twoside_border,
                        side3=self.twoside_border,
                        nr4=base_nr))

        for side_nr in (4, 1):
            side_field = 'side%s' % side_nr
            segment = calc_segment(loc, side_nr)
            side_options = self._get_side_options(loc, side_nr)
            side_new = list(qset.distinct(side_field).values_list(side_field, flat=True))

            for side in side_options:
                if side not in side_new:
                    self._reduce(segment, side, side_nr)
            # for

    def handle(self, *args, **options):

        loc = options['loc'][0]
        if loc not in (1, 8, 57, 64):
            self.stderr.write('[ERROR] Invalid location')
            return

        self.processor = options['processor'][0]

        corner_base = options['base'][0]

        self.stdout.write('[INFO] Processor=%s; Location: %s; Corner base piece number: %s' % (self.processor,
                                                                                               loc,
                                                                                               corner_base))

        if loc == 1:
            self._reduce_loc_1(corner_base)
        elif loc == 8:
            self._reduce_loc_8(corner_base)
        elif loc == 57:
            self._reduce_loc_57(corner_base)
        else:
            self._reduce_loc_64(corner_base)

        total = sum(self.reductions.values())
        if total == 0:
            self.stdout.write('[INFO] No reductions')
        else:
            self.stdout.write('[INFO] Reductions: %s, %s, %s, %s' % (self.reductions[1],
                                                                     self.reductions[2],
                                                                     self.reductions[3],
                                                                     self.reductions[4]))


# end of file
