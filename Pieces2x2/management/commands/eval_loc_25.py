# -*- coding: utf-8 -*-

#  Copyright (c) 2023-2024 Ramon van der Winkel.
#  All rights reserved.
#  Licensed under BSD-3-Clause-Clear. See LICENSE file for details.

from django.utils import timezone
from django.core.management.base import BaseCommand
from Pieces2x2.models import TwoSide, TwoSideOptions, Piece2x2, EvalProgress
from Pieces2x2.helpers import calc_segment
from Solutions.models import Solution8x8
from WorkQueue.operations import propagate_segment_reduction
import datetime
import time


class Command(BaseCommand):

    help = "Eval a possible reduction in TwoSideOptions for a square of 25 locations"

    """
              s0           s1           s2            s3            s4
            +-----+      +-----+      +-----+       +-----+       +-----+
        s5  | p0  |  s6  | p1  |  s7  | p2  |  s8   | p3  |  s9   | p4  |  s10
            +-----+      +-----+      +-----+       +-----+       +-----+
              s11          s12          s13           s14           s15
            +-----+      +-----+      +-----+       +-----+       +-----+
        s16 | p5  |  s17 | p6  |  s18 | p7  |  s19  | p8  |  s20  | p9  |  s21
            +-----+      +-----+      +-----+       +-----+       +-----+
              s22          s23          s24           s25           s26
            +-----+      +-----+      +-----+       +-----+       +-----+
        s27 | p10 |  s28 | p11 |  s29 | p12 |  s30  | p13 |  s31  | p14 |  s32
            +-----+      +-----+      +-----+       +-----+       +-----+
              s33          s34          s35           s36           s37
            +-----+      +-----+      +-----+       +-----+       +-----+
        s38 | p15 |  s39 | p16 |  s40 | p17 |  s41  | p18 |  s42  | p19 |  s43
            +-----+      +-----+      +-----+       +-----+       +-----+
              s44          s45          s46           s47           s48
            +-----+      +-----+      +-----+       +-----+       +-----+
        s49 | p20 |  s50 | p21 |  s51 | p22 |  s52  | p23 |  s53  | p24 |  s54
            +-----+      +-----+      +-----+       +-----+       +-----+
              s55          s56          s57           s58           s59
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
        self.segment = 0
        self.locs = (0, 0)                  # p0..p8
        self.side_options = ([], [])        # s0..s23
        self.side_options_rev = ([], [])    # s0..s23
        self.segment_options = dict()       # [segment] = side_options
        self.reductions = 0

        self.unused0 = list()

        self.do_commit = True

        # [p_nr] = [p_nr on side1..4 or -1 if border or -2 if no neighbour]
        self.neighbours: dict[int, tuple] = {0: (-1, 1, 5, -1),
                                             1: (-1, 2, 6, 0),
                                             2: (-1, 3, 7, 1),
                                             3: (-1, 4, 8, 2),
                                             4: (-1, -1, 9, 3),
                                             5: (0, 6, 10, -1),
                                             6: (1, 7, 11, 5),
                                             7: (2, 8, 12, 6),
                                             8: (3, 9, 13, 7),
                                             9: (4, -1, 14, 8),
                                             10: (5, 11, 15, -1),
                                             11: (6, 12, 16, 10),
                                             12: (7, 13, 17, 11),
                                             13: (8, 14, 18, 12),
                                             14: (9, -1, 19, 13),
                                             15: (10, 16, 20, -1),
                                             16: (11, 17, 21, 15),
                                             17: (12, 18, 22, 16),
                                             18: (13, 19, 23, 17),
                                             19: (14, -1, 24, 18),
                                             20: (15, 21, -1, -1),
                                             21: (16, 22, -1, 20),
                                             22: (17, 23, -1, 21),
                                             23: (18, 24, -1, 22),
                                             24: (19, -1, -1, 23)}

        """
                  s0           s1           s2            s3            s4
                +-----+      +-----+      +-----+       +-----+       +-----+
            s5  | p0  |  s6  | p1  |  s7  | p2  |  s8   | p3  |  s9   | p4  |  s10
                +-----+      +-----+      +-----+       +-----+       +-----+
                  s11          s12          s13           s14           s15
                +-----+      +-----+      +-----+       +-----+       +-----+
            s16 | p5  |  s17 | p6  |  s18 | p7  |  s19  | p8  |  s20  | p9  |  s21
                +-----+      +-----+      +-----+       +-----+       +-----+
                  s22          s23          s24           s25           s26
                +-----+      +-----+      +-----+       +-----+       +-----+
            s27 | p10 |  s28 | p11 |  s29 | p12 |  s30  | p13 |  s31  | p14 |  s32
                +-----+      +-----+      +-----+       +-----+       +-----+
                  s33          s34          s35           s36           s37
                +-----+      +-----+      +-----+       +-----+       +-----+
            s38 | p15 |  s39 | p16 |  s40 | p17 |  s41  | p18 |  s42  | p19 |  s43
                +-----+      +-----+      +-----+       +-----+       +-----+
                  s44          s45          s46           s47           s48
                +-----+      +-----+      +-----+       +-----+       +-----+
            s49 | p20 |  s50 | p21 |  s51 | p22 |  s52  | p23 |  s53  | p24 |  s54
                +-----+      +-----+      +-----+       +-----+       +-----+
                  s55          s56          s57           s58           s59
        """
        # [p_nr] = [4 side nr]
        self.side_nrs: dict[int, tuple] = {0: (0, 6, 11, 5),
                                           1: (1, 7, 12, 6),
                                           2: (2, 8, 13, 7),
                                           3: (3, 9, 14, 8),
                                           4: (4, 10, 15, 9),
                                           5: (11, 17, 22, 16),
                                           6: (12, 18, 23, 17),
                                           7: (13, 19, 24, 18),
                                           8: (14, 20, 25, 19),
                                           9: (15, 21, 26, 20),
                                           10: (22, 28, 33, 27),
                                           11: (23, 28, 34, 28),
                                           12: (24, 30, 35, 29),
                                           13: (25, 31, 36, 30),
                                           14: (26, 32, 37, 31),
                                           15: (33, 39, 44, 38),
                                           16: (34, 40, 45, 39),
                                           17: (35, 41, 46, 40),
                                           18: (36, 42, 47, 41),
                                           19: (37, 43, 48, 42),
                                           20: (44, 50, 55, 49),
                                           21: (45, 51, 56, 50),
                                           22: (46, 52, 57, 51),
                                           23: (47, 53, 58, 52),
                                           24: (48, 54, 59, 53)}

        # [0..8] = None or Piece2x2 with side1/2/3/4
        self.board: dict[int, Piece2x2 | None] = {0: None, 1: None, 2: None, 3: None, 4: None,
                                                  5: None, 6: None, 7: None, 8: None, 9: None,
                                                  10: None, 11: None, 12: None, 13: None, 14: None,
                                                  15: None, 16: None, 17: None, 18: None, 19: None,
                                                  20: None, 21: None, 22: None, 23: None, 24: None}

        self.board_order = list()   # solve order (for popping)
        self.board_unused = list()
        self.p_nrs_order = list()
        self.requested_order = list()
        self.prev_tick = 0
        self.progress = None

        self.progress_15min = -1

    def add_arguments(self, parser):
        parser.add_argument('processor', nargs=1, type=int, help='Processor number to use')
        parser.add_argument('loc', nargs=1, type=int, help='Top-left location on board (1..37)')
        parser.add_argument('segment', nargs=1, type=int, help='Segment to work on (1..72, 129..193)')
        parser.add_argument('--dryrun', action='store_true')
        parser.add_argument('order', nargs='*', type=int, help='Solving order (1..64), max %s' % len(self.locs))

    def _check_progress_15min(self):
        # returns True when it is time to do a 15min-interval report
        minute = datetime.datetime.now().minute
        curr_15min = int(minute / 15) % 4
        if curr_15min != self.progress_15min:
            next_15min = (curr_15min + 1) % 4
            self.progress_15min = next_15min
            return True
        return False

    def _save_progress_solution(self):
        sol = Solution8x8(based_on_6x6=0)
        for loc in range(1, 64+1):
            field_str = 'nr%s' % loc
            setattr(sol, field_str, 0)
        # for
        for nr in range(len(self.locs)):
            loc = self.locs[nr]
            p2x2 = self.board[nr]
            if p2x2:
                field_str = 'nr%s' % loc
                setattr(sol, field_str, p2x2.nr)
        # for
        sol.save()
        print('[INFO] Saved progress solution: pk=%s' % sol.pk)

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
                  s0           s1           s2            s3            s4
                +-----+      +-----+      +-----+       +-----+       +-----+
            s5  | p0  |  s6  | p1  |  s7  | p2  |  s8   | p3  |  s9   | p4  |  s10
                +-----+      +-----+      +-----+       +-----+       +-----+
                  s11          s12          s13           s14           s15
                +-----+      +-----+      +-----+       +-----+       +-----+
            s16 | p5  |  s17 | p6  |  s18 | p7  |  s19  | p8  |  s20  | p9  |  s21
                +-----+      +-----+      +-----+       +-----+       +-----+
                  s22          s23          s24           s25           s26
                +-----+      +-----+      +-----+       +-----+       +-----+
            s27 | p10 |  s28 | p11 |  s29 | p12 |  s30  | p13 |  s31  | p14 |  s32
                +-----+      +-----+      +-----+       +-----+       +-----+
                  s33          s34          s35           s36           s37
                +-----+      +-----+      +-----+       +-----+       +-----+
            s38 | p15 |  s39 | p16 |  s40 | p17 |  s41  | p18 |  s42  | p19 |  s43
                +-----+      +-----+      +-----+       +-----+       +-----+
                  s44          s45          s46           s47           s48
                +-----+      +-----+      +-----+       +-----+       +-----+
            s49 | p20 |  s50 | p21 |  s51 | p22 |  s52  | p23 |  s53  | p24 |  s54
                +-----+      +-----+      +-----+       +-----+       +-----+
                  s55          s56          s57           s58           s59
        """
        s0 = self._get_loc_side_options(self.locs[0], 1)
        s1 = self._get_loc_side_options(self.locs[1], 1)
        s2 = self._get_loc_side_options(self.locs[2], 1)
        s3 = self._get_loc_side_options(self.locs[3], 1)
        s4 = self._get_loc_side_options(self.locs[4], 1)

        s5 = self._get_loc_side_options(self.locs[0], 4)
        s6 = self._get_loc_side_options(self.locs[0], 2)
        s7 = self._get_loc_side_options(self.locs[1], 2)
        s8 = self._get_loc_side_options(self.locs[2], 2)
        s9 = self._get_loc_side_options(self.locs[3], 2)
        s10 = self._get_loc_side_options(self.locs[4], 2)

        s11 = self._get_loc_side_options(self.locs[5], 1)
        s12 = self._get_loc_side_options(self.locs[6], 1)
        s13 = self._get_loc_side_options(self.locs[7], 1)
        s14 = self._get_loc_side_options(self.locs[8], 1)
        s15 = self._get_loc_side_options(self.locs[9], 1)

        s16 = self._get_loc_side_options(self.locs[5], 4)
        s17 = self._get_loc_side_options(self.locs[5], 2)
        s18 = self._get_loc_side_options(self.locs[6], 2)
        s19 = self._get_loc_side_options(self.locs[7], 2)
        s20 = self._get_loc_side_options(self.locs[8], 2)
        s21 = self._get_loc_side_options(self.locs[9], 2)

        s22 = self._get_loc_side_options(self.locs[10], 1)
        s23 = self._get_loc_side_options(self.locs[11], 1)
        s24 = self._get_loc_side_options(self.locs[12], 1)
        s25 = self._get_loc_side_options(self.locs[13], 1)
        s26 = self._get_loc_side_options(self.locs[14], 1)

        s27 = self._get_loc_side_options(self.locs[10], 4)
        s28 = self._get_loc_side_options(self.locs[10], 2)
        s29 = self._get_loc_side_options(self.locs[11], 2)
        s30 = self._get_loc_side_options(self.locs[12], 2)
        s31 = self._get_loc_side_options(self.locs[13], 2)
        s32 = self._get_loc_side_options(self.locs[14], 2)

        s33 = self._get_loc_side_options(self.locs[15], 1)
        s34 = self._get_loc_side_options(self.locs[16], 1)
        s35 = self._get_loc_side_options(self.locs[17], 1)
        s36 = self._get_loc_side_options(self.locs[18], 1)
        s37 = self._get_loc_side_options(self.locs[19], 1)

        s38 = self._get_loc_side_options(self.locs[15], 4)
        s39 = self._get_loc_side_options(self.locs[15], 2)
        s40 = self._get_loc_side_options(self.locs[16], 2)
        s41 = self._get_loc_side_options(self.locs[17], 2)
        s42 = self._get_loc_side_options(self.locs[18], 2)
        s43 = self._get_loc_side_options(self.locs[19], 2)

        s44 = self._get_loc_side_options(self.locs[20], 1)
        s45 = self._get_loc_side_options(self.locs[21], 1)
        s46 = self._get_loc_side_options(self.locs[22], 1)
        s47 = self._get_loc_side_options(self.locs[23], 1)
        s48 = self._get_loc_side_options(self.locs[24], 1)

        s49 = self._get_loc_side_options(self.locs[20], 4)
        s50 = self._get_loc_side_options(self.locs[20], 2)
        s51 = self._get_loc_side_options(self.locs[21], 2)
        s52 = self._get_loc_side_options(self.locs[22], 2)
        s53 = self._get_loc_side_options(self.locs[23], 2)
        s54 = self._get_loc_side_options(self.locs[24], 2)

        s55 = self._get_loc_side_options(self.locs[20], 3)
        s56 = self._get_loc_side_options(self.locs[21], 3)
        s57 = self._get_loc_side_options(self.locs[22], 3)
        s58 = self._get_loc_side_options(self.locs[23], 3)
        s59 = self._get_loc_side_options(self.locs[24], 3)

        self.side_options = [s0, s1, s2, s3, s4,
                             s5, s6, s7, s8, s9, s10,
                             s11, s12, s13, s14, s15,
                             s16, s17, s18, s19, s20, s21,
                             s22, s23, s24, s25, s26,
                             s27, s28, s29, s30, s31, s32,
                             s33, s34, s35, s36, s37,
                             s38, s39, s40, s41, s42, s43,
                             s44, s45, s46, s47, s48,
                             s49, s50, s51, s52, s53, s54,
                             s55, s56, s57, s58, s59]

        self.side_options_rev = [self._reverse_sides(s) for s in self.side_options]

        self.segment_options[calc_segment(self.locs[0], 1)] = s0
        self.segment_options[calc_segment(self.locs[1], 1)] = s1
        self.segment_options[calc_segment(self.locs[2], 1)] = s2
        self.segment_options[calc_segment(self.locs[3], 1)] = s3
        self.segment_options[calc_segment(self.locs[4], 1)] = s4

        self.segment_options[calc_segment(self.locs[0], 4)] = s5
        self.segment_options[calc_segment(self.locs[0], 2)] = s6
        self.segment_options[calc_segment(self.locs[1], 2)] = s7
        self.segment_options[calc_segment(self.locs[2], 2)] = s8
        self.segment_options[calc_segment(self.locs[3], 2)] = s9
        self.segment_options[calc_segment(self.locs[4], 2)] = s10

        self.segment_options[calc_segment(self.locs[5], 1)] = s11
        self.segment_options[calc_segment(self.locs[6], 1)] = s12
        self.segment_options[calc_segment(self.locs[7], 1)] = s13
        self.segment_options[calc_segment(self.locs[8], 1)] = s14
        self.segment_options[calc_segment(self.locs[9], 1)] = s15

        self.segment_options[calc_segment(self.locs[5], 4)] = s16
        self.segment_options[calc_segment(self.locs[5], 2)] = s17
        self.segment_options[calc_segment(self.locs[6], 2)] = s18
        self.segment_options[calc_segment(self.locs[7], 2)] = s19
        self.segment_options[calc_segment(self.locs[8], 2)] = s20
        self.segment_options[calc_segment(self.locs[9], 2)] = s21

        self.segment_options[calc_segment(self.locs[10], 1)] = s22
        self.segment_options[calc_segment(self.locs[11], 1)] = s23
        self.segment_options[calc_segment(self.locs[12], 1)] = s24
        self.segment_options[calc_segment(self.locs[13], 1)] = s25
        self.segment_options[calc_segment(self.locs[14], 1)] = s26

        self.segment_options[calc_segment(self.locs[10], 4)] = s27
        self.segment_options[calc_segment(self.locs[10], 2)] = s28
        self.segment_options[calc_segment(self.locs[11], 2)] = s29
        self.segment_options[calc_segment(self.locs[12], 2)] = s30
        self.segment_options[calc_segment(self.locs[13], 2)] = s31
        self.segment_options[calc_segment(self.locs[14], 2)] = s32

        self.segment_options[calc_segment(self.locs[15], 1)] = s33
        self.segment_options[calc_segment(self.locs[16], 1)] = s34
        self.segment_options[calc_segment(self.locs[17], 1)] = s35
        self.segment_options[calc_segment(self.locs[18], 1)] = s36
        self.segment_options[calc_segment(self.locs[19], 1)] = s37

        self.segment_options[calc_segment(self.locs[15], 4)] = s38
        self.segment_options[calc_segment(self.locs[15], 2)] = s39
        self.segment_options[calc_segment(self.locs[16], 2)] = s40
        self.segment_options[calc_segment(self.locs[17], 2)] = s41
        self.segment_options[calc_segment(self.locs[18], 2)] = s42
        self.segment_options[calc_segment(self.locs[19], 2)] = s43

        self.segment_options[calc_segment(self.locs[20], 1)] = s44
        self.segment_options[calc_segment(self.locs[21], 1)] = s45
        self.segment_options[calc_segment(self.locs[22], 1)] = s46
        self.segment_options[calc_segment(self.locs[23], 1)] = s47
        self.segment_options[calc_segment(self.locs[24], 1)] = s48

        self.segment_options[calc_segment(self.locs[20], 4)] = s49
        self.segment_options[calc_segment(self.locs[20], 2)] = s50
        self.segment_options[calc_segment(self.locs[21], 2)] = s51
        self.segment_options[calc_segment(self.locs[22], 2)] = s52
        self.segment_options[calc_segment(self.locs[23], 2)] = s53
        self.segment_options[calc_segment(self.locs[24], 2)] = s54

        self.segment_options[calc_segment(self.locs[20], 3)] = s55
        self.segment_options[calc_segment(self.locs[21], 3)] = s56
        self.segment_options[calc_segment(self.locs[22], 3)] = s57
        self.segment_options[calc_segment(self.locs[23], 3)] = s58
        self.segment_options[calc_segment(self.locs[24], 3)] = s59

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
            propagate_segment_reduction(self.processor, segment)

    def _check_open_ends_1(self):
        #  verify each twoside open end can still be solved
        twoside_open = list()
        empty_nrs = [nr
                     for nr in range(len(self.locs))
                     if not self.board[nr]]
        empty_nrs.append(-2)        # internal open
        for p_nr in range(len(self.locs)):
            p2x2 = self.board[p_nr]
            if p2x2:
                neighs = self.neighbours[p_nr]

                if neighs[0] in empty_nrs:
                    twoside_open.append(p2x2.side1)
                if neighs[1] in empty_nrs:
                    twoside_open.append(p2x2.side2)
                if neighs[2] in empty_nrs:
                    twoside_open.append(p2x2.side3)
                if neighs[3] in empty_nrs:
                    twoside_open.append(p2x2.side4)
        # for

        qset = Piece2x2.objects.filter(nr1__in=self.board_unused, nr2__in=self.board_unused,
                                       nr3__in=self.board_unused, nr4__in=self.board_unused)
        # counts = dict()
        for side in set(twoside_open):
            # ensure we have a Piece2x2 that can connect to this side
            side_rev = self.twoside2reverse[side]
            p2x2 = qset.filter(side1=side_rev).first()
            if not p2x2:
                # no solution
                # print('[DEBUG] check_open_ends: out of options for side: %s' % repr(side))
                return False
            # counts[side] = qset.filter(side1=side_rev).count()
        # for

        # print('[DEBUG] check_open_ends: all good: %s' % repr(counts))
        return True

    def _check_open_ends(self):
        #  verify each location can still be filled
        qset = Piece2x2.objects.filter(nr1__in=self.board_unused, nr2__in=self.board_unused,
                                       nr3__in=self.board_unused, nr4__in=self.board_unused)

        for p_nr in range(len(self.locs)):
            if not self.board[p_nr]:
                # empty position on the board
                # check if it has neighbours that are filled
                neighs = self.neighbours[p_nr]
                qset2 = qset

                if neighs[0] >= 0:
                    # neighbour on side1
                    p2x2 = self.board[neighs[0]]
                    if p2x2:
                        qset2 = qset2.filter(side1=self.twoside2reverse[p2x2.side3])

                if neighs[1] >= 0:
                    # neighbour on side2
                    p2x2 = self.board[neighs[1]]
                    if p2x2:
                        qset2 = qset2.filter(side2=self.twoside2reverse[p2x2.side4])

                if neighs[2] >= 0:
                    # neighbour on side3
                    p2x2 = self.board[neighs[2]]
                    if p2x2:
                        qset2 = qset2.filter(side3=self.twoside2reverse[p2x2.side1])

                if neighs[3] >= 0:
                    # neighbour on side4
                    p2x2 = self.board[neighs[3]]
                    if p2x2:
                        qset2 = qset2.filter(side4=self.twoside2reverse[p2x2.side2])

                if qset2.first() is None:
                    # no solution
                    return False
        # for

        # all good
        return True

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
        for p_nr in range(len(self.locs)):
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
            # print(msg)
            self.progress.solve_order = msg
            self.progress.updated = timezone.now()
            self.progress.save(update_fields=['solve_order', 'updated'])

        if len(self.board_order) == len(self.locs):
            if self._check_progress_15min():
                self._save_progress_solution()
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

            if self._check_open_ends():
                found = self._find_recurse()
            else:
                found = False

            self._board_pop()

            if found:
                return True
        # for

        return False

    @staticmethod
    def _segment_to_loc(segment):
        """ reverse of calc_segment """
        if segment > 128:
            return segment - 129, 2
        else:
            return segment, 1

    def _find_reduce(self):
        sides = self.segment_options[self.segment]
        todo = len(sides)
        self.stdout.write('[INFO] Checking %s options in segment %s' % (len(sides), self.segment))
        self.p_nrs_order = self.requested_order[:]       # allow deciding optimal order anew

        loc, side_n = self._segment_to_loc(self.segment)
        p_nr = self.locs.index(loc)

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
                self._reduce(self.segment, side)

            todo -= 1
            self.stdout.write('[INFO] Remaining: %s/%s' % (todo, len(sides)))
            self.prev_tick = time.monotonic()
        # for

    def handle(self, *args, **options):
        """
                  s0           s1           s2            s3            s4
                +-----+      +-----+      +-----+       +-----+       +-----+
            s5  | p0  |  s6  | p1  |  s7  | p2  |  s8   | p3  |  s9   | p4  |  s10
                +-----+      +-----+      +-----+       +-----+       +-----+
                  s11          s12          s13           s14           s15
                +-----+      +-----+      +-----+       +-----+       +-----+
            s16 | p5  |  s17 | p6  |  s18 | p7  |  s19  | p8  |  s20  | p9  |  s21
                +-----+      +-----+      +-----+       +-----+       +-----+
                  s22          s23          s24           s25           s26
                +-----+      +-----+      +-----+       +-----+       +-----+
            s27 | p10 |  s28 | p11 |  s29 | p12 |  s30  | p13 |  s31  | p14 |  s32
                +-----+      +-----+      +-----+       +-----+       +-----+
                  s33          s34          s35           s36           s37
                +-----+      +-----+      +-----+       +-----+       +-----+
            s38 | p15 |  s39 | p16 |  s40 | p17 |  s41  | p18 |  s42  | p19 |  s43
                +-----+      +-----+      +-----+       +-----+       +-----+
                  s44          s45          s46           s47           s48
                +-----+      +-----+      +-----+       +-----+       +-----+
            s49 | p20 |  s50 | p21 |  s51 | p22 |  s52  | p23 |  s53  | p24 |  s54
                +-----+      +-----+      +-----+       +-----+       +-----+
                  s55          s56          s57           s58           s59
        """

        if options['dryrun']:
            self.do_commit = False

        self.processor = options['processor'][0]
        self.stdout.write('[INFO] Processor: %s' % self.processor)

        loc = options['loc'][0]
        if loc < 1 or loc > 28 or loc in (5, 6, 7, 8,
                                          13, 14, 15, 16,
                                          21, 22, 23, 24):
            self.stderr.write('[ERROR] Invalid location')
            return
        self.locs = (loc + 0, loc + 1, loc + 2, loc + 3, loc + 4,
                     loc + 8, loc + 9, loc + 10, loc + 11, loc + 12,
                     loc + 16, loc + 17, loc + 18, loc + 19, loc + 20,
                     loc + 24, loc + 25, loc + 26, loc + 27, loc + 28,
                     loc + 32, loc + 33, loc + 34, loc + 35, loc + 36)
        self.stdout.write('[INFO] Locations: %s' % repr(self.locs))

        self.segment = options['segment'][0]
        self.stdout.write('[INFO] Segment: %s' % self.segment)

        for loc in options['order']:
            if loc not in self.locs:
                self.stdout.write('[WARNING] Skipping invalid order: %s' % loc)
            elif loc not in self.requested_order:
                self.requested_order.append(self.locs.index(loc))
            else:
                self.stdout.write('[WARNING] Duplicate in requested order: %s' % loc)
        # for
        self.stdout.write('[INFO] Initial solve order: %s' % repr(self.requested_order))

        self._calc_unused0()
        self.board_unused = self.unused0[:]

        self._get_side_options()
        # self.stdout.write('%s' % ", ".join([str(len(opt)) for opt in self.side_options]))

        self.prev_tick = time.monotonic()

        self.progress = EvalProgress(
                        eval_size=25,
                        eval_loc=self.locs[0],
                        processor=self.processor,
                        segment=self.segment,
                        todo_count=0,
                        left_count=0,
                        solve_order='',
                        updated=timezone.now())
        self.progress.save()

        try:
            self._find_reduce()
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
