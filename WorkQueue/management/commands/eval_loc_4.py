# -*- coding: utf-8 -*-

#  Copyright (c) 2023-2024 Ramon van der Winkel.
#  All rights reserved.
#  Licensed under BSD-3-Clause-Clear. See LICENSE file for details.

from django.utils import timezone
from django.core.management.base import BaseCommand
from Pieces2x2.models import TwoSide, TwoSideOptions, Piece2x2, EvalProgress
from Pieces2x2.helpers import calc_segment
from WorkQueue.operations import propagate_segment_reduction, get_unused_for_locs, check_dead_end
import time


class Command(BaseCommand):

    help = "Eval a possible reduction in TwoSideOptions for a square of 4 locations"

    """
              s0          s1
            +----+      +----+
        s2  | p0 |  s3  | p1 |  s4
            +----+      +----+
              s5          s6
            +----+      +----+
        s7  | p2 |  s8  | p3 |  s9
            +----+      +----+
             s10         s11
    """

    MAX_SECONDS_SEARCH = 15 * 60    # 15 minutes

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.twoside_border = TwoSide.objects.get(two_sides='XX').nr

        self.processor = 0
        self.locs = (0, 0, 0, 0)        # p0..p3
        self.side_options = ([], [], [], [], [], [], [], [], [], [], [], [])        # s0..s11
        self.variation = 99

        self.reductions = 0
        self.unused0 = []
        self.progress = None
        self.do_commit = True

        self._sides5_seen = []
        self._sides6_seen = []
        self._sides8_seen = []

        self.nop = False

    def add_arguments(self, parser):
        parser.add_argument('processor', type=int, help='Processor number to use')
        parser.add_argument('loc', type=int, help='Top-left location on the board (1..55)')
        parser.add_argument('--nop', action='store_true', help='Do not propagate')
        parser.add_argument('--dryrun', action='store_true')

    def _get_unused(self):
        unused = get_unused_for_locs(self.processor, self.locs)

        if 36 not in self.locs and 139 in unused:
            unused.remove(139)

        # if 10 not in self.locs and 208 in unused:
        #     unused.remove(208)
        #
        # if 15 not in self.locs and 255 in unused:
        #     unused.remove(255)
        #
        # if 50 not in self.locs and 181 in unused:
        #     unused.remove(181)
        #
        # if 55 not in self.locs and 249 in unused:
        #     unused.remove(249)

        self.stdout.write('[INFO] %s base pieces in use' % (256 - len(unused)))
        return unused

    def _get_loc_side_options(self, loc, side_nr):
        segment = calc_segment(loc, side_nr)
        options = (TwoSideOptions
                   .objects
                   .filter(processor=self.processor,
                           segment=segment)
                   .values_list('two_side', flat=True))
        options = list(options)
        # self.stdout.write('[DEBUG] Segment %s has %s options' % (segment, len(options)))
        return options

    def _get_side_options(self):
        """
                  s0          s1
                +----+      +----+
            s2  | p0 |  s3  | p1 |  s4
                +----+      +----+
                  s5          s6
                +----+      +----+
            s7  | p2 |  s8  | p3 |  s9
                +----+      +----+
                 s10         s11
        """
        s0 = self._get_loc_side_options(self.locs[0], 1)
        s1 = self._get_loc_side_options(self.locs[1], 1)
        s2 = self._get_loc_side_options(self.locs[0], 4)
        s3 = self._get_loc_side_options(self.locs[0], 2)
        s4 = self._get_loc_side_options(self.locs[1], 2)
        s5 = self._get_loc_side_options(self.locs[2], 1)
        s6 = self._get_loc_side_options(self.locs[3], 1)
        s7 = self._get_loc_side_options(self.locs[2], 4)
        s8 = self._get_loc_side_options(self.locs[2], 2)
        s9 = self._get_loc_side_options(self.locs[3], 2)
        s10 = self._get_loc_side_options(self.locs[2], 3)
        s11 = self._get_loc_side_options(self.locs[3], 3)

        self.side_options = [s0, s1, s2, s3, s4, s5, s6, s7, s8, s9, s10, s11]

        self.variation = sum([sum(options) for options in self.side_options])
        self.stdout.write('[INFO] Variation is %s' % self.variation)

    def _limit_work(self, options):
        if len(options) >= 250:
            # 250..289 --> reduce to 1/6 = 33..48
            start_idx = self.variation % 6          # cause variation
            options = options[start_idx::6]         # keep every 6th

        elif len(options) >= 200:
            # 200..249 --> reduce to 1/5 = 40..49
            start_idx = self.variation % 5          # cause variation
            options = options[start_idx::5]         # keep every 5th

        elif len(options) >= 150:
            # 150..199 --> reduce to 1/4 = 37..49
            start_idx = self.variation % 4          # cause variation
            options = options[start_idx::4]         # keep every 3th

        elif len(options) >= 100:
            # 100..149 --> reduce to 1/3 = 33..49
            start_idx = self.variation % 3          # cause variation
            options = options[start_idx::3]         # keep every 2nd

        elif len(options) >= 50:
            # 50..99 --> reduce to 1/2 = 25..49
            start_idx = self.variation % 2          # cause variation
            options = options[start_idx::2]         # keep every 2nd

        return options

    @staticmethod
    def _iter(unused1, options_side1, options_side2, options_side3, options_side4):
        if len(options_side1) == 1 and len(options_side2) == 1 and len(options_side3) == 1 and len(options_side4) == 1:
            # special case: this location is already filled, so it can be skipped
            p2x2 = Piece2x2(nr=0,
                            nr1=0, nr2=0, nr3=0, nr4=0,
                            side1=options_side1[0],
                            side2=options_side2[0],
                            side3=options_side3[0],
                            side4=options_side4[0])
            yield p2x2, unused1
            return

        for p in (Piece2x2
                  .objects
                  .filter(side1__in=options_side1,
                          side2__in=options_side2,
                          side3__in=options_side3,
                          side4__in=options_side4,
                          nr1__in=unused1,
                          nr2__in=unused1,
                          nr3__in=unused1,
                          nr4__in=unused1)
                  .iterator(chunk_size=1000)):
            unused2 = unused1[:]
            unused2.remove(p.nr1)
            unused2.remove(p.nr2)
            unused2.remove(p.nr3)
            unused2.remove(p.nr4)
            yield p, unused2
        # for

    def _reduce(self, segment, two_side):
        qset = TwoSideOptions.objects.filter(processor=self.processor, segment=segment, two_side=two_side)
        if qset.count() == 1:
            self.stdout.write('[INFO] Reduction segment %s: %s' % (segment, two_side))
            if self.do_commit:
                qset.delete()
            self.reductions += 1
            if not self.nop:
                propagate_segment_reduction(self.processor, segment)
        # else: most likely deleted by parallel operation

    def _reduce_s3(self):
        """
                  s0          s1
                +----+      +----+
            s2  | p0 |  s3  | p1 |  s4
                +----+      +----+
                  s5          s6
                +----+      +----+
            s7  | p2 |  s8  | p3 |  s9
                +----+      +----+
                 s10         s11
        """
        segment = calc_segment(self.locs[0], 2)
        sides = self.side_options[3]
        original_todo = len(sides)
        sides = self._limit_work(sides)
        todo = len(sides)
        # if todo > self.segment_limit:
        #     return

        self.progress.segment = segment
        self.progress.todo_count = todo
        self.progress.left_count = todo
        self.progress.save(update_fields=['segment', 'todo_count', 'left_count'])

        self.stdout.write('[INFO] Checking %s of %s options in segment %s' % (todo, original_todo, segment))
        for side in sides:
            if check_dead_end(self.processor):
                return

            self.progress.left_count -= 1
            self.progress.updated = timezone.now()
            self.progress.save(update_fields=['left_count', 'updated'])

            deadline = time.monotonic() + self.MAX_SECONDS_SEARCH

            p0_exp_s2 = side
            p1_exp_s4 = side
            found = False
            for p0, unused1 in self._iter(self.unused0,
                                          self.side_options[0],
                                          [p0_exp_s2],
                                          self.side_options[5],
                                          self.side_options[2]):
                p2_exp_s1 = p0.side3

                for p1, unused2 in self._iter(unused1,
                                              self.side_options[1],
                                              self.side_options[4],
                                              self.side_options[6],
                                              [p1_exp_s4]):
                    p3_exp_s1 = p1.side3

                    for p2, unused3 in self._iter(unused2,
                                                  [p2_exp_s1],
                                                  self.side_options[8],
                                                  self.side_options[10],
                                                  self.side_options[7]):
                        p3_exp_s4 = p2.side2

                        for p3, _ in self._iter(unused3,
                                                [p3_exp_s1],
                                                self.side_options[9],
                                                self.side_options[11],
                                                [p3_exp_s4]):
                            # found a combi of p0..p3
                            found = True
                            # avoid repeating
                            self._sides5_seen.append(p2.side1)
                            self._sides6_seen.append(p3.side1)
                            self._sides8_seen.append(p2.side2)
                            break
                        # for

                        if time.monotonic() > deadline:
                            found = True

                        if found:
                            break
                    # for
                    if found:
                        break
                # for
                if found:
                    break
            # for

            if not found:
                self._reduce(segment, side)
                # built up history is no longer valid
                self._sides5_seen = []
                self._sides6_seen = []
                self._sides8_seen = []

            todo -= 1
            self.stdout.write('[INFO] Left: %s/%s' % (todo, len(sides)))
        # for

    def _reduce_s5(self):
        """
                  s0          s1
                +----+      +----+
            s2  | p0 |  s3  | p1 |  s4
                +----+      +----+
                  s5          s6
                +----+      +----+
            s7  | p2 |  s8  | p3 |  s9
                +----+      +----+
                 s10         s11
        """
        segment = calc_segment(self.locs[0], 3)
        sides = self.side_options[5]
        original_todo = len(sides)
        sides = self._limit_work(sides)
        todo = len(sides)
        # if todo - len(self._sides5_seen) > self.segment_limit:
        #     return

        self.progress.segment = segment
        self.progress.todo_count = todo
        self.progress.left_count = todo
        self.progress.save(update_fields=['segment', 'todo_count', 'left_count'])

        self.stdout.write('[INFO] Checking %s of %s options in segment %s' % (todo, original_todo, segment))
        for side in sides:
            if side in self._sides5_seen:
                continue

            if check_dead_end(self.processor):
                return

            self.progress.left_count -= 1
            self.progress.updated = timezone.now()
            self.progress.save(update_fields=['left_count', 'updated'])

            deadline = time.monotonic() + self.MAX_SECONDS_SEARCH

            p0_exp_s3 = side
            p2_exp_s1 = side
            found = False
            for p0, unused1 in self._iter(self.unused0,
                                          self.side_options[0],
                                          self.side_options[3],
                                          [p0_exp_s3],
                                          self.side_options[2]):
                p1_exp_s4 = p0.side2

                for p2, unused2 in self._iter(unused1,
                                              [p2_exp_s1],
                                              self.side_options[8],
                                              self.side_options[10],
                                              self.side_options[7]):
                    p3_exp_s4 = p2.side2

                    for p1, unused3 in self._iter(unused2,
                                                  self.side_options[1],
                                                  self.side_options[4],
                                                  self.side_options[6],
                                                  [p1_exp_s4]):
                        p3_exp_s1 = p1.side3

                        for p3, _ in self._iter(unused3,
                                                [p3_exp_s1],
                                                self.side_options[9],
                                                self.side_options[11],
                                                [p3_exp_s4]):
                            # found a combi of p0..p3
                            found = True
                            # avoid repeating
                            self._sides6_seen.append(p3.side1)
                            self._sides8_seen.append(p2.side2)
                            break
                        # for

                        if time.monotonic() > deadline:
                            found = True

                        if found:
                            break
                    # for
                    if found:
                        break
                # for
                if found:
                    break
            # for

            if not found:
                self._reduce(segment, side)
                # built up history is no longer valid
                self._sides6_seen = []
                self._sides8_seen = []

            todo -= 1
            self.stdout.write('[INFO] Left: %s/%s' % (todo, len(sides)))
        # for

    def _reduce_s6(self):
        """
                  s0          s1
                +----+      +----+
            s2  | p0 |  s3  | p1 |  s4
                +----+      +----+
                  s5          s6
                +----+      +----+
            s7  | p2 |  s8  | p3 |  s9
                +----+      +----+
                 s10         s11
        """
        segment = calc_segment(self.locs[1], 3)
        sides = self.side_options[6]
        original_todo = len(sides)
        sides = self._limit_work(sides)
        todo = len(sides)
        # if todo - len(self._sides6_seen) > self.segment_limit:
        #     return

        self.progress.segment = segment
        self.progress.todo_count = todo
        self.progress.left_count = todo
        self.progress.save(update_fields=['segment', 'todo_count', 'left_count'])

        self.stdout.write('[INFO] Checking %s of %s options in segment %s' % (todo, original_todo, segment))
        for side in sides:
            if side in self._sides6_seen:
                continue

            if check_dead_end(self.processor):
                return

            self.progress.left_count -= 1
            self.progress.updated = timezone.now()
            self.progress.save(update_fields=['left_count', 'updated'])

            deadline = time.monotonic() + self.MAX_SECONDS_SEARCH

            p1_exp_s3 = side
            p3_exp_s1 = side
            found = False
            for p1, unused1 in self._iter(self.unused0,
                                          self.side_options[1],
                                          self.side_options[4],
                                          [p1_exp_s3],
                                          self.side_options[3]):
                p0_exp_s2 = p1.side4

                for p3, unused2 in self._iter(unused1,
                                              [p3_exp_s1],
                                              self.side_options[9],
                                              self.side_options[11],
                                              self.side_options[8]):
                    p2_exp_s2 = p3.side4

                    for p0, unused3 in self._iter(unused2,
                                                  self.side_options[0],
                                                  [p0_exp_s2],
                                                  self.side_options[5],
                                                  self.side_options[2]):
                        p2_exp_s1 = p0.side3

                        for p2, _ in self._iter(unused3,
                                                [p2_exp_s1],
                                                [p2_exp_s2],
                                                self.side_options[10],
                                                self.side_options[7]):
                            # found a combi of p0..p3
                            found = True
                            # avoid repeating
                            self._sides8_seen.append(p2.side2)
                            break
                        # for

                        if time.monotonic() > deadline:
                            found = True

                        if found:
                            break
                    # for
                    if found:
                        break
                # for
                if found:
                    break
            # for

            if not found:
                self._reduce(segment, side)
                # built up history is no longer valid
                self._sides8_seen = []

            todo -= 1
            self.stdout.write('[INFO] Left: %s/%s' % (todo, len(sides)))
        # for

    def _reduce_s8(self):
        """
                  s0          s1
                +----+      +----+
            s2  | p0 |  s3  | p1 |  s4
                +----+      +----+
                  s5          s6
                +----+      +----+
            s7  | p2 |  s8  | p3 |  s9
                +----+      +----+
                 s10         s11
        """
        segment = calc_segment(self.locs[2], 2)
        sides = self.side_options[8]
        original_todo = len(sides)
        sides = self._limit_work(sides)
        todo = len(sides)
        # if todo - len(self._sides8_seen) > self.segment_limit:
        #     return

        self.progress.segment = segment
        self.progress.todo_count = todo
        self.progress.left_count = todo
        self.progress.save(update_fields=['segment', 'todo_count', 'left_count'])

        self.stdout.write('[INFO] Checking %s of %s options in segment %s' % (todo, original_todo, segment))
        for side in sides:
            if side in self._sides8_seen:
                continue

            if check_dead_end(self.processor):
                return

            self.progress.left_count -= 1
            self.progress.updated = timezone.now()
            self.progress.save(update_fields=['left_count', 'updated'])

            deadline = time.monotonic() + self.MAX_SECONDS_SEARCH

            p2_exp_s2 = side
            p3_exp_s4 = side
            found = False
            for p2, unused1 in self._iter(self.unused0,
                                          self.side_options[5],
                                          [p2_exp_s2],
                                          self.side_options[10],
                                          self.side_options[7]):
                p0_exp_s3 = p2.side1

                for p3, unused2 in self._iter(unused1,
                                              self.side_options[6],
                                              self.side_options[9],
                                              self.side_options[11],
                                              [p3_exp_s4]):
                    p1_exp_s3 = p3.side1

                    for p0, unused3 in self._iter(unused2,
                                                  self.side_options[0],
                                                  self.side_options[3],
                                                  [p0_exp_s3],
                                                  self.side_options[2]):
                        p1_exp_s4 = p0.side2

                        for _ in self._iter(unused3,
                                            self.side_options[1],
                                            self.side_options[4],
                                            [p1_exp_s3],
                                            [p1_exp_s4]):
                            # found a combi of p0..p3
                            found = True
                            break
                        # for

                        if time.monotonic() > deadline:
                            found = True

                        if found:
                            break
                    # for
                    if found:
                        break
                # for
                if found:
                    break
            # for

            if not found:
                self._reduce(segment, side)

            todo -= 1
            self.stdout.write('[INFO] Left: %s/%s' % (todo, len(sides)))
        # for

    def handle(self, *args, **options):

        """
                  s0          s1
                +----+      +----+
            s2  | p0 |  s3  | p1 |  s4
                +----+      +----+
                  s5          s6
                +----+      +----+
            s7  | p2 |  s8  | p3 |  s9
                +----+      +----+
                 s10         s11
        """

        if options['dryrun']:
            self.do_commit = False

        loc = options['loc']
        if loc < 1 or loc > 55 or loc in (8, 16, 24, 32, 40, 48):
            self.stdout.write('[ERROR] Invalid location')
            return
        self.locs = (loc, loc + 1,
                     loc + 8, loc + 9)
        self.stdout.write('[INFO] Locations: %s' % repr(self.locs))

        self.processor = options['processor']
        self.stdout.write('[INFO] Processor=%s' % self.processor)

        self.nop = options['nop']

        self.unused0 = self._get_unused()

        self._get_side_options()
        # self.stdout.write('%s' % ", ".join([str(len(opt)) for opt in self.side_options]))

        msg = "[%s, %s, %s, %s]" % (calc_segment(self.locs[0], 2),
                                    calc_segment(self.locs[0], 3),
                                    calc_segment(self.locs[1], 3),
                                    calc_segment(self.locs[2], 2))

        self.progress = EvalProgress(
                            eval_size=4,
                            eval_loc=loc,
                            processor=self.processor,
                            segment=0,
                            todo_count=0,
                            left_count=0,
                            solve_order=msg,
                            updated=timezone.now())
        self.progress.save()

        try:
            self._reduce_s3()

            if check_dead_end(self.processor):
                self.stdout.write('[WARNING] Dead end')
                return

            self.progress.solve_order = msg
            self.progress.updated = timezone.now()
            self.progress.save(update_fields=['solve_order', 'updated'])
            self._sides5_seen = frozenset(self._sides5_seen)
            self._reduce_s5()

            if check_dead_end(self.processor):
                self.stdout.write('[WARNING] Dead end')
                return

            self.progress.solve_order = msg
            self.progress.updated = timezone.now()
            self.progress.save(update_fields=['solve_order', 'updated'])
            self._sides6_seen = frozenset(self._sides6_seen)
            self._reduce_s6()

            if check_dead_end(self.processor):
                self.stdout.write('[WARNING] Dead end')
                return

            self.progress.solve_order = msg
            self.progress.updated = timezone.now()
            self.progress.save(update_fields=['solve_order', 'updated'])
            self._sides8_seen = frozenset(self._sides8_seen)
            self._reduce_s8()
        except KeyboardInterrupt:
            pass

        self.progress.delete()

        if self.reductions == 0:
            self.stdout.write('[INFO] No reductions')
        else:
            self.stdout.write('[INFO] Reductions: %s' % self.reductions)
            if not self.do_commit:
                self.stdout.write('[WARNING] Use --commit to keep')

# end of file
