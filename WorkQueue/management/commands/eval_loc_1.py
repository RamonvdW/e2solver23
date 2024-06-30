# -*- coding: utf-8 -*-

#  Copyright (c) 2023-2024 Ramon van der Winkel.
#  All rights reserved.
#  Licensed under BSD-3-Clause-Clear. See LICENSE file for details.

from django.utils import timezone
from django.core.management.base import BaseCommand
from Pieces2x2.models import TwoSide, TwoSideOptions, Piece2x2, EvalProgress
from Pieces2x2.helpers import calc_segment
from WorkQueue.models import ProcessorUsedPieces
from WorkQueue.operations import (propagate_segment_reduction, get_unused_for_locs, set_loc_used, request_eval_claims,
                                  set_dead_end)
import sys


class Command(BaseCommand):

    help = "Eval a possible reduction in TwoSideOptions for a single chosen location"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.twoside_border = TwoSide.objects.get(two_sides='XX').nr

        self.processor_nr = 0
        self.loc = 0
        self.reductions = {1: 0, 2: 0, 3: 0, 4: 0}     # [side_nr] = count
        self.bulk_reduce = dict()       # [segment] = [two_side, ..]

    def add_arguments(self, parser):
        # parser.add_argument('--verbose', action='store_true')
        parser.add_argument('processor', type=int, help='Processor number to use')
        parser.add_argument('loc', type=int, help='Location on board (1..64)')
        parser.add_argument('claimed', nargs='*', type=int, help="Base piece number claimed for other location")
        parser.add_argument('--nop', action='store_true', help='Do not propagate')

    def _get_unused(self, claimed):
        unused = get_unused_for_locs(self.processor_nr, [self.loc])

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

    def _get_side_options(self, side_nr):
        segment = calc_segment(self.loc, side_nr)
        options = (TwoSideOptions
                   .objects
                   .filter(processor=self.processor_nr,
                           segment=segment)
                   .values_list('two_side', flat=True))
        options = list(options)

        # print('segment %s options: %s' % (segment, repr(options)))
        return options

    def _reduce(self, segment, two_side, side_nr):
        try:
            self.bulk_reduce[segment].append(two_side)
        except KeyError:
            self.bulk_reduce[segment] = [two_side]

        self.reductions[side_nr] += 1

    def handle(self, *args, **options):

        self.loc = options['loc']
        if self.loc < 1 or self.loc > 64:
            self.stderr.write('[ERROR] Invalid location')
            return

        self.processor_nr = options['processor']
        nop = options['nop']

        self.stdout.write('[INFO] Location: %s; processor=%s' % (self.loc, self.processor_nr))

        try:
            used = ProcessorUsedPieces.objects.get(processor=self.processor_nr)
        except ProcessorUsedPieces.DoesNotExist:
            # not available
            pass
        else:
            loc_str = 'loc%s' % self.loc
            p2x2_nr = getattr(used, loc_str, 0)
            # self.stdout.write('[DEBUG] p2x2_nr for loc %s is %s' % (loc_str, p2x2_nr))
            if p2x2_nr > 0:
                self.stdout.write('[INFO] No work: location is already filled')
                return

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

        if self.loc == 36:
            qset = qset.filter(nr2=139)
        elif self.loc == 10:
            qset = qset.filter(nr1=208)
        elif self.loc == 15:
            qset = qset.filter(nr2=255)
        elif self.loc == 50:
            qset = qset.filter(nr3=181)
        elif self.loc == 55:
            qset = qset.filter(nr4=249)

        count = qset.count()

        if count == 0:
            # not filled in and no options left --> dead end
            self.stdout.write('[INFO] No solution possible for loc %s' % self.loc)

            self.stderr.write('[ERROR] Safety stop')
            set_dead_end(self.processor_nr)

            if EvalProgress.objects.filter(
                                    eval_size=1,
                                    eval_loc=self.loc,
                                    processor=self.processor_nr,
                                    segment=0,
                                    todo_count=0,
                                    left_count=0,
                                    solve_order="Safety stop!").count() == 0:
                EvalProgress(
                        eval_size=1,
                        eval_loc=self.loc,
                        processor=self.processor_nr,
                        segment=0,
                        todo_count=0,
                        left_count=0,
                        solve_order="Safety stop!",
                        updated=timezone.now()).save()

            sys.exit(1)

        self.stdout.write('[INFO] Number of Piece2x2: %s' % count)

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
                    self._reduce(segment, side, 3)
            # for

        if len(side4_new) != count4:
            # reduction
            segment = calc_segment(self.loc, 4)
            for side in side4_options:
                if side not in side4_new:
                    self._reduce(segment, side, 4)
            # for

        for segment, two_sides in self.bulk_reduce.items():
            qset2 = TwoSideOptions.objects.filter(processor=self.processor_nr, segment=segment, two_side__in=two_sides)
            qset2.delete()
        # for

        if not nop:
            for segment in self.bulk_reduce.keys():
                propagate_segment_reduction(self.processor_nr, segment)
            # for

        if count == 1:
            # only 1 solution left: set the base pieces as used
            self.stdout.write('[INFO] Single solution left for loc %s' % self.loc)
            p2x2 = qset.first()
            set_loc_used(self.processor_nr, self.loc, p2x2)
            return

        if count < 10:
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
            if not nop:
                request_eval_claims(self.processor_nr)


# end of file
