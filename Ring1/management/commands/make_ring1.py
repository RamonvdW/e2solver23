# -*- coding: utf-8 -*-

#  Copyright (c) 2023 Ramon van der Winkel.
#  All rights reserved.
#  Licensed under BSD-3-Clause-Clear. See LICENSE file for details.

from django.core.management.base import BaseCommand
from Pieces2x2.models import TwoSide, TwoSideOptions, Piece2x2
from Pieces2x2.helpers import calc_segment
from Ring1.models import Ring1
import time


class Command(BaseCommand):

    help = "Make all possible combinations of ring1, the outer 2x2 ring"

    """
        +----+----+----+----+----+----+----+----+
        | 1  | 2  | 3  | 4  | 5  | 6  | 7  | 8  |
        +----+----+----+----+----+----+----+----+
        | 9  |                             | 16 |
        +----+                             +----+
        | 17 |                             | 24 |
        +----+                             +----+
        | 25 |                             | 32 |
        +----+                             +----+
        | 33 |                             | 40 |
        +----+                             +----+
        | 41 |                             | 48 |
        +----+                             +----+
        | 49 |                             | 56 |
        +----+----+----+----+----+----+----+----+
        | 57 | 58 | 59 | 60 | 61 | 62 | 63 | 64 |
        +----+----+----+----+----+----+----+----+
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
        self.locs = (1, 2, 3, 4, 5, 6, 7, 8,
                     9, 16,
                     17, 24,
                     25, 32,
                     33, 40,
                     41, 48,
                     49, 56,
                     57, 58, 59, 60, 61, 62, 63, 64,
                     10, 15, 50, 55,
                     42, 51, 11, 18, 14, 23, 47, 54)

        # [loc] = [loc on side1..4 or -1 if border or -2 if neighbour is a gap]
        self.neighbours = self._calc_neighbours()

        # [loc] = [4 side nr]
        self.segment_nrs: dict[int, tuple] = dict()
        for loc in self.locs:
            self.segment_nrs[loc] = (calc_segment(loc, 1),
                                     calc_segment(loc, 2),
                                     calc_segment(loc, 3),
                                     calc_segment(loc, 4))
        # for

        self.unused0 = list(range(1, 256+1))
        # none of the hints are in Ring1
        self.unused0.remove(139)
        # self.unused0.remove(208)      # needed for loc 10
        # self.unused0.remove(255)      # needed for loc 15
        # self.unused0.remove(181)      # needed for loc 50
        # self.unused0.remove(249)      # needed for loc 55

        # [1..64] = None or Piece2x2 with side1/2/3/4
        self.board: dict[int, Piece2x2 | None] = {}
        for loc in self.locs:
            self.board[loc] = None

        self.solve_order = list()
        self.board_order = list()   # solved order (for popping)
        self.board_unused = self.unused0[:]
        self.requested_order = list()

        self.prev_tick = time.monotonic()

        self.p10_sides = list()     # list of tuples: (side4, side1)
        self.p15_sides = list()     # list of tuples: (side1, side2)
        self.p55_sides = list()     # list of tuples: (side2, side3)
        self.p50_sides = list()     # list of tuples: (side3, side4)

        self.segment_options = dict()
        self.segment_options_rev = dict()

    def add_arguments(self, parser):
        parser.add_argument('processor', nargs=1, type=int, help='Processor number to use')
        parser.add_argument('start10', nargs=1, type=int, help='Start index for p10 (1..500)')
        parser.add_argument('start15', nargs=1, type=int, help='Start index for p15 (1..500)')
        parser.add_argument('start50', nargs=1, type=int, help='Start index for p50 (1..500)')
        parser.add_argument('start55', nargs=1, type=int, help='Start index for p55 (1..500)')
        parser.add_argument('order', nargs='*', type=int, help='Solving order (1..64), max %s' % len(self.locs))

    def _calc_neighbours(self):
        neighbours = dict()

        # order of the entries: side 1, 2, 3, 4
        for nr in range(1, 64+1):
            if nr in self.locs:
                n = list()
                col = (nr - 1) % 8
                row = int((nr - 1) / 8)

                # side 1
                if row == 0:
                    n.append(-1)    # outer border
                elif nr - 8 in self.locs:
                    n.append(nr - 8)
                else:
                    n.append(-2)    # inner gap

                # side 2
                if col == 7:
                    n.append(-1)    # outer border
                elif nr + 1 in self.locs:
                    n.append(nr + 1)
                else:
                    n.append(-2)    # inner gap

                # side 3
                if row == 7:
                    n.append(-1)    # outer border
                elif nr + 8 in self.locs:
                    n.append(nr + 8)
                else:
                    n.append(-2)    # inner gap

                # side 4
                if col == 0:
                    n.append(-1)    # outer border
                elif nr - 1 in self.locs:
                    n.append(nr - 1)
                else:
                    n.append(-2)    # inner gap

                neighbours[nr] = tuple(n)
        # for
        return neighbours

    def _reverse_sides(self, options):
        return [self.twoside2reverse[two_side] for two_side in options]

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

    def _save_ring1(self):
        ring = Ring1()
        for loc in self.locs:
            field = 'nr%s' % loc
            setattr(ring, field, self.board[loc].nr)
        # for
        ring.save()
        self.stdout.write('[INFO] Saved Ring1 with pk=%s' % ring.pk)

    def _query_segment_options(self, segment):
        """ Return the options remaining for a specific segment """
        options = (TwoSideOptions
                   .objects
                   .filter(processor=self.processor,
                           segment=segment)
                   .values_list('two_side', flat=True))
        options = list(options)
        # self.stdout.write('[DEBUG] Segment %s has %s options' % (segment, len(options)))
        return options

    def _get_segments_options(self):
        for loc in self.locs:
            for side in range(1, 4+1):
                segment = calc_segment(loc, side)
                options = self._query_segment_options(segment)
                self.segment_options[segment] = options
                self.segment_options_rev[segment] = self._reverse_sides(options)
        # for

    def _get_hint_sides(self):
        """ find all combinations of 2 sides of the 2x2 with the hint pieces, facing the ring1 """
        p10_sides4 = self.segment_options[138]
        p10_sides1 = self.segment_options[10]
        self.p10_sides = list(Piece2x2.objects
                              .filter(side4__in=p10_sides4, side1__in=p10_sides1, has_hint=True, nr1=208)
                              .distinct('side4', 'side1')
                              .values_list('side4', 'side1'))

        p15_sides1 = self.segment_options[15]
        p15_sides2 = self.segment_options[144]
        self.p15_sides = list(Piece2x2.objects
                              .filter(side1__in=p15_sides1, side2__in=p15_sides2, has_hint=True, nr2=255)
                              .distinct('side1', 'side2')
                              .values_list('side1', 'side2'))

        p55_sides2 = self.segment_options[184]
        p55_sides3 = self.segment_options_rev[63]
        self.p55_sides = list(Piece2x2.objects
                              .filter(side2__in=p55_sides2, side3__in=p55_sides3, has_hint=True, nr4=249)
                              .distinct('side2', 'side3')
                              .values_list('side2', 'side3'))

        p50_sides3 = self.segment_options_rev[58]
        p50_sides4 = self.segment_options_rev[178]
        self.p50_sides = list(Piece2x2.objects
                              .filter(side3__in=p50_sides3, side4__in=p50_sides4, has_hint=True, nr3=181)
                              .distinct('side3', 'side4')
                              .values_list('side3', 'side4'))

    def _iter(self, options_side1, options_side2, options_side3, options_side4):
        qset = (Piece2x2
                .objects
                .filter(nr1__in=self.board_unused,
                        nr2__in=self.board_unused,
                        nr3__in=self.board_unused,
                        nr4__in=self.board_unused))

        if options_side1:
            qset = qset.filter(side1__in=options_side1)
        if options_side2:
            qset = qset.filter(side2__in=options_side2)
        if options_side3:
            qset = qset.filter(side3__in=options_side3)
        if options_side4:
            qset = qset.filter(side4__in=options_side4)

        # todo = qset.count()
        # print('todo: %s' % todo)

        for p in qset:
            yield p
        # for

    def _select_next_loc(self):
        # decide which position on the board has the fewest options

        # follow previous solve order
        for loc in self.solve_order:
            if self.board[loc] is None:
                return loc, False
        # for

        # decide the next best position on the board to solve

        qset = Piece2x2.objects.filter(nr1__in=self.board_unused,
                                       nr2__in=self.board_unused,
                                       nr3__in=self.board_unused,
                                       nr4__in=self.board_unused)

        loc_counts = list()
        for loc in self.locs:
            if self.board[loc] is None:
                # empty position on the board
                seg1, seg2, seg3, seg4 = self.segment_nrs[loc]
                # print('loc=%s, segs=%s, %s, %s, %s' % (loc, seg1, seg2, seg3, seg4))
                options_side1 = self.segment_options[seg1]
                options_side2 = self.segment_options[seg2]
                options_side3 = self.segment_options_rev[seg3]
                options_side4 = self.segment_options_rev[seg4]

                n1, n2, n3, n4 = self.neighbours[loc]
                if n1 > 0:
                    p = self.board[n1]
                    if p:
                        options_side1 = [self.twoside2reverse[p.side3]]
                if n2 > 0:
                    p = self.board[n2]
                    if p:
                        options_side2 = [self.twoside2reverse[p.side4]]
                if n3 > 0:
                    p = self.board[n3]
                    if p:
                        options_side3 = [self.twoside2reverse[p.side1]]
                if n4 > 0:
                    p = self.board[n4]
                    if p:
                        options_side4 = [self.twoside2reverse[p.side2]]

                if loc in (10, 15, 50, 55):
                    count = qset.filter(has_hint=True,
                                        side1__in=options_side1,
                                        side2__in=options_side2,
                                        side3__in=options_side3,
                                        side4__in=options_side4).count()
                else:
                    count = qset.filter(is_border=True,
                                        side1__in=options_side1,
                                        side2__in=options_side2,
                                        side3__in=options_side3,
                                        side4__in=options_side4).count()
                tup = (count, loc)
                loc_counts.append(tup)

                if count == 0:
                    # dead end
                    self.stdout.write('[DEBUG] No options for %s' % loc)
                    return -1, True
        # for

        # take the lowest
        if len(loc_counts) > 0:
            loc_counts.sort()       # lowest first
            loc = loc_counts[0][-1]
            # self.stdout.write('[INFO] Added %s' % p_nr)
            self.solve_order.append(loc)
            return loc, False

        # niets kunnen kiezen
        self.stdout.write('[ERROR] select_next_loc failed')
        self.stdout.write('[DEBUG] solve_order = %s' % repr(self.board_order))
        return -1, True

    def _find_recurse(self):
        tick = time.monotonic()
        if tick - self.prev_tick > 10:
            self.prev_tick = tick
            msg = '(%s) %s' % (len(self.board_order), repr(self.board_order))
            print(msg)

        if len(self.board_order) == len(self.locs):
            self._save_ring1()
            return

        # decide which loc to continue with
        loc, has_zero = self._select_next_loc()
        if has_zero:
            return
        # self.stdout.write('next loc: %s' % loc)

        seg1, seg2, seg3, seg4 = self.segment_nrs[loc]
        options_side1 = self.segment_options[seg1]
        options_side2 = self.segment_options[seg2]
        options_side3 = self.segment_options_rev[seg3]
        options_side4 = self.segment_options_rev[seg4]

        n1, n2, n3, n4 = self.neighbours[loc]
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
            self._board_place(loc, p)

            self._find_recurse()

            self._board_pop()
        # for

    def _find_ring1(self, seg138, seg10, seg15, seg144, seg184, seg63, seg58, seg178):
        self.stdout.write('[INFO] Find ring1 starting with 10=%s,%s, 15=%s,%s, 55=%s,%s, 50=%s,%s' % (
                            seg138, seg10, seg15, seg144, seg184, seg63, seg58, seg178))

        # load the limited segment options
        self.segment_options[138] = [seg138]
        self.segment_options[10] = [seg10]
        self.segment_options[15] = [seg15]
        self.segment_options[144] = [seg144]
        self.segment_options[184] = [seg184]
        self.segment_options[63] = [seg63]
        self.segment_options[58] = [seg58]
        self.segment_options[178] = [seg178]

        for seg in (138, 10, 15, 144, 184, 63, 58, 178):
            self.segment_options_rev[seg] = self._reverse_sides(self.segment_options[seg])
        # for

        self.solve_order = self.requested_order[:]
        self._find_recurse()

    def handle(self, *args, **options):
        self.processor = options['processor'][0]
        self.stdout.write('[INFO] Processor: %s' % self.processor)

        for loc in options['order']:
            if loc not in self.locs:
                self.stdout.write('[WARNING] Skipping invalid order: %s' % loc)
            elif loc not in self.requested_order:
                self.requested_order.append(loc)
            else:
                self.stdout.write('[WARNING] Duplicate in requested order: %s' % loc)
        # for

        if len(self.requested_order) == 0:
            self.requested_order = [10, 2, 1, 9, 11, 3, 18, 17,
                                    15, 7, 8, 16, 14, 6, 23, 24,
                                    50, 49, 57, 58, 42, 41, 51, 59,
                                    55, 56, 64, 63, 47, 48, 54, 62]

        self.stdout.write('[INFO] Initial solve order: %s' % repr(self.requested_order))

        self._get_segments_options()
        self._get_hint_sides()

        start10 = options['start10'][0]
        start15 = options['start15'][0]
        start50 = options['start50'][0]
        start55 = options['start55'][0]

        self.stdout.write('[INFO] p10_sides: %s/%s' % (start10, len(self.p10_sides)))
        self.stdout.write('[INFO] p15_sides: %s/%s' % (start15, len(self.p15_sides)))
        self.stdout.write('[INFO] p50_sides: %s/%s' % (start50, len(self.p50_sides)))
        self.stdout.write('[INFO] p55_sides: %s/%s' % (start55, len(self.p55_sides)))
        # self.stdout.write('[INFO] total: %s' % (
        #                   len(self.p10_sides) * len(self.p15_sides) * len(self.p55_sides) * len(self.p50_sides)))

        p10_s4, p10_s1 = self.p10_sides[start10 - 1]
        p15_s1, p15_s2 = self.p15_sides[start15 - 1]
        p50_s3, p50_s4 = self.p50_sides[start50 - 1]
        p55_s2, p55_s3 = self.p55_sides[start55 - 1]

        try:
            self._find_ring1(
                    self.twoside2reverse[p10_s4], p10_s1,
                    p15_s1, p15_s2,
                    p55_s2, self.twoside2reverse[p55_s3],
                    self.twoside2reverse[p50_s3], self.twoside2reverse[p50_s4])
        except KeyboardInterrupt:
            pass

# end of file
