# -*- coding: utf-8 -*-

#  Copyright (c) 2023-2024 Ramon van der Winkel.
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
        | 9  | 10 |                   | 15 | 16 |
        +----+----+                   +----+----+
        | 17 |                             | 24 |
        +----+                             +----+
        | 25 |                             | 32 |
        +----+                             +----+
        | 33 |                             | 40 |
        +----+                             +----+
        | 41 |                             | 48 |
        +----+----+                   +----+----+
        | 49 | 50 |                   | 55 | 56 |
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
                     10, 15, 50, 55)

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

        # remove the hints not in Ring1
        self.unused0.remove(139)      # needed for loc 36
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

        self.segment_options = dict()
        self.segment_options_rev = dict()

    def add_arguments(self, parser):
        parser.add_argument('processor', type=int, help='Processor number to use')
        parser.add_argument('order', nargs='*', type=int, help='Solving order (1..64), max %s' % len(self.locs))

    def _calc_neighbours(self):
        neighbours = dict()

        # order of the entries: side 1, 2, 3, 4
        for nr in range(1, 64+1):
            if nr in self.locs:
                if nr == 36:
                    n = (-2, -2, -2, -2)
                else:
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

    def _iter(self, loc, options_side1, options_side2, options_side3, options_side4):

        unused = self.board_unused[:]
        if loc != 10 and 208 in unused:
            unused.remove(208)
        if loc != 15 and 255 in unused:
            unused.remove(255)
        if loc != 36 and 139 in unused:
            unused.remove(139)
        if loc != 50 and 181 in unused:
            unused.remove(181)
        if loc != 55 and 249 in unused:
            unused.remove(249)

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
                # print('loc=%s, segments=%s, %s, %s, %s' % (loc, seg1, seg2, seg3, seg4))
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

                if loc in (10, 15, 50, 55, 36):
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
                    # self.stdout.write('[DEBUG] No options for %s' % loc)
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

        for p in self._iter(loc, options_side1, options_side2, options_side3, options_side4):
            self._board_place(loc, p)

            self._find_recurse()

            self._board_pop()
        # for

    def handle(self, *args, **options):
        self.processor = options['processor']
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
            self.requested_order = [1, 2, 9,
                                    8, 7, 16,
                                    57, 58, 49,
                                    64, 63, 56,
                                    3, 24, 62, 41,
                                    4, 6, 5,
                                    32, 48, 40,
                                    61, 59, 60,
                                    17, 33, 25,
                                    10, 15, 50, 55]

        self.stdout.write('[INFO] Initial solve order: %s' % repr(self.requested_order))

        self._get_segments_options()

        try:
            self.solve_order = self.requested_order[:]
            self._find_recurse()
        except KeyboardInterrupt:
            pass

# end of file
