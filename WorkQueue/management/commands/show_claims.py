# -*- coding: utf-8 -*-

#  Copyright (c) 2023-2024 Ramon van der Winkel.
#  All rights reserved.
#  Licensed under BSD-3-Clause-Clear. See LICENSE file for details.

from django.core.management.base import BaseCommand
from Pieces2x2.models import TwoSide, TwoSideOptions, Piece2x2
from Pieces2x2.helpers import calc_segment
from WorkQueue.operations import propagate_segment_reduction, set_used, get_unused


class Command(BaseCommand):

    help = "Show the base piece claims for locations with limited options"

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
        self.unused = list()

    def add_arguments(self, parser):
        # parser.add_argument('--verbose', action='store_true')
        parser.add_argument('processor', nargs=1, type=int, help='Processor number to use')

    def _reverse_sides(self, options):
        return [self.twoside2reverse[two_side] for two_side in options]

    def _load_unused(self):
        self.unused = get_unused(self.processor)
        self.stdout.write('[INFO] %s base pieces in use' % (256 - len(self.unused)))

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

    def _limit_base_pieces(self):
        for loc in range(1, 64+1):
            # see if this loc requires certain base pieces
            options1 = self._get_side_options(loc, 1)
            options2 = self._get_side_options(loc, 2)
            options3 = self._get_side_options(loc, 3)
            options4 = self._get_side_options(loc, 4)

            qset = Piece2x2.objects.filter(side1__in=options1, side2__in=options2,
                                           side3__in=options3, side4__in=options4,
                                           nr1__in=self.unused, nr2__in=self.unused,
                                           nr3__in=self.unused, nr4__in=self.unused)

            if 1 < qset.count() < 1000:
                self.stdout.write('[INFO] Checking base piece claims on loc %s' % loc)

                p_nrs = {1: [], 2: [], 3: [], 4: []}
                for p2x2 in qset.all():
                    if p2x2.nr1 not in p_nrs[1]:
                        p_nrs[1].append(p2x2.nr1)
                    if p2x2.nr2 not in p_nrs[2]:
                        p_nrs[2].append(p2x2.nr2)
                    if p2x2.nr3 not in p_nrs[3]:
                        p_nrs[3].append(p2x2.nr3)
                    if p2x2.nr4 not in p_nrs[4]:
                        p_nrs[4].append(p2x2.nr4)
                # for

                if len(p_nrs[1]) <= 3:
                    self.stdout.write('[INFO] Loc %s requires base %s on nr1' % (loc, repr(p_nrs[1])))
                if len(p_nrs[2]) <= 3:
                    self.stdout.write('[INFO] Loc %s requires base %s on nr2' % (loc, repr(p_nrs[2])))
                if len(p_nrs[3]) <= 3:
                    self.stdout.write('[INFO] Loc %s requires base %s on nr3' % (loc, repr(p_nrs[3])))
                if len(p_nrs[4]) <= 3:
                    self.stdout.write('[INFO] Loc %s requires base %s on nr4' % (loc, repr(p_nrs[4])))
        # for

    def handle(self, *args, **options):

        self.processor = options['processor'][0]

        self.stdout.write('[INFO] Processor=%s' % self.processor)

        self._load_unused()

        self._limit_base_pieces()


# end of file
