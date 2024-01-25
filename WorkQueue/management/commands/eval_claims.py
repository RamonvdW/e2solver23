# -*- coding: utf-8 -*-

#  Copyright (c) 2023-2024 Ramon van der Winkel.
#  All rights reserved.
#  Licensed under BSD-3-Clause-Clear. See LICENSE file for details.

from django.core.management.base import BaseCommand
from Pieces2x2.models import TwoSide, TwoSideOptions, Piece2x2
from Pieces2x2.helpers import calc_segment
from WorkQueue.models import ProcessorUsedPieces
from WorkQueue.operations import get_unused


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

    def _count_twoside(self):
        return TwoSideOptions.objects.filter(processor=self.processor).count()

    def _limit_base_pieces(self):
        used = ProcessorUsedPieces.objects.get(processor=self.processor)
        used.claimed_at_twoside_count = self._count_twoside()

        single_nrs = list()
        double_nrs = dict()
        for loc in range(1, 64+1):
            # see if this loc requires certain base pieces
            options1 = self._get_side_options(loc, 1)
            options2 = self._get_side_options(loc, 2)
            options3 = self._get_side_options(loc, 3)
            options4 = self._get_side_options(loc, 4)

            unused = self.unused[:]

            if loc != 36 and 139 in unused:
                unused.remove(139)

            if loc != 10 and 208 in unused:
                unused.remove(208)

            if loc != 15 and 255 in unused:
                unused.remove(255)

            if loc != 50 and 181 in unused:
                unused.remove(181)

            if loc != 55 and 249 in unused:
                unused.remove(249)

            qset = Piece2x2.objects.filter(side1__in=options1, side2__in=options2,
                                           side3__in=options3, side4__in=options4,
                                           nr1__in=unused, nr2__in=unused,
                                           nr3__in=unused, nr4__in=unused)

            if loc == 10:
                qset = qset.filter(nr1=208)
            elif loc == 15:
                qset = qset.filter(nr2=255)
            elif loc == 36:
                qset = qset.filter(nr2=139)
            elif loc == 50:
                qset = qset.filter(nr3=181)
            elif loc == 55:
                qset = qset.filter(nr4=249)

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

                for lp in (1, 2, 3, 4):
                    if len(p_nrs[lp]) == 1:
                        tup = (p_nrs[lp][0], loc)
                        single_nrs.append(tup)
                    if len(p_nrs[lp]) == 2:
                        tup = tuple(p_nrs[lp])
                        try:
                            double_nrs[tup].append(loc)
                        except KeyError:
                            double_nrs[tup] = [loc]
                # for
        # for

        claimed_nrs = list()
        single_nrs.sort()
        for nr, loc in single_nrs:
            self.stdout.write('[WARNING] Single claim: %s needs %s' % (loc, nr))
            claimed_nrs.append('%s:%s' % (nr, loc))
        # for
        claimed_nrs_single = ",".join(claimed_nrs)

        if used.claimed_nrs_single != claimed_nrs_single:
            count1 = used.claimed_nrs_single.count(':')
            count2 = claimed_nrs_single.count(':')
            self.stdout.write('[INFO] Singles claim changed from %s to %s nrs' % (count1, count2))

        used.claimed_nrs_single = claimed_nrs_single

        # TODO: double claim from one loc
        claimed_nrs = list()
        for tup, locs in double_nrs.items():
            if len(locs) > 1:
                locs_str = " and ".join([str(loc) for loc in locs])
                self.stdout.write('[WARNING] Double claim: %s need %s' % (locs_str, repr(tup)))
                for nr in tup:
                    claimed_nrs.append('%s:%s;%s' % (nr, locs[0], locs[1]))
        # for
        claimed_nrs_double = ",".join(claimed_nrs)

        if used.claimed_nrs_double != claimed_nrs_double:
            count1 = used.claimed_nrs_double.count(':')
            count2 = claimed_nrs_double.count(':')
            self.stdout.write('[INFO] Doubles claim changed from %s to %s nrs' % (count1, count2))

        used.save(update_fields=['claimed_nrs_single', 'claimed_nrs_double', 'claimed_at_twoside_count'])

    def handle(self, *args, **options):

        self.processor = options['processor'][0]

        self.stdout.write('[INFO] Processor=%s' % self.processor)

        self._load_unused()

        self._limit_base_pieces()


# end of file
