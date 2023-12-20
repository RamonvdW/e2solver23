# -*- coding: utf-8 -*-

#  Copyright (c) 2023 Ramon van der Winkel.
#  All rights reserved.
#  Licensed under BSD-3-Clause-Clear. See LICENSE file for details.

from django.utils import timezone
from django.core.management.base import BaseCommand
from Pieces2x2.models import TwoSide, TwoSideOptions, Piece2x2, EvalProgress
from Pieces2x2.helpers import calc_segment
import time


class Command(BaseCommand):

    help = "Eval a possible reduction in TwoSideOptions for a square of 16 locations"

    """
              s0           s1           s2            s3
            +-----+      +-----+      +-----+       +-----+
        s4  | p0  |  s5  | p1  |  s6  | p2  |  s7   | p3  |  s8
            +-----+      +-----+      +-----+       +-----+
              s9           s10          s11           s12
            +-----+      +-----+      +-----+       +-----+
        s13 | p4  |  s14 | p5  |  s15 | p6  |  s16  | p7  |  s17
            +-----+      +-----+      +-----+       +-----+
              s18          s19          s20           s21
            +-----+      +-----+      +-----+       +-----+
        s22 | p8  |  s23 | p9  |  s24 | p10 |  s25  | p11 |  s26
            +-----+      +-----+      +-----+       +-----+
              s27          s28          s29           s30
            +-----+      +-----+      +-----+       +-----+
        s31 | p12 |  s32 | p13 |  s33 | p14 |  s34  | p15 |  s35
            +-----+      +-----+      +-----+       +-----+
              s36          s37          s38           s39
    """

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
        self.locs = (0, 0)                  # p0..p8
        self.side_options = ([], [])        # s0..s23
        self.side_options_rev = ([], [])    # s0..s23
        self.reductions = 0

        self.unused0 = list()

        self.do_commit = True

        # [p_nr] = [p_nr on side1..4 or -1 if no neighbour]
        self.neighbours: dict[int, tuple] = {0: (-1, 1, 4, -1),
                                             1: (-1, 2, 5, 0),
                                             2: (-1, 3, 6, 1),
                                             3: (-1, -1, 7, 2),
                                             4: (0, 5, 8, -1),
                                             5: (1, 6, 9, 4),
                                             6: (2, 7, 10, 5),
                                             7: (3, -1, 11, 6),
                                             8: (4, 9, 12, -1),
                                             9: (5, 10, 13, 8),
                                             10: (6, 11, 14, 9),
                                             11: (7, -1, 15, 10),
                                             12: (8, 13, -1, -1),
                                             13: (9, 14, -1, 12),
                                             14: (10, 15, -1, 13),
                                             15: (11, -1, -1, 14)}

        """
                  s0           s1           s2            s3
                +-----+      +-----+      +-----+       +-----+
            s4  | p0  |  s5  | p1  |  s6  | p2  |  s7   | p3  |  s8
                +-----+      +-----+      +-----+       +-----+
                  s9           s10          s11           s12
                +-----+      +-----+      +-----+       +-----+
            s13 | p4  |  s14 | p5  |  s15 | p6  |  s16  | p7  |  s17
                +-----+      +-----+      +-----+       +-----+
                  s18          s19          s20           s21
                +-----+      +-----+      +-----+       +-----+
            s22 | p8  |  s23 | p9  |  s24 | p10 |  s25  | p11 |  s26
                +-----+      +-----+      +-----+       +-----+
                  s27          s28          s29           s30
                +-----+      +-----+      +-----+       +-----+
            s31 | p12 |  s32 | p13 |  s33 | p14 |  s34  | p15 |  s35
                +-----+      +-----+      +-----+       +-----+
                  s36          s37          s38           s39
        """
        # [p_nr] = [4 side nr]
        self.side_nrs: dict[int, tuple] = {0: (0, 5, 9, 4),
                                           1: (1, 6, 10, 5),
                                           2: (2, 7, 11, 6),
                                           3: (3, 8, 12, 7),
                                           4: (9, 14, 18, 13),
                                           5: (10, 15, 19, 14),
                                           6: (11, 16, 20, 15),
                                           7: (12, 17, 21, 16),
                                           8: (18, 23, 27, 22),
                                           9: (19, 24, 28, 23),
                                           10: (20, 25, 29, 24),
                                           11: (21, 26, 30, 25),
                                           12: (27, 32, 36, 31),
                                           13: (28, 33, 37, 32),
                                           14: (29, 34, 38, 33),
                                           15: (30, 35, 39, 34)}

        # [0..8] = None or Piece2x2 with side1/2/3/4
        self.board: dict[int, Piece2x2 | None] = {0: None, 1: None, 2: None, 3: None,
                                                  4: None, 5: None, 6: None, 7: None,
                                                  8: None, 9: None, 10: None, 11: None,
                                                  12: None, 13: None, 14: None, 15: None}

        self.board_order = list()   # solve order (for popping)
        self.board_unused = list()
        self.p_nrs_order = list()
        self.prev_tick = 0
        self.progress = None

    def add_arguments(self, parser):
        parser.add_argument('processor', nargs=1, type=int, help='Processor number to use')
        parser.add_argument('loc', nargs=1, type=int, help='Top-left location on board (1..37)')
        parser.add_argument('--dryrun', action='store_true')

    def _calc_unused0(self):
        self.unused0 = list(range(1, 256+1))

        if 36 not in self.locs:
            self.unused0.remove(139)

        if 10 not in self.locs:
            self.unused0.remove(208)

        if 15 not in self.locs:
            self.unused0.remove(255)

        if 50 not in self.locs:
            self.unused0.remove(181)

        if 55 not in self.locs:
            self.unused0.remove(249)

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
        # self.stdout.write('[DEBUG] Segment %s has %s options' % (segment, len(options)))
        return options

    def _get_side_options(self):
        """
                      s0           s1           s2            s3
                    +-----+      +-----+      +-----+       +-----+
                s4  | p0  |  s5  | p1  |  s6  | p2  |  s7   | p3  |  s8
                    +-----+      +-----+      +-----+       +-----+
                      s9           s10          s11           s12
                    +-----+      +-----+      +-----+       +-----+
                s13 | p4  |  s14 | p5  |  s15 | p6  |  s16  | p7  |  s17
                    +-----+      +-----+      +-----+       +-----+
                      s18          s19          s20           s21
                    +-----+      +-----+      +-----+       +-----+
                s22 | p8  |  s23 | p9  |  s24 | p10 |  s25  | p11 |  s26
                    +-----+      +-----+      +-----+       +-----+
                      s27          s28          s29           s30
                    +-----+      +-----+      +-----+       +-----+
                s31 | p12 |  s32 | p13 |  s33 | p14 |  s34  | p15 |  s35
                    +-----+      +-----+      +-----+       +-----+
                      s36          s37          s38           s39
        """
        s0 = self._get_loc_side_options(self.locs[0], 1)
        s1 = self._get_loc_side_options(self.locs[1], 1)
        s2 = self._get_loc_side_options(self.locs[2], 1)
        s3 = self._get_loc_side_options(self.locs[3], 1)

        s4 = self._get_loc_side_options(self.locs[0], 4)
        s5 = self._get_loc_side_options(self.locs[0], 2)
        s6 = self._get_loc_side_options(self.locs[1], 2)
        s7 = self._get_loc_side_options(self.locs[2], 2)
        s8 = self._get_loc_side_options(self.locs[3], 2)

        s9 = self._get_loc_side_options(self.locs[4], 1)
        s10 = self._get_loc_side_options(self.locs[5], 1)
        s11 = self._get_loc_side_options(self.locs[6], 1)
        s12 = self._get_loc_side_options(self.locs[7], 1)

        s13 = self._get_loc_side_options(self.locs[4], 4)
        s14 = self._get_loc_side_options(self.locs[4], 2)
        s15 = self._get_loc_side_options(self.locs[5], 2)
        s16 = self._get_loc_side_options(self.locs[6], 2)
        s17 = self._get_loc_side_options(self.locs[7], 2)

        s18 = self._get_loc_side_options(self.locs[8], 1)
        s19 = self._get_loc_side_options(self.locs[9], 1)
        s20 = self._get_loc_side_options(self.locs[10], 1)
        s21 = self._get_loc_side_options(self.locs[11], 1)

        s22 = self._get_loc_side_options(self.locs[8], 4)
        s23 = self._get_loc_side_options(self.locs[8], 2)
        s24 = self._get_loc_side_options(self.locs[9], 2)
        s25 = self._get_loc_side_options(self.locs[10], 2)
        s26 = self._get_loc_side_options(self.locs[11], 2)

        s27 = self._get_loc_side_options(self.locs[12], 1)
        s28 = self._get_loc_side_options(self.locs[13], 1)
        s29 = self._get_loc_side_options(self.locs[14], 1)
        s30 = self._get_loc_side_options(self.locs[15], 1)

        s31 = self._get_loc_side_options(self.locs[12], 4)
        s32 = self._get_loc_side_options(self.locs[12], 2)
        s33 = self._get_loc_side_options(self.locs[13], 2)
        s34 = self._get_loc_side_options(self.locs[14], 2)
        s35 = self._get_loc_side_options(self.locs[15], 2)

        s36 = self._get_loc_side_options(self.locs[12], 3)
        s37 = self._get_loc_side_options(self.locs[13], 3)
        s38 = self._get_loc_side_options(self.locs[14], 3)
        s39 = self._get_loc_side_options(self.locs[15], 3)

        self.side_options = [s0, s1, s2, s3,
                             s4, s5, s6, s7, s8,
                             s9, s10, s11, s12,
                             s13, s14, s15, s16, s17,
                             s18, s19, s20, s21,
                             s22, s23, s24, s25, s26,
                             s27, s28, s29, s30,
                             s31, s32, s33, s34, s35,
                             s36, s37, s38, s39]

        self.side_options_rev = [self._reverse_sides(s) for s in self.side_options]

    def _board_place(self, p_nr: int, p2x2):
        self.board_order.append(p_nr)
        self.board[p_nr] = p2x2
        self.board_unused.remove(p2x2.nr1)
        self.board_unused.remove(p2x2.nr2)
        self.board_unused.remove(p2x2.nr3)
        self.board_unused.remove(p2x2.nr4)

    def _board_pop(self):
        p_nr = self.board_order[-1]
        self.board_order = self.board_order[:-1]
        p2x2 = self.board[p_nr]
        self.board[p_nr] = None
        self.board_unused.extend([p2x2.nr1, p2x2.nr2, p2x2.nr3, p2x2.nr4])

    def _iter(self, options_side1, options_side2, options_side3, options_side4):
        unused = self.board_unused
        for p in (Piece2x2
                  .objects
                  .filter(side1__in=options_side1,
                          side2__in=options_side2,
                          side3__in=options_side3,
                          side4__in=options_side4,
                          nr1__in=unused,
                          nr2__in=unused,
                          nr3__in=unused,
                          nr4__in=unused)):
            yield p
        # for

    def _reduce(self, segment, two_side):
        qset = TwoSideOptions.objects.filter(processor=self.processor, segment=segment, two_side=two_side)
        if qset.count() != 1:
            self.stderr.write('[ERROR] Cannot find segment=%s, two_side=%s' % (segment, two_side))
        else:
            self.stdout.write('[INFO] Reduction segment %s: %s' % (segment, two_side))
            if self.do_commit:
                qset.delete()
            self.reductions += 1

    def _select_p_nr(self):
        # decide which position on the board has the fewest options

        # follow previous solve order
        for p_nr in self.p_nrs_order:
            if self.board[p_nr] is None:
                return p_nr, False
        # for

        # decide the next best position on the board to solve

        qset = Piece2x2.objects.filter(nr1__in=self.board_unused,
                                       nr2__in=self.board_unused,
                                       nr3__in=self.board_unused,
                                       nr4__in=self.board_unused)

        p_nr_counts = list()
        for p_nr in range(16):
            if self.board[p_nr] is None:
                # empty position on the board
                s1, s2, s3, s4 = self.side_nrs[p_nr]
                options_side1 = self.side_options[s1]
                options_side2 = self.side_options[s2]
                options_side3 = self.side_options_rev[s3]
                options_side4 = self.side_options_rev[s4]

                n1, n2, n3, n4 = self.neighbours[p_nr]
                if n1 >= 0:
                    p = self.board[n1]
                    if p:
                        options_side1 = [self.twoside2reverse[p.side3]]
                if n2 >= 0:
                    p = self.board[n2]
                    if p:
                        options_side2 = [self.twoside2reverse[p.side4]]
                if n3 >= 0:
                    p = self.board[n3]
                    if p:
                        options_side3 = [self.twoside2reverse[p.side1]]
                if n4 >= 0:
                    p = self.board[n4]
                    if p:
                        options_side4 = [self.twoside2reverse[p.side2]]

                count = qset.filter(side1__in=options_side1,
                                    side2__in=options_side2,
                                    side3__in=options_side3,
                                    side4__in=options_side4).count()
                tup = (count, p_nr)
                p_nr_counts.append(tup)

                if count == 0:
                    # dead end
                    # self.stdout.write('[DEBUG] No options for %s' % p_nr)
                    return -1, True
        # for

        # take the lowest
        if len(p_nr_counts) > 0:
            p_nr_counts.sort()       # lowest first
            p_nr = p_nr_counts[0][-1]
            # self.stdout.write('[INFO] Added %s' % p_nr)
            self.p_nrs_order.append(p_nr)
            return p_nr, False

        # niets kunnen kiezen
        self.stdout.write('[DEBUG] select_p_nr failure')
        return -1, True

    def _find_recurse(self):
        tick = time.monotonic()
        if tick - self.prev_tick > 30:
            self.prev_tick = tick
            msg = '(%s) %s' % (len(self.board_order), repr([self.locs[idx] for idx in self.board_order]))
            print(msg)
            self.progress.solve_order = msg
            self.progress.updated = timezone.now()
            self.progress.save(update_fields=['solve_order', 'updated'])

        if len(self.board_order) == 16:
            return True

        # decide which p_nr to continue with
        p_nr, has_zero = self._select_p_nr()
        if has_zero:
            return False

        s1, s2, s3, s4 = self.side_nrs[p_nr]
        options_side1 = self.side_options[s1]
        options_side2 = self.side_options[s2]
        options_side3 = self.side_options_rev[s3]
        options_side4 = self.side_options_rev[s4]

        n1, n2, n3, n4 = self.neighbours[p_nr]
        if n1 >= 0:
            p = self.board[n1]
            if p:
                options_side1 = [self.twoside2reverse[p.side3]]
        if n2 >= 0:
            p = self.board[n2]
            if p:
                options_side2 = [self.twoside2reverse[p.side4]]
        if n3 >= 0:
            p = self.board[n3]
            if p:
                options_side3 = [self.twoside2reverse[p.side1]]
        if n4 >= 0:
            p = self.board[n4]
            if p:
                options_side4 = [self.twoside2reverse[p.side2]]

        for p in self._iter(options_side1, options_side2, options_side3, options_side4):
            self._board_place(p_nr, p)
            found = self._find_recurse()
            self._board_pop()

            if found:
                return True
        # for

        return False

    def _find_reduce(self, p_nr, side_n, s_nr):
        segment = calc_segment(self.locs[p_nr], side_n)
        sides = self.side_options[s_nr]
        todo = len(sides)
        self.stdout.write('[INFO] Checking %s options in segment %s' % (len(sides), segment))
        self.p_nrs_order = list()       # allow deciding optimal order anew

        self.progress.segment = segment
        self.progress.todo_count = todo
        self.progress.save(update_fields=['segment', 'todo_count'])

        for side in sides:
            # update the progress record in the database
            self.progress.left_count = todo
            self.progress.updated = timezone.now()
            self.progress.save(update_fields=['left_count', 'updated'])

            # place the first piece
            s1, s2, s3, s4 = self.side_nrs[p_nr]
            options_side1 = self.side_options[s1]
            options_side2 = self.side_options[s2]
            options_side3 = self.side_options_rev[s3]
            options_side4 = self.side_options_rev[s4]

            if side_n == 1:
                options_side1 = [side]
            elif side_n == 2:
                options_side2 = [side]
            elif side_n == 3:
                options_side3 = [self.twoside2reverse[side]]
            else:   # side_n == 4:
                options_side4 = [self.twoside2reverse[side]]

            found = False
            for p in self._iter(options_side1, options_side2, options_side3, options_side4):
                self._board_place(p_nr, p)
                found = self._find_recurse()
                self._board_pop()
                if found:
                    break
            # for

            if not found:
                self._reduce(segment, side)

            todo -= 1
            self.stdout.write('[INFO] Remaining: %s/%s' % (todo, len(sides)))
            self.prev_tick = time.monotonic()
        # for

    def handle(self, *args, **options):

        """
                      s0           s1           s2            s3
                    +-----+      +-----+      +-----+       +-----+
                s4  | p0  |  s5  | p1  |  s6  | p2  |  s7   | p3  |  s8
                    +-----+      +-----+      +-----+       +-----+
                      s9           s10          s11           s12
                    +-----+      +-----+      +-----+       +-----+
                s13 | p4  |  s14 | p5  |  s15 | p6  |  s16  | p7  |  s17
                    +-----+      +-----+      +-----+       +-----+
                      s18          s19          s20           s21
                    +-----+      +-----+      +-----+       +-----+
                s22 | p8  |  s23 | p9  |  s24 | p10 |  s25  | p11 |  s26
                    +-----+      +-----+      +-----+       +-----+
                      s27          s28          s29           s30
                    +-----+      +-----+      +-----+       +-----+
                s31 | p12 |  s32 | p13 |  s33 | p14 |  s34  | p15 |  s35
                    +-----+      +-----+      +-----+       +-----+
                      s36          s37          s38           s39
        """

        if options['dryrun']:
            self.do_commit = False

        loc = options['loc'][0]
        if loc < 1 or loc > 37 or loc in (6, 7, 8,
                                          14, 15, 16,
                                          22, 23, 24,
                                          30, 31, 32):
            self.stderr.write('[ERROR] Invalid location')
            return
        self.locs = (loc + 0, loc + 1, loc + 2, loc + 3,
                     loc + 8, loc + 9, loc + 10, loc + 11,
                     loc + 16, loc + 17, loc + 18, loc + 19,
                     loc + 24, loc + 25, loc + 26, loc + 27)
        self.stdout.write('[INFO] Locations: %s' % repr(self.locs))

        self.processor = options['processor'][0]
        self.stdout.write('[INFO] Processor=%s' % self.processor)

        self._calc_unused0()
        self.board_unused = self.unused0[:]

        self._get_side_options()
        # self.stdout.write('%s' % ", ".join([str(len(opt)) for opt in self.side_options]))

        self.prev_tick = time.monotonic()

        self.progress = EvalProgress(
                        eval_size=16,
                        eval_loc=self.locs[0],
                        processor=self.processor,
                        segment=0,
                        todo_count=0,
                        left_count=0,
                        solve_order='',
                        updated=timezone.now())
        self.progress.save()

        try:
            self._find_reduce(0, 2, 5)
            self._find_reduce(1, 2, 6)
            self._find_reduce(2, 2, 7)

            self._find_reduce(4, 1, 9)
            self._find_reduce(5, 1, 10)
            self._find_reduce(6, 1, 11)
            self._find_reduce(7, 1, 12)

            self._find_reduce(4, 2, 14)
            self._find_reduce(5, 2, 15)
            self._find_reduce(6, 2, 16)

            self._find_reduce(8, 1, 18)
            self._find_reduce(9, 1, 19)
            self._find_reduce(10, 1, 20)
            self._find_reduce(11, 1, 21)

            self._find_reduce(8, 2, 23)
            self._find_reduce(9, 2, 24)
            self._find_reduce(10, 2, 25)

            self._find_reduce(12, 1, 27)
            self._find_reduce(13, 1, 28)
            self._find_reduce(14, 1, 29)
            self._find_reduce(15, 1, 30)

            self._find_reduce(12, 2, 32)
            self._find_reduce(13, 2, 33)
            self._find_reduce(14, 2, 34)

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
