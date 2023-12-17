# -*- coding: utf-8 -*-

#  Copyright (c) 2023 Ramon van der Winkel.
#  All rights reserved.
#  Licensed under BSD-3-Clause-Clear. See LICENSE file for details.

from django.core.management.base import BaseCommand
from Pieces2x2.models import TwoSide, TwoSideOptions, Piece2x2
from Pieces2x2.helpers import calc_segment


class Command(BaseCommand):

    help = "Eval a possible reduction in TwoSideOptions for a square of 9 locations"

    """
              s0          s1          s2 
            +----+      +----+      +----+
        s3  | p0 |  s4  | p1 |  s5  | p2 |  s6 
            +----+      +----+      +----+
              s7          s8          s9
            +----+      +----+      +----+
        s10 | p3 |  s11 | p4 |  s12 | p5 |  s13
            +----+      +----+      +----+
              s14         s15        s16
            +----+      +----+      +----+
        s17 | p6 |  s18 | p7 |  s19 | p8 |  s20
            +----+      +----+      +----+
              s21         s22         s23
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

        self.do_commit = False

        self.neighbours = dict()    # [p_nr] = [p_nr on side1..4 or -1 if no neighbour]
        self.neighbours[0] = (-1, 1, 3, -1)
        self.neighbours[1] = (-1, 2, 4, 0)
        self.neighbours[2] = (-1, -1, 5, 1)
        self.neighbours[3] = (0, 4, 6, -1)
        self.neighbours[4] = (1, 3, 5, 7)
        self.neighbours[5] = (2, -1, 8, 4)
        self.neighbours[6] = (3, 7, -1, -1)
        self.neighbours[7] = (4, 8, -1, 6)
        self.neighbours[8] = (5, -1, -1, 7)

        self.side_nrs = dict()      # [p_nr] = [4 side nrs]
        self.side_nrs[0] = (0, 4, 7, 3)
        self.side_nrs[1] = (1, 5, 8, 4)
        self.side_nrs[2] = (2, 6, 9, 5)
        self.side_nrs[3] = (7, 11, 14, 10)
        self.side_nrs[4] = (8, 12, 15, 11)
        self.side_nrs[5] = (9, 13, 16, 12)
        self.side_nrs[6] = (14, 18, 21, 17)
        self.side_nrs[7] = (15, 19, 22, 18)
        self.side_nrs[8] = (16, 20, 23, 19)

        self.board = dict()          # [0..8] = None or Piece2x2 with side1/2/3/4
        self.board[0] = None
        self.board[1] = None
        self.board[2] = None
        self.board[3] = None
        self.board[4] = None
        self.board[5] = None
        self.board[6] = None
        self.board[7] = None
        self.board[8] = None
        self.board_order = list()   # solve order (for popping)
        self.board_unused = list()

    def add_arguments(self, parser):
        parser.add_argument('processor', nargs=1, type=int, help='Processor number to use')
        parser.add_argument('loc', nargs=1, type=int, help='Location on board (10..55)')
        parser.add_argument('--commit', action='store_true')

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
                  s0          s1          s2
                +----+      +----+      +----+
            s3  | p0 |  s4  | p1 |  s5  | p2 |  s6
                +----+      +----+      +----+
                  s7          s8          s9
                +----+      +----+      +----+
            s10 | p3 |  s11 | p4 |  s12 | p5 |  s13
                +----+      +----+      +----+
                  s14         s15        s16
                +----+      +----+      +----+
            s17 | p6 |  s18 | p7 |  s19 | p8 |  s20
                +----+      +----+      +----+
                  s21         s22         s23
        """
        s0 = self._get_loc_side_options(self.locs[0], 1)
        s1 = self._get_loc_side_options(self.locs[1], 1)
        s2 = self._get_loc_side_options(self.locs[2], 1)

        s3 = self._get_loc_side_options(self.locs[0], 4)
        s4 = self._get_loc_side_options(self.locs[1], 4)
        s5 = self._get_loc_side_options(self.locs[2], 4)
        s6 = self._get_loc_side_options(self.locs[2], 2)

        s7 = self._get_loc_side_options(self.locs[3], 1)
        s8 = self._get_loc_side_options(self.locs[4], 1)
        s9 = self._get_loc_side_options(self.locs[5], 1)

        s10 = self._get_loc_side_options(self.locs[3], 4)
        s11 = self._get_loc_side_options(self.locs[4], 4)
        s12 = self._get_loc_side_options(self.locs[5], 4)
        s13 = self._get_loc_side_options(self.locs[5], 2)

        s14 = self._get_loc_side_options(self.locs[6], 1)
        s15 = self._get_loc_side_options(self.locs[7], 1)
        s16 = self._get_loc_side_options(self.locs[8], 1)

        s17 = self._get_loc_side_options(self.locs[6], 4)
        s18 = self._get_loc_side_options(self.locs[7], 4)
        s19 = self._get_loc_side_options(self.locs[8], 4)
        s20 = self._get_loc_side_options(self.locs[8], 2)

        s21 = self._get_loc_side_options(self.locs[6], 3)
        s22 = self._get_loc_side_options(self.locs[7], 3)
        s23 = self._get_loc_side_options(self.locs[8], 3)

        self.side_options = [s0, s1, s2,
                             s3, s4, s5, s6,
                             s7, s8, s9,
                             s10, s11, s12, s13,
                             s14, s15, s16,
                             s17, s18, s19, s20,
                             s21, s22, s23]

        self.side_options_rev = [self._reverse_sides(s) for s in self.side_options]

    def _board_place(self, p_nr, p2x2):
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

    @staticmethod
    def _iter(unused1, options_side1, options_side2, options_side3, options_side4):
        for p in (Piece2x2
                  .objects
                  .filter(side1__in=options_side1,
                          side2__in=options_side2,
                          side3__in=options_side3,
                          side4__in=options_side4,
                          nr1__in=unused1,
                          nr2__in=unused1,
                          nr3__in=unused1,
                          nr4__in=unused1)):
            unused2 = unused1[:]
            unused2.remove(p.nr1)
            unused2.remove(p.nr2)
            unused2.remove(p.nr3)
            unused2.remove(p.nr4)
            yield p, unused2
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

        qset = Piece2x2.objects.filter(nr1__in=self.board_unused,
                                       nr2__in=self.board_unused,
                                       nr3__in=self.board_unused,
                                       nr4__in=self.board_unused)

        p_nr_counts = list()
        for p_nr in range(8+1):
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
        # for

        p_nr_counts.sort()  # smallest first
        tup = p_nr_counts[0]
        return tup[1]

    def _find_recurse(self):
        print(repr(self.board_order))
        if len(self.board_order) == 9:
            return True

        # decide which p_nr to continue with
        p_nr = self._select_p_nr()

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

        for p, _ in self._iter(self.board_unused, options_side1, options_side2, options_side3, options_side4):
            self._board_place(p_nr, p)
            found = self._find_recurse()
            self._board_pop()

            if found:
                return True
        # for

        return False

    def _find_reduce(self, side_n, s_nr, segment):
        p_nr = 4
        print('p_nr = %s' % p_nr)
        sides = self.side_options[s_nr]
        todo = len(sides)
        self.stdout.write('[INFO] Checking %s options in segment %s' % (len(sides), segment))
        for side in sides:
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
            for p, _ in self._iter(self.board_unused, options_side1, options_side2, options_side3, options_side4):
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
        # for

    def handle(self, *args, **options):

        """
                  s0          s1          s2
                +----+      +----+      +----+
            s3  | p0 |  s4  | p1 |  s5  | p2 |  s6
                +----+      +----+      +----+
                  s7          s8          s9
                +----+      +----+      +----+
            s10 | p3 |  s11 | p4 |  s12 | p5 |  s13
                +----+      +----+      +----+
                  s14         s15        s16
                +----+      +----+      +----+
            s17 | p6 |  s18 | p7 |  s19 | p8 |  s20
                +----+      +----+      +----+
                  s21         s22         s23
        """

        if options['commit']:
            self.do_commit = True

        loc = options['loc'][0]
        if loc < 10 or loc > 55 or loc in (17, 25, 33, 41, 49, 16, 24, 32, 40, 48):
            self.stderr.write('[ERROR] Invalid location')
            return
        self.locs = (loc - 9, loc - 8, loc - 7,
                     loc - 1, loc + 0, loc + 1,
                     loc + 7, loc + 8, loc + 9)
        self.stdout.write('[INFO] Locations: %s' % repr(self.locs))

        self.processor = options['processor'][0]
        self.stdout.write('[INFO] Processor=%s' % self.processor)

        self._calc_unused0()
        self.board_unused = self.unused0[:]

        self._get_side_options()
        # self.stdout.write('%s' % ", ".join([str(len(opt)) for opt in self.side_options]))

        self._find_reduce(1, 8, calc_segment(self.locs[4], 1))
        self._find_reduce(2, 12, calc_segment(self.locs[4], 2))
        self._find_reduce(3, 15, calc_segment(self.locs[4], 3))
        self._find_reduce(4, 11, calc_segment(self.locs[4], 4))

        if self.reductions == 0:
            self.stdout.write('[INFO] No reductions')
        else:
            self.stdout.write('[INFO] Reductions: %s' % self.reductions)
            if not self.do_commit:
                self.stdout.write('[WARNING] Use --commit to keep')

# end of file
