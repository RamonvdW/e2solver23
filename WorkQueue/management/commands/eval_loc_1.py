# -*- coding: utf-8 -*-

#  Copyright (c) 2023-2024 Ramon van der Winkel.
#  All rights reserved.
#  Licensed under BSD-3-Clause-Clear. See LICENSE file for details.

from django.utils import timezone
from django.core.management.base import BaseCommand
from Pieces2x2.models import TwoSide, TwoSideOptions, Piece2x2, EvalProgress
from Pieces2x2.helpers import calc_segment
from WorkQueue.operations import (propagate_segment_reduction, get_unused_for_locs, set_used, request_eval_claims,
                                  check_dead_end, set_dead_end)


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
        parser.add_argument('claimed', nargs='*', type=int, help="Base piece number claimed for other location")

    def _get_unused(self, claimed):
        unused = get_unused_for_locs(self.processor, [self.loc])

        if self.loc != 36 and 139 in unused:
            unused.remove(139)

        if self.loc != 10 and 208 in unused:
            unused.remove(208)

        if self.loc != 15 and 255 in unused:
            unused.remove(255)

        if self.loc != 50 and 181 in unused:
            unused.remove(181)

        if self.loc != 55 and 249 in unused:
            unused.remove(249)

        for claim in claimed:
            if claim in unused:
                unused.remove(claim)
        # for

        self.stdout.write('[INFO] %s base pieces in use or claimed' % (256 - len(unused)))
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

        unused = self._get_unused(options['claimed'])

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

        if self.loc == 10:
            qset = qset.filter(nr1=208)
        elif self.loc == 15:
            qset = qset.filter(nr2=255)
        elif self.loc == 36:
            qset = qset.filter(nr2=139)
        elif self.loc == 50:
            qset = qset.filter(nr3=181)
        elif self.loc == 55:
            qset = qset.filter(nr4=249)

        count = qset.count()

        self.stdout.write('[INFO] Number of Piece2x2: %s' % count)

        if count == 0:
            if len(side1_options) + len(side2_options) + len(side3_options) + len(side4_options) == 4:
                self.stdout.write('[INFO] Location seems filled')
                return

            self.stderr.write('[ERROR] Safety stop')
            set_dead_end(self.processor)

            if EvalProgress.objects.filter(
                                    eval_size=1,
                                    eval_loc=self.loc,
                                    processor=self.processor,
                                    segment=0,
                                    todo_count=0,
                                    left_count=0,
                                    solve_order="Safety stop!").count() == 0:
                EvalProgress(
                        eval_size=1,
                        eval_loc=self.loc,
                        processor=self.processor,
                        segment=0,
                        todo_count=0,
                        left_count=0,
                        solve_order="Safety stop!",
                        updated=timezone.now()).save()
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

        if count == 1:
            # only 1 solution left: set the base pieces as used
            self.stdout.write('[INFO] Single solution left for loc %s' % self.loc)
            p2x2 = qset.first()
            base_nrs = [p2x2.nr1, p2x2.nr2, p2x2.nr3, p2x2.nr4]
            set_used(self.processor, base_nrs)
            return

        if count < 5:
            for p2x2 in qset:
                print('[DEBUG] p2x2 nr %s has base nrs [%s, %s, %s, %s]' % (p2x2.nr,
                                                                            p2x2.nr1, p2x2.nr2, p2x2.nr3, p2x2.nr4))
            # for

        total = sum(self.reductions.values())
        if total == 0:
            self.stdout.write('[INFO] No reductions')
        else:
            self.stdout.write('[INFO] Reductions: %s, %s, %s, %s' % (self.reductions[1],
                                                                     self.reductions[2],
                                                                     self.reductions[3],
                                                                     self.reductions[4]))
            request_eval_claims(self.processor)


# end of file
