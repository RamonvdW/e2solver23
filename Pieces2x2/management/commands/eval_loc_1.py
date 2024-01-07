# -*- coding: utf-8 -*-

#  Copyright (c) 2023-2024 Ramon van der Winkel.
#  All rights reserved.
#  Licensed under BSD-3-Clause-Clear. See LICENSE file for details.

from django.core.management.base import BaseCommand
from Pieces2x2.models import TwoSide, TwoSideOptions, Piece2x2
from Pieces2x2.helpers import calc_segment
from WorkQueue.operations import propagate_segment_reduction


class Command(BaseCommand):

    help = "Eval a possible reduction in TwoSideOptions for a single chosen location"

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
        self.loc = 0
        self.reductions = {1: 0, 2: 0, 3: 0, 4: 0}     # [side_nr] = count

    def add_arguments(self, parser):
        # parser.add_argument('--verbose', action='store_true')
        parser.add_argument('processor', nargs=1, type=int, help='Processor number to use')
        parser.add_argument('loc', nargs=1, type=int, help='Location on board (1..64)')

    def _get_unused(self):
        unused0 = list(range(1, 256+1))

        if self.loc != 36:
            unused0.remove(139)

        if self.loc != 10:
            unused0.remove(208)

        if self.loc != 15:
            unused0.remove(255)

        if self.loc != 50:
            unused0.remove(181)

        if self.loc != 55:
            unused0.remove(249)

        unused = unused0[:]

        # load all the segments
        seg2count = dict()
        for options in TwoSideOptions.objects.filter(processor=self.processor):
            try:
                seg2count[options.segment] += 1
            except KeyError:
                seg2count[options.segment] = 1
        # for

        # check how many Piece2x2 fit each location
        for loc in range(1, 64+1):
            seg1 = calc_segment(loc, 1)
            seg2 = calc_segment(loc, 2)
            seg3 = calc_segment(loc, 3)
            seg4 = calc_segment(loc, 4)

            count1 = seg2count[seg1]
            count2 = seg2count[seg2]
            count3 = seg2count[seg3]
            count4 = seg2count[seg4]

            if count1 == 1 and count2 == 1 and count3 == 1 and count4 == 1:
                # limited options on this location: get the Piece2x2
                side1 = TwoSideOptions.objects.get(processor=self.processor, segment=seg1).two_side
                side2 = TwoSideOptions.objects.get(processor=self.processor, segment=seg2).two_side
                side3 = TwoSideOptions.objects.get(processor=self.processor, segment=seg3).two_side
                side4 = TwoSideOptions.objects.get(processor=self.processor, segment=seg4).two_side

                side3 = self.twoside2reverse[side3]
                side4 = self.twoside2reverse[side4]

                nrs = dict()
                p2x2_count = 0
                for p2x2 in Piece2x2.objects.filter(side1=side1, side2=side2, side3=side3, side4=side4,
                                                    nr1__in=unused0, nr2__in=unused0, nr3__in=unused0, nr4__in=unused0):
                    p2x2_count += 1
                    for nr in (p2x2.nr1, p2x2.nr2, p2x2.nr3, p2x2.nr4):
                        try:
                            nrs[nr] += 1
                        except KeyError:
                            nrs[nr] = 1
                    # for
                # for
                for nr, nr_count in nrs.items():
                    if nr_count == p2x2_count:
                        unused.remove(nr)
                # for
        # for

        self.stdout.write('[INFO] %s base pieces in use' % (256 - len(unused)))
        return unused

    def _reverse_sides(self, options):
        return [self.twoside2reverse[two_side] for two_side in options]

    def _get_side_options(self, side_nr):
        segment = calc_segment(self.loc, side_nr)
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
        qset = TwoSideOptions.objects.filter(processor=self.processor, segment=segment, two_side=two_side)
        if qset.count() != 1:
            self.stderr.write('[ERROR] Cannot find segment=%s, two_side=%s' % (segment, two_side))
        else:
            self.stdout.write('[INFO] Reduction side%s: %s' % (side_nr, two_side))
            qset.delete()
            self.reductions[side_nr] += 1
            propagate_segment_reduction(self.processor, segment)

    def handle(self, *args, **options):

        self.loc = options['loc'][0]
        if self.loc < 1 or self.loc > 64:
            self.stderr.write('[ERROR] Invalid location')
            return

        self.processor = options['processor'][0]

        self.stdout.write('[INFO] Location: %s; processor=%s' % (self.loc, self.processor))

        unused = self._get_unused()

        side1_options = self._get_side_options(1)
        side2_options = self._get_side_options(2)
        side3_options = self._get_side_options(3)
        side4_options = self._get_side_options(4)

        count1 = len(side1_options)
        count2 = len(side2_options)
        count3 = len(side3_options)
        count4 = len(side4_options)

        self.stdout.write('[INFO] Side options: %s, %s, %s, %s' % (count1, count2, count3, count4))

        qset = (Piece2x2
                .objects
                .filter(side1__in=side1_options,
                        side2__in=side2_options,
                        side3__in=side3_options,
                        side4__in=side4_options,
                        nr1__in=unused,
                        nr2__in=unused,
                        nr3__in=unused,
                        nr4__in=unused))

        self.stdout.write('[INFO] Number of Piece2x2: %s' % qset.count())

        if qset.count() == 0:
            self.stderr.write('[ERROR] Safety stop')
            return

        side1_new = list(qset.distinct('side1').values_list('side1', flat=True))
        side2_new = list(qset.distinct('side2').values_list('side2', flat=True))
        side3_new = list(qset.distinct('side3').values_list('side3', flat=True))
        side4_new = list(qset.distinct('side4').values_list('side4', flat=True))

        if len(side1_new) != count1:
            # reduction
            segment = calc_segment(self.loc, 1)
            for side in side1_options:
                if side not in side1_new:
                    self._reduce(segment, side, 1)
            # for

        if len(side2_new) != count2:
            # reduction
            segment = calc_segment(self.loc, 2)
            for side in side2_options:
                if side not in side2_new:
                    self._reduce(segment, side, 2)
            # for

        if len(side3_new) != count3:
            # reduction
            segment = calc_segment(self.loc, 3)
            for side in side3_options:
                if side not in side3_new:
                    self._reduce(segment, self.twoside2reverse[side], 3)
            # for

        if len(side4_new) != count4:
            # reduction
            segment = calc_segment(self.loc, 4)
            for side in side4_options:
                if side not in side4_new:
                    self._reduce(segment, self.twoside2reverse[side], 4)
            # for

        total = sum(self.reductions.values())
        if total == 0:
            self.stdout.write('[INFO] No reductions')
        else:
            self.stdout.write('[INFO] Reductions: %s, %s, %s, %s' % (self.reductions[1],
                                                                     self.reductions[2],
                                                                     self.reductions[3],
                                                                     self.reductions[4]))


# end of file
