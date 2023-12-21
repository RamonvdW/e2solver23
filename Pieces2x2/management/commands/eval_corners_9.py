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

    help = "Eval a possible reduction in TwoSideOptions for a square of 9 locations in each corner"

    """
              s0           s1           s2                       s3           s4           s5 
            +-----+      +-----+      +-----+                  +-----+      +-----+      +-----+
        s6  | p0  |  s7  | p1  |  s8  | p2  | s9           s10 | p3  |  s11 | p4  |  s12 | p5  | s13
            +-----+      +-----+      +-----+                  +-----+      +-----+      +-----+
              s14          s15          s16                      s17          s18          s19
            +-----+      +-----+      +-----+                  +-----+      +-----+      +-----+
        s20 | p6  |  s21 | p7  |  s22 | p8  | s23          s24 | p9  |  s25 | p10 |  s26 | p11 | s27
            +-----+      +-----+      +-----+                  +-----+      +-----+      +-----+
              s28          s29          s30                      s31          s32          s33
            +-----+      +-----+      +-----+                  +-----+      +-----+      +-----+
        s34 | p12 |  s35 | p13 |  s36 | p14 | s37          s38 | p15 |  s39 | p16 |  s40 | p17 | s41
            +-----+      +-----+      +-----+                  +-----+      +-----+      +-----+
              s42          s43          s44                      s45          s46          s47


              s48          s40          s50                      s51          s52          s53
            +-----+      +-----+      +-----+                  +-----+      +-----+      +-----+
        s54 | p18 |  s55 | p19 |  s56 | p20 | s57          s58 | p21 |  s59 | p22 |  s60 | p23 | s61
            +-----+      +-----+      +-----+                  +-----+      +-----+      +-----+
              s62          s63          s64                      s65          s66          s67
            +-----+      +-----+      +-----+                  +-----+      +-----+      +-----+
        s68 | p24 |  s69 | p25 |  s70 | p26 | s71          s72 | p27 |  s73 | p28 |  s74 | p29 | s75
            +-----+      +-----+      +-----+                  +-----+      +-----+      +-----+
              s76          s77          s78                      s79          s80          s81
            +-----+      +-----+      +-----+                  +-----+      +-----+      +-----+
        s82 | p30 |  s83 | p31 |  s84 | p32 | s85          s86 | p33 |  s87 | p34 |  s88 | p35 | s89
            +-----+      +-----+      +-----+                  +-----+      +-----+      +-----+
              s90          s91          s92                      s93          s94          s95
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
        self.segment_options = dict()
        self.reductions = 0

        self.unused0 = list()

        self.do_commit = True

        # [p_nr] = [p_nr on side1..4 or -1 if no neighbour]
        self.neighbours: dict[int, tuple] = {0: (-1, 1, 6, -1),
                                             1: (-1, 2, 7, 0),
                                             2: (-1, -1, 8, 1),
                                             3: (-1, 4, 9, -1),
                                             4: (-1, 5, 10, 3),
                                             5: (-1, -1, 11, 4),
                                             6: (0, 7, 12, -1),
                                             7: (1, 8, 13, 6),
                                             8: (2, -1, 14, 7),
                                             9: (3, 10, 15, -1),
                                             10: (4, 11, 16, 9),
                                             11: (5, -1, 17, 10),
                                             12: (6, 13, -1, -1),
                                             13: (7, 14, -1, 12),
                                             14: (8, -1, -1, 13),
                                             15: (9, 16, -1, -1),
                                             16: (10, 17, -1, 15),
                                             17: (11, -1, -1, 16),
                                             18: (-1, 19, 24, -1),
                                             19: (-1, 20, 25, 18),
                                             20: (-1, -1, 26, 19),
                                             21: (-1, 22, 27, -1),
                                             22: (-1, 23, 28, 21),
                                             23: (-1, -1, 29, 22),
                                             24: (18, 19, 30, -1),
                                             25: (19, 20, 31, 24),
                                             26: (20, -1, 32, 25),
                                             27: (21, 22, 33, -1),
                                             28: (22, 23, 34, 27),
                                             29: (23, -1, 35, 28),
                                             30: (24, 31, -1, -1),
                                             31: (25, 32, -1, 30),
                                             32: (26, -1, -1, 31),
                                             33: (27, 34, -1, -1),
                                             34: (28, 35, -1, 33),
                                             35: (29, -1, -1, 34)}

        # [p_nr] = [4 side nr]
        self.side_nrs: dict[int, tuple] = {0: (0, 7, 14, 6),
                                           1: (1, 8, 15 ,7),
                                           2: (2, 9, 16, 8),
                                           3: (3, 11, 17, 10),
                                           4: (4, 12, 18, 11),
                                           5: (5, 13, 19, 12),
                                           6: (14, 21, 28, 20),
                                           7: (15, 22, 29, 21),
                                           8: (16, 23, 30, 22),
                                           9: (17, 25, 31, 24),
                                           10: (18, 26, 32, 25),
                                           11: (19, 27, 33, 26),
                                           12: (28, 35, 42, 34),
                                           13: (20, 36, 43, 35),
                                           14: (30, 37, 44, 36),
                                           15: (31, 39, 45, 38),
                                           16: (32, 40, 46, 39),
                                           17: (33, 41, 47, 40),
                                           18: (48, 55, 62, 54),
                                           19: (49, 56, 63, 55),
                                           20: (50, 57, 64, 56),
                                           21: (51, 59, 65, 58),
                                           22: (52, 60, 66, 59),
                                           23: (53, 61, 67, 60),
                                           24: (62, 69, 76, 68),
                                           25: (63, 70, 77, 69),
                                           26: (64, 71, 78, 70),
                                           27: (65, 73, 79, 72),
                                           28: (66, 74, 80, 73),
                                           29: (67, 75, 81, 74),
                                           30: (76, 83, 90, 82),
                                           31: (77, 84, 91, 83),
                                           32: (78, 85, 92, 84),
                                           33: (79, 87, 93, 86),
                                           34: (80, 88, 94, 87),
                                           35: (81, 89, 95, 88)}

        # [0..8] = None or Piece2x2 with side1/2/3/4
        self.board: dict[int, Piece2x2 | None] = {}
        for p_nr in range(36):
            self.board[p_nr] = None

        self.board_order = list()   # solve order (for popping)
        self.board_unused = list()
        self.p_nrs_order = list()
        self.prev_tick = 0
        self.progress = None

    def add_arguments(self, parser):
        parser.add_argument('processor', nargs=1, type=int, help='Processor number to use')
        parser.add_argument('segment', nargs=1, type=int, help='Segment to work on (1..72, 129..193)')
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
                  s0           s1           s2                       s3           s4           s5
                +-----+      +-----+      +-----+                  +-----+      +-----+      +-----+
            s6  | p0  |  s7  | p1  |  s8  | p2  | s9           s10 | p3  |  s11 | p4  |  s12 | p5  | s13
                +-----+      +-----+      +-----+                  +-----+      +-----+      +-----+
                  s14          s15          s16                      s17          s18          s19
                +-----+      +-----+      +-----+                  +-----+      +-----+      +-----+
            s20 | p6  |  s21 | p7  |  s22 | p8  | s23          s24 | p9  |  s25 | p10 |  s26 | p11 | s27
                +-----+      +-----+      +-----+                  +-----+      +-----+      +-----+
                  s28          s29          s30                      s31          s32          s33
                +-----+      +-----+      +-----+                  +-----+      +-----+      +-----+
            s34 | p12 |  s35 | p13 |  s36 | p14 | s37          s38 | p15 |  s39 | p16 |  s40 | p17 | s41
                +-----+      +-----+      +-----+                  +-----+      +-----+      +-----+
                  s42          s43          s44                      s45          s46          s47


                  s48          s40          s50                      s51          s52          s53
                +-----+      +-----+      +-----+                  +-----+      +-----+      +-----+
            s54 | p18 |  s55 | p19 |  s56 | p20 | s57          s58 | p21 |  s59 | p22 |  s60 | p23 | s61
                +-----+      +-----+      +-----+                  +-----+      +-----+      +-----+
                  s62          s63          s64                      s65          s66          s67
                +-----+      +-----+      +-----+                  +-----+      +-----+      +-----+
            s68 | p24 |  s69 | p25 |  s70 | p26 | s71          s72 | p27 |  s73 | p28 |  s74 | p29 | s75
                +-----+      +-----+      +-----+                  +-----+      +-----+      +-----+
                  s76          s77          s78                      s79          s80          s81
                +-----+      +-----+      +-----+                  +-----+      +-----+      +-----+
            s82 | p30 |  s83 | p31 |  s84 | p32 | s85          s86 | p33 |  s87 | p34 |  s88 | p35 | s89
                +-----+      +-----+      +-----+                  +-----+      +-----+      +-----+
                  s90          s91          s92                      s93          s94          s95
        """
        s0 = self._get_loc_side_options(self.locs[0], 1)
        s1 = self._get_loc_side_options(self.locs[1], 1)
        s2 = self._get_loc_side_options(self.locs[2], 1)
        s3 = self._get_loc_side_options(self.locs[3], 1)
        s4 = self._get_loc_side_options(self.locs[4], 1)
        s5 = self._get_loc_side_options(self.locs[5], 1)

        s14 = self._get_loc_side_options(self.locs[6], 1)
        s15 = self._get_loc_side_options(self.locs[7], 1)
        s16 = self._get_loc_side_options(self.locs[8], 1)
        s17 = self._get_loc_side_options(self.locs[9], 1)
        s18 = self._get_loc_side_options(self.locs[10], 1)
        s19 = self._get_loc_side_options(self.locs[11], 1)

        s28 = self._get_loc_side_options(self.locs[12], 1)
        s29 = self._get_loc_side_options(self.locs[13], 1)
        s30 = self._get_loc_side_options(self.locs[14], 1)
        s31 = self._get_loc_side_options(self.locs[15], 1)
        s32 = self._get_loc_side_options(self.locs[16], 1)
        s33 = self._get_loc_side_options(self.locs[17], 1)

        s42 = self._get_loc_side_options(self.locs[12], 3)
        s43 = self._get_loc_side_options(self.locs[13], 3)
        s44 = self._get_loc_side_options(self.locs[14], 3)
        s45 = self._get_loc_side_options(self.locs[15], 3)
        s46 = self._get_loc_side_options(self.locs[16], 3)
        s47 = self._get_loc_side_options(self.locs[17], 3)

        s48 = self._get_loc_side_options(self.locs[18], 1)
        s49 = self._get_loc_side_options(self.locs[19], 1)
        s50 = self._get_loc_side_options(self.locs[20], 1)
        s51 = self._get_loc_side_options(self.locs[21], 1)
        s52 = self._get_loc_side_options(self.locs[22], 1)
        s53 = self._get_loc_side_options(self.locs[23], 1)

        s62 = self._get_loc_side_options(self.locs[24], 1)
        s63 = self._get_loc_side_options(self.locs[25], 1)
        s64 = self._get_loc_side_options(self.locs[26], 1)
        s65 = self._get_loc_side_options(self.locs[27], 1)
        s66 = self._get_loc_side_options(self.locs[28], 1)
        s67 = self._get_loc_side_options(self.locs[29], 1)

        s76 = self._get_loc_side_options(self.locs[30], 1)
        s77 = self._get_loc_side_options(self.locs[31], 1)
        s78 = self._get_loc_side_options(self.locs[32], 1)
        s79 = self._get_loc_side_options(self.locs[33], 1)
        s80 = self._get_loc_side_options(self.locs[34], 1)
        s81 = self._get_loc_side_options(self.locs[35], 1)

        s90 = self._get_loc_side_options(self.locs[30], 3)
        s91 = self._get_loc_side_options(self.locs[31], 3)
        s92 = self._get_loc_side_options(self.locs[32], 3)
        s93 = self._get_loc_side_options(self.locs[33], 3)
        s94 = self._get_loc_side_options(self.locs[34], 3)
        s95 = self._get_loc_side_options(self.locs[35], 3)

        s6 = self._get_loc_side_options(self.locs[0], 4)
        s7 = self._get_loc_side_options(self.locs[0], 2)
        s8 = self._get_loc_side_options(self.locs[1], 2)
        s9 = self._get_loc_side_options(self.locs[2], 2)
        s10 = self._get_loc_side_options(self.locs[3], 4)
        s11 = self._get_loc_side_options(self.locs[3], 2)
        s12 = self._get_loc_side_options(self.locs[4], 2)
        s13 = self._get_loc_side_options(self.locs[5], 2)

        s20 = self._get_loc_side_options(self.locs[6], 4)
        s21 = self._get_loc_side_options(self.locs[6], 2)
        s22 = self._get_loc_side_options(self.locs[7], 2)
        s23 = self._get_loc_side_options(self.locs[8], 2)
        s24 = self._get_loc_side_options(self.locs[9], 4)
        s25 = self._get_loc_side_options(self.locs[9], 2)
        s26 = self._get_loc_side_options(self.locs[10], 2)
        s27 = self._get_loc_side_options(self.locs[11], 2)

        s34 = self._get_loc_side_options(self.locs[12], 4)
        s35 = self._get_loc_side_options(self.locs[12], 2)
        s36 = self._get_loc_side_options(self.locs[13], 2)
        s37 = self._get_loc_side_options(self.locs[14], 2)
        s38 = self._get_loc_side_options(self.locs[15], 4)
        s39 = self._get_loc_side_options(self.locs[15], 2)
        s40 = self._get_loc_side_options(self.locs[16], 2)
        s41 = self._get_loc_side_options(self.locs[17], 2)

        s54 = self._get_loc_side_options(self.locs[18], 4)
        s55 = self._get_loc_side_options(self.locs[18], 2)
        s56 = self._get_loc_side_options(self.locs[19], 2)
        s57 = self._get_loc_side_options(self.locs[20], 2)
        s58 = self._get_loc_side_options(self.locs[21], 4)
        s59 = self._get_loc_side_options(self.locs[21], 2)
        s60 = self._get_loc_side_options(self.locs[22], 2)
        s61 = self._get_loc_side_options(self.locs[23], 2)

        s68 = self._get_loc_side_options(self.locs[24], 4)
        s69 = self._get_loc_side_options(self.locs[24], 2)
        s70 = self._get_loc_side_options(self.locs[25], 2)
        s71 = self._get_loc_side_options(self.locs[26], 2)
        s72 = self._get_loc_side_options(self.locs[27], 4)
        s73 = self._get_loc_side_options(self.locs[27], 2)
        s74 = self._get_loc_side_options(self.locs[28], 2)
        s75 = self._get_loc_side_options(self.locs[29], 2)

        s82 = self._get_loc_side_options(self.locs[30], 4)
        s83 = self._get_loc_side_options(self.locs[30], 2)
        s84 = self._get_loc_side_options(self.locs[31], 2)
        s85 = self._get_loc_side_options(self.locs[32], 2)
        s86 = self._get_loc_side_options(self.locs[33], 4)
        s87 = self._get_loc_side_options(self.locs[33], 2)
        s88 = self._get_loc_side_options(self.locs[34], 2)
        s89 = self._get_loc_side_options(self.locs[35], 2)

        self.side_options = [s0, s1, s2, s3, s4, s5,
                             s6, s7, s8, s9, s10, s11, s12, s13,
                             s14, s15, s16, s17, s18, s19,
                             s20, s21, s22, s23, s24, s25, s26, s27,
                             s28, s29, s30, s31, s32, s33,
                             s34, s35, s36, s37, s38, s39, s40, s41,
                             s42, s43, s44, s45, s46, s47,
                             s48, s49, s50, s51, s52, s53,
                             s54, s55, s56, s57, s58, s59, s60, s61,
                             s62, s63, s64, s65, s66, s67,
                             s68, s69, s70, s71, s72, s73, s74, s75,
                             s76, s77, s78, s79, s80, s81,
                             s82, s83, s84, s85, s86, s87, s88, s89,
                             s90, s91, s92, s93, s94, s95]

        self.side_options_rev = [self._reverse_sides(s) for s in self.side_options]

        self.segment_options[calc_segment(self.locs[0], 1)] = s0
        self.segment_options[calc_segment(self.locs[1], 1)] = s1
        self.segment_options[calc_segment(self.locs[2], 1)] = s2
        self.segment_options[calc_segment(self.locs[3], 1)] = s3
        self.segment_options[calc_segment(self.locs[4], 1)] = s4
        self.segment_options[calc_segment(self.locs[5], 1)] = s5

        self.segment_options[calc_segment(self.locs[6], 1)] = s14
        self.segment_options[calc_segment(self.locs[7], 1)] = s15
        self.segment_options[calc_segment(self.locs[8], 1)] = s16
        self.segment_options[calc_segment(self.locs[9], 1)] = s17
        self.segment_options[calc_segment(self.locs[10], 1)] = s18
        self.segment_options[calc_segment(self.locs[11], 1)] = s19

        self.segment_options[calc_segment(self.locs[12], 1)] = s28
        self.segment_options[calc_segment(self.locs[13], 1)] = s29
        self.segment_options[calc_segment(self.locs[14], 1)] = s30
        self.segment_options[calc_segment(self.locs[15], 1)] = s31
        self.segment_options[calc_segment(self.locs[16], 1)] = s32
        self.segment_options[calc_segment(self.locs[17], 1)] = s33

        self.segment_options[calc_segment(self.locs[12], 3)] = s42
        self.segment_options[calc_segment(self.locs[13], 3)] = s43
        self.segment_options[calc_segment(self.locs[14], 3)] = s44
        self.segment_options[calc_segment(self.locs[15], 3)] = s45
        self.segment_options[calc_segment(self.locs[16], 3)] = s46
        self.segment_options[calc_segment(self.locs[17], 3)] = s47

        self.segment_options[calc_segment(self.locs[18], 1)] = s48
        self.segment_options[calc_segment(self.locs[19], 1)] = s49
        self.segment_options[calc_segment(self.locs[20], 1)] = s50
        self.segment_options[calc_segment(self.locs[21], 1)] = s51
        self.segment_options[calc_segment(self.locs[22], 1)] = s52
        self.segment_options[calc_segment(self.locs[23], 1)] = s53

        self.segment_options[calc_segment(self.locs[24], 1)] = s62
        self.segment_options[calc_segment(self.locs[25], 1)] = s63
        self.segment_options[calc_segment(self.locs[26], 1)] = s64
        self.segment_options[calc_segment(self.locs[27], 1)] = s65
        self.segment_options[calc_segment(self.locs[28], 1)] = s66
        self.segment_options[calc_segment(self.locs[29], 1)] = s67

        self.segment_options[calc_segment(self.locs[30], 1)] = s76
        self.segment_options[calc_segment(self.locs[31], 1)] = s77
        self.segment_options[calc_segment(self.locs[32], 1)] = s78
        self.segment_options[calc_segment(self.locs[33], 1)] = s79
        self.segment_options[calc_segment(self.locs[34], 1)] = s80
        self.segment_options[calc_segment(self.locs[35], 1)] = s81

        self.segment_options[calc_segment(self.locs[30], 3)] = s90
        self.segment_options[calc_segment(self.locs[31], 3)] = s91
        self.segment_options[calc_segment(self.locs[32], 3)] = s92
        self.segment_options[calc_segment(self.locs[33], 3)] = s93
        self.segment_options[calc_segment(self.locs[34], 3)] = s94
        self.segment_options[calc_segment(self.locs[35], 3)] = s95

        self.segment_options[calc_segment(self.locs[0], 4)] = s6
        self.segment_options[calc_segment(self.locs[0], 2)] = s7
        self.segment_options[calc_segment(self.locs[1], 2)] = s8
        self.segment_options[calc_segment(self.locs[2], 2)] = s9
        self.segment_options[calc_segment(self.locs[3], 4)] = s10
        self.segment_options[calc_segment(self.locs[3], 2)] = s11
        self.segment_options[calc_segment(self.locs[4], 2)] = s12
        self.segment_options[calc_segment(self.locs[5], 2)] = s13

        self.segment_options[calc_segment(self.locs[6], 4)] = s20
        self.segment_options[calc_segment(self.locs[6], 2)] = s21
        self.segment_options[calc_segment(self.locs[7], 2)] = s22
        self.segment_options[calc_segment(self.locs[8], 2)] = s23
        self.segment_options[calc_segment(self.locs[9], 4)] = s24
        self.segment_options[calc_segment(self.locs[9], 2)] = s25
        self.segment_options[calc_segment(self.locs[10], 2)] = s26
        self.segment_options[calc_segment(self.locs[11], 2)] = s27

        self.segment_options[calc_segment(self.locs[12], 4)] = s34
        self.segment_options[calc_segment(self.locs[12], 2)] = s35
        self.segment_options[calc_segment(self.locs[13], 2)] = s36
        self.segment_options[calc_segment(self.locs[14], 2)] = s37
        self.segment_options[calc_segment(self.locs[15], 4)] = s38
        self.segment_options[calc_segment(self.locs[15], 2)] = s39
        self.segment_options[calc_segment(self.locs[16], 2)] = s40
        self.segment_options[calc_segment(self.locs[17], 2)] = s41

        self.segment_options[calc_segment(self.locs[18], 4)] = s54
        self.segment_options[calc_segment(self.locs[18], 2)] = s55
        self.segment_options[calc_segment(self.locs[19], 2)] = s56
        self.segment_options[calc_segment(self.locs[20], 2)] = s57
        self.segment_options[calc_segment(self.locs[21], 4)] = s58
        self.segment_options[calc_segment(self.locs[21], 2)] = s59
        self.segment_options[calc_segment(self.locs[22], 2)] = s60
        self.segment_options[calc_segment(self.locs[23], 2)] = s61

        self.segment_options[calc_segment(self.locs[24], 4)] = s68
        self.segment_options[calc_segment(self.locs[24], 2)] = s69
        self.segment_options[calc_segment(self.locs[25], 2)] = s70
        self.segment_options[calc_segment(self.locs[26], 2)] = s71
        self.segment_options[calc_segment(self.locs[27], 4)] = s72
        self.segment_options[calc_segment(self.locs[27], 2)] = s73
        self.segment_options[calc_segment(self.locs[28], 2)] = s74
        self.segment_options[calc_segment(self.locs[29], 2)] = s75

        self.segment_options[calc_segment(self.locs[30], 4)] = s82
        self.segment_options[calc_segment(self.locs[30], 2)] = s83
        self.segment_options[calc_segment(self.locs[31], 2)] = s84
        self.segment_options[calc_segment(self.locs[32], 2)] = s85
        self.segment_options[calc_segment(self.locs[33], 4)] = s86
        self.segment_options[calc_segment(self.locs[33], 2)] = s87
        self.segment_options[calc_segment(self.locs[34], 2)] = s88
        self.segment_options[calc_segment(self.locs[35], 2)] = s89

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
        for p_nr in range(36):
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

        if len(self.board_order) == 36:
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
        self.p_nrs_order = list()       # allow deciding optimal order anew
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
                  s0           s1           s2                       s3           s4           s5
                +-----+      +-----+      +-----+                  +-----+      +-----+      +-----+
            s6  | p0  |  s7  | p1  |  s8  | p2  | s9           s10 | p3  |  s11 | p4  |  s12 | p5  | s13
                +-----+      +-----+      +-----+                  +-----+      +-----+      +-----+
                  s14          s15          s16                      s17          s18          s19
                +-----+      +-----+      +-----+                  +-----+      +-----+      +-----+
            s20 | p6  |  s21 | p7  |  s22 | p8  | s23          s24 | p9  |  s25 | p10 |  s26 | p11 | s27
                +-----+      +-----+      +-----+                  +-----+      +-----+      +-----+
                  s28          s29          s30                      s31          s32          s33
                +-----+      +-----+      +-----+                  +-----+      +-----+      +-----+
            s34 | p12 |  s35 | p13 |  s36 | p14 | s37          s38 | p15 |  s39 | p16 |  s40 | p17 | s41
                +-----+      +-----+      +-----+                  +-----+      +-----+      +-----+
                  s42          s43          s44                      s45          s46          s47


                  s48          s40          s50                      s51          s52          s53
                +-----+      +-----+      +-----+                  +-----+      +-----+      +-----+
            s54 | p18 |  s55 | p19 |  s56 | p20 | s57          s58 | p21 |  s59 | p22 |  s60 | p23 | s61
                +-----+      +-----+      +-----+                  +-----+      +-----+      +-----+
                  s62          s63          s64                      s65          s66          s67
                +-----+      +-----+      +-----+                  +-----+      +-----+      +-----+
            s68 | p24 |  s69 | p25 |  s70 | p26 | s71          s72 | p27 |  s73 | p28 |  s74 | p29 | s75
                +-----+      +-----+      +-----+                  +-----+      +-----+      +-----+
                  s76          s77          s78                      s79          s80          s81
                +-----+      +-----+      +-----+                  +-----+      +-----+      +-----+
            s82 | p30 |  s83 | p31 |  s84 | p32 | s85          s86 | p33 |  s87 | p34 |  s88 | p35 | s89
                +-----+      +-----+      +-----+                  +-----+      +-----+      +-----+
                  s90          s91          s92                      s93          s94          s95
        """
        if options['dryrun']:
            self.do_commit = False

        self.locs = (1, 2, 3, 6, 7, 8,
                     9, 10, 11, 14, 15, 16,
                     17, 18, 19, 22, 23, 24,
                     41, 42, 43, 46, 47, 48,
                     49, 50, 51, 54, 55, 56,
                     57, 58, 59, 62, 63, 64)
        self.stdout.write('[INFO] Locations: %s' % repr(self.locs))

        self.processor = options['processor'][0]
        self.stdout.write('[INFO] Processor: %s' % self.processor)

        self.segment = options['segment'][0]
        self.stdout.write('[INFO] Segment: %s' % self.segment)

        self._calc_unused0()
        self.board_unused = self.unused0[:]

        self._get_side_options()
        # self.stdout.write('%s' % ", ".join([str(len(opt)) for opt in self.side_options]))

        self.prev_tick = time.monotonic()

        self.progress = EvalProgress(
                        eval_size=36,
                        eval_loc=1,
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
