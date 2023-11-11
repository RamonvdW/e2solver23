# -*- coding: utf-8 -*-

#  Copyright (c) 2023 Ramon van der Winkel.
#  All rights reserved.
#  Licensed under BSD-3-Clause-Clear. See LICENSE file for details.

from django.core.management.base import BaseCommand
from BasePieces.models import BasePiece
from Borders4x2.models import Border4x2
from BorderSolutions.models import BorderSolution
from Pieces2x2.models import TwoSides, Piece2x2
from Pieces4x4.models import Piece4x4
from Ring4.models import Ring4


class Command(BaseCommand):

    help = "Generate Ring4 solutions from BorderSolution and central Piece2x2"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # cache all base pieces
        self.base_pieces = dict()       # [nr] = BasePiece()
        for piece in BasePiece.objects.all():
            self.base_pieces[piece.nr] = piece
        # for

        # load all TwoSides
        self.two_sides2nr = dict()   # ['XX'] = nr
        for two in TwoSides.objects.all():
            self.two_sides2nr[two.two_sides] = two.nr
        # for

        self.side_nr2reverse = dict()       # [side nr] = reverse side nr
        for two in TwoSides.objects.all():
            reverse = two.two_sides[1] + two.two_sides[0]
            try:
                self.side_nr2reverse[two.nr] = self.two_sides2nr[reverse]
            except KeyError:
                self.side_nr2reverse[two.nr] = 9999   # bestaat niet
        # for

        self.counter_rot = {
            0: 0,
            1: 3,
            2: 2,
            3: 1
        }

        self.nr = 0

    def _set_4x4_side2b_side3a(self, piece4x4):
        p12 = self.base_pieces[piece4x4.nr12]
        p15 = self.base_pieces[piece4x4.nr15]
        p16 = self.base_pieces[piece4x4.nr16]

        side2b_reverse = p16.get_side(2, piece4x4.rot16) + p12.get_side(2, piece4x4.rot12)
        piece4x4.side2b = self.two_sides2nr[side2b_reverse]

        side3a_reverse = p15.get_side(3, piece4x4.rot15) + p16.get_side(3, piece4x4.rot16)
        piece4x4.side3a = self.two_sides2nr[side3a_reverse]

    def _set_4x2_side3a_side3b(self, border4x2):
        # side3 = "8765"
        border4x2.side3a = self.two_sides2nr[border4x2.side3[1] + border4x2.side3[0]]  # 7+8
        border4x2.side3b = self.two_sides2nr[border4x2.side3[3] + border4x2.side3[2]]  # 5+6

    def _find_correct_2x2(self, piece2x2, rot):
        # rot = number of clockwise rotation
        """
            +---+---+       +---+---+
            | 1 | 2 |       | 3 | 1 |
            +---+---+  -->  +---+---+
            | 3 | 4 |       | 4 | 2 |
            +---+---+       +---+---+
        """
        # print('correct_2x2: nr=%s, rot=%s' % (piece2x2.nr, rot))

        # piece2x2 exist in groups of 4 in counter-rotating increments
        nr = piece2x2.nr
        nr_rot = (nr - 1) % 4
        group = nr - nr_rot
        # print('      group: %s' % group)
        # print('     nr_rot: %s' % nr_rot)

        guess = group + (nr_rot + self.counter_rot[rot]) % 4
        # print('      guess: %s' % guess)
        return guess

        # nr1, nr2, nr3, nr4 = piece2x2.nr1, piece2x2.nr2, piece2x2.nr3, piece2x2.nr4
        # rot1, rot2, rot3, rot4 = piece2x2.rot1, piece2x2.rot2, piece2x2.rot3, piece2x2.rot4
        #
        # rot1 -= rot
        # rot2 -= rot
        # rot3 -= rot
        # rot4 -= rot
        #
        # if rot1 < 0:
        #     rot1 += 4
        # if rot2 < 0:
        #     rot2 += 4
        # if rot3 < 0:
        #     rot3 += 4
        # if rot4 < 0:
        #     rot4 += 4
        #
        # while rot > 0:
        #     rot -= 1
        #     nr1, nr2, nr3, nr4 = nr3, nr1, nr4, nr2
        #     rot1, rot2, rot3, rot4 = rot3, rot1, rot4, rot2
        # # while
        #
        # correct = Piece2x2.objects.get(nr1=nr1, nr2=nr2, nr3=nr3, nr4=nr4,
        #                                rot1=rot1, rot2=rot2, rot3=rot3, rot4=rot4)
        #
        # print('correct 2x2: %s --> %s' % (piece2x2.nr, correct.nr))
        # return correct.nr

    def _find_correct_2x2s(self, tup, rot):
        p1, p2, p3, p4 = tup
        p1 = self._find_correct_2x2(p1, rot)
        p2 = self._find_correct_2x2(p2, rot)
        p3 = self._find_correct_2x2(p3, rot)
        p4 = self._find_correct_2x2(p4, rot)
        return p1, p2, p3, p4

    @staticmethod
    def _test_piece2x2(used_nrs, exp_side4, exp_side1):
        # assert isinstance(exp_side4, int)
        # assert isinstance(exp_side1, int)
        for _ in (Piece2x2
                  .objects
                  .filter(side4=exp_side4,
                          side1=exp_side1)
                  .exclude(nr1__in=used_nrs)
                  .exclude(nr2__in=used_nrs)
                  .exclude(nr3__in=used_nrs)
                  .exclude(nr4__in=used_nrs)
                  .iterator(chunk_size=10)):
            # found a solution
            return True
        # for

        # nothing found
        return False

    @staticmethod
    def _iter_2x2_side4_1(used_nrs, exp_side4, exp_side1):
        for p in (Piece2x2
                  .objects
                  .filter(side4=exp_side4,
                          side1=exp_side1)
                  .exclude(nr1__in=used_nrs)
                  .exclude(nr2__in=used_nrs)
                  .exclude(nr3__in=used_nrs)
                  .exclude(nr4__in=used_nrs)
                  .iterator(chunk_size=1000)):

            used_nrs2 = used_nrs + (p.nr1, p.nr2, p.nr3, p.nr4)
            yield p, used_nrs2
        # for

    @staticmethod
    def _iter_2x2_side1_2(used_nrs, exp_side1, exp_side2):
        for p in (Piece2x2
                  .objects
                  .filter(side1=exp_side1,
                          side2=exp_side2)
                  .exclude(nr1__in=used_nrs)
                  .exclude(nr2__in=used_nrs)
                  .exclude(nr3__in=used_nrs)
                  .exclude(nr4__in=used_nrs)
                  .iterator(chunk_size=1000)):

            used_nrs2 = used_nrs + (p.nr1, p.nr2, p.nr3, p.nr4)
            yield p, used_nrs2
        # for

    @staticmethod
    def _iter_2x2_side4_1_2(used_nrs, exp_side4, exp_side1, exp_side2):
        for p in (Piece2x2
                  .objects
                  .filter(side4=exp_side4,
                          side1=exp_side1,
                          side2=exp_side2)
                  .exclude(nr1__in=used_nrs)
                  .exclude(nr2__in=used_nrs)
                  .exclude(nr3__in=used_nrs)
                  .exclude(nr4__in=used_nrs)
                  .iterator(chunk_size=1000)):

            yield p
        # for

    def _iter_ring2(self, used_nrs0, c1, b1, b2, c2):
        """"
              +--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
              |  Piece4x4 | Border4x2 | Border4x2 |  Piece4x4 |
              +         2a+     b1    +     b2    +3b         +
              |           |  3b    3a |  3b    3a |           |
              +    c1     +--+--+--+--+--+--+--+--+     c2    +
              |           |     |     |     |     |           |
              +         2b+  p1 +  p2 +  p3 +  p4 +3a         +
              | 3b    3a  |     |     |     |     |  2b    2a |
              +--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
        """
        for p1, used_nrs1 in self._iter_2x2_side4_1(used_nrs0, c1.side2b, b1.side3b):
            for p4, used_nrs2 in self._iter_2x2_side1_2(used_nrs1, b2.side3a, c2.side3a):
                p2_exp_s4 = self.side_nr2reverse[p1.side2]
                for p2, used_nrs3 in self._iter_2x2_side4_1(used_nrs2, p2_exp_s4, b1.side3a):
                    p3_exp_s4 = self.side_nr2reverse[p2.side2]
                    p3_exp_s2 = self.side_nr2reverse[p4.side4]
                    for p3 in self._iter_2x2_side4_1_2(used_nrs3, p3_exp_s4, b2.side3b, p3_exp_s2):

                        used_nrs = (p1.nr1, p1.nr2, p1.nr3, p1.nr4,
                                    p2.nr1, p2.nr2, p2.nr3, p2.nr4,
                                    p3.nr1, p3.nr2, p3.nr3, p3.nr4,
                                    p4.nr1, p4.nr2, p4.nr3, p4.nr4)

                        yield p1, p2, p3, p4, used_nrs
                    # for
                # for
            # for
        # for

    def _find_ring4(self, sol, sol_nrs, c1, c2, c3, c4, b1, b2, b3, b4, b5, b6, b7, b8):
        """
                   Border Solution:

              +--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
              |  Piece4x4 | Border4x2 | Border4x2 |  Piece4x4 |
              +         2a+     b1    +     b2    +3b         +
              |           |  3b    3a |  3b    3a |           |
              +    c1     +--+--+--+--+--+--+--+--+     c2    +
              |           |                       |           |
              +         2b+                       +3a         +
              | 3b    3a  |                       |  2b    2a |
              +--+--+--+--+                       +--+--+--+--+
              |     |                                   |     |
              +   3a+                                   +3b   +
              |     |                                   |     |
              + b8  +                                   +  b3 +
              |     |                                   |     |
              +   3b+                                   +     +
              |     |                                   |3a   |
              +--+--+                                   +--+--+
              |     |                                   |     |
              +   3a+                                   +3b   +
              |     |                                   |     |
              + b7  +                                   +  b4 +
              |     |                                   |     |
              +   3b+                                   +3a   +
              |     |                                   |     |
              +--+--+--+--+                       +--+--+--+--+
              |       2b  |                       |  3a       |
              +         3a+                       +2b         +
              |           |                       |           |
              +    c4     +--+--+--+--+--+--+--+--+     c3    +
              |           |  3a   3b  |  3a   3b  |           |
              +           +     b6    +     b5    +           +
              |  Piece4x4 | Border4x2 | Border4x2 |  Piece4x4 |
              +--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
        """

        blk1 = list()
        blk2 = list()
        blk3 = list()
        blk4 = list()

        # top (p1, p2, p3, p4)
        for p1, p2, p3, p4, used_nrs in self._iter_ring2(sol_nrs, c1, b1, b2, c2):
            tup = (used_nrs, (p1, p2, p3, p4))
            blk1.append(tup)
        # for
        print('  blk1: %s' % len(blk1))
        if len(blk1) == 0:
            # no solution
            return

        # right (p5, p6, p7, p8)
        for p1, p2, p3, p4, used_nrs in self._iter_ring2(sol_nrs, c2, b3, b4, c3):
            tup = (used_nrs, (p1, p2, p3, p4))
            blk2.append(tup)
        # for
        print('  blk2: %s' % len(blk2))
        if len(blk2) == 0:
            # no solution
            return

        # bottom (p9, p10, p11, p12)
        for p1, p2, p3, p4, used_nrs in self._iter_ring2(sol_nrs, c3, b5, b6, c4):
            tup = (used_nrs, (p1, p2, p3, p4))
            blk3.append(tup)
        # for
        print('  blk3: %s' % len(blk3))
        if len(blk3) == 0:
            # no solution
            return

        # left (p13, p14, p15, p16)
        for p1, p2, p3, p4, used_nrs in self._iter_ring2(sol_nrs, c4, b7, b8, c1):
            tup = (used_nrs, (p1, p2, p3, p4))
            blk4.append(tup)
        # for
        print('  blk4: %s' % len(blk4))
        if len(blk4) == 0:
            # no solution
            return

        # find non-overlapping sets
        for used_nrs1, tup1 in blk1:
            for used_nrs2, tup2 in blk2:
                if len(set(used_nrs1 + used_nrs2)) == 16 * 2:
                    for used_nrs3, tup3 in blk3:
                        if len(set(used_nrs1 + used_nrs2 + used_nrs3)) == 16 * 3:
                            for used_nrs4, tup4 in blk4:
                                if len(set(used_nrs1 + used_nrs2 + used_nrs3 + used_nrs4)) == 16 * 4:

                                    self.nr += 1
                                    print('[INFO] Solution %s' % self.nr)

                                    p1, p2, p3, p4 = tup1
                                    p5, p6, p7, p8 = self._find_correct_2x2s(tup2, 1)
                                    p9, p10, p11, p12 = self._find_correct_2x2s(tup3, 2)
                                    p13, p14, p15, p16 = self._find_correct_2x2s(tup4, 3)

                                    ring = Ring4(
                                            nr=self.nr,
                                            c1=sol.c1, c2=sol.c2, c3=sol.c3, c4=sol.c4,
                                            b1=sol.b1, b2=sol.b2, b3=sol.b3, b4=sol.b4,
                                            b5=sol.b5, b6=sol.b6, b7=sol.b7, b8=sol.b8,
                                            p1=p1.nr, p2=p2.nr, p3=p3.nr, p4=p4.nr,
                                            p5=p5, p6=p6, p7=p7, p8=p8,
                                            p9=p9, p10=p10, p11=p11, p12=p12,
                                            p13=p13, p14=p14, p15=p15, p16=p16)
                                    ring.save()
                            # for
                    # for
            # for
        # for

    def handle(self, *args, **options):

        """ a ring4 solution is a BorderSolution amended with sixteen Piece2x2

              c1           b1      b2            c2
                +-------+-------+-------+-------+
                |       |  4x2  |  4x2  |       |
                +  4x4  +---+---+---+---+  4x4  +
                |       |2x2|2x2|2x2|2x2|       |
                +---+---+---+---+---+---+---+---+
                          p1  p2  p3  p4
                +---+---+               +---+---+
                |   |2x2|p16          p5|2x2|   |
             b8 |4x2+---+               +---+4x2+ b3
                |   |2x2|p15          p6|2x2|   |
                +---+---+               +---+---+
                |   |2x2|p14          p7|2x2|   |
             b7 |4x2+---+               +---+4x2+ b4
                |   |2x2|p13          p8|2x2|   |
                +---+---+               +---+---+
                         p12 p11 p10 p9
                +---+---+---+---+---+---+---+---+
                |       |2x2|2x2|2x2|2x2|       |
                +  4x4  +---+---+---+---+  4x4  +
                |       |  4x2  |  4x2  |       |
                +-------+-------+-------+-------+
              c4           b6      b5            c3

        """

        # delete the old solutions
        Ring4.objects.all().delete()

        for sol in BorderSolution.objects.iterator(chunk_size=5):
            self.stdout.write('[INFO] Loading BorderSolution %s' % sol.nr)
            c1 = Piece4x4.objects.get(nr=sol.c1)
            c2 = Piece4x4.objects.get(nr=sol.c2)
            c3 = Piece4x4.objects.get(nr=sol.c3)
            c4 = Piece4x4.objects.get(nr=sol.c4)
            b1 = Border4x2.objects.get(nr=sol.b1)
            b2 = Border4x2.objects.get(nr=sol.b2)
            b3 = Border4x2.objects.get(nr=sol.b3)
            b4 = Border4x2.objects.get(nr=sol.b4)
            b5 = Border4x2.objects.get(nr=sol.b5)
            b6 = Border4x2.objects.get(nr=sol.b6)
            b7 = Border4x2.objects.get(nr=sol.b7)
            b8 = Border4x2.objects.get(nr=sol.b8)

            sol_nrs = (139,     # don't ever used this number
                       c1.nr1, c1.nr2, c1.nr3, c1.nr4, c1.nr5, c1.nr6, c1.nr7, c1.nr8,
                       c1.nr9, c1.nr10, c1.nr11, c1.nr12, c1.nr13, c1.nr14, c1.nr15, c1.nr16,
                       c2.nr1, c2.nr2, c2.nr3, c2.nr4, c2.nr5, c2.nr6, c2.nr7, c2.nr8,
                       c2.nr9, c2.nr10, c2.nr11, c2.nr12, c2.nr13, c2.nr14, c2.nr15, c2.nr16,
                       c3.nr1, c3.nr2, c3.nr3, c3.nr4, c3.nr5, c3.nr6, c3.nr7, c3.nr8,
                       c3.nr9, c3.nr10, c3.nr11, c3.nr12, c3.nr13, c3.nr14, c3.nr15, c3.nr16,
                       c4.nr1, c4.nr2, c4.nr3, c4.nr4, c4.nr5, c4.nr6, c4.nr7, c4.nr8,
                       c4.nr9, c4.nr10, c4.nr11, c4.nr12, c4.nr13, c4.nr14, c4.nr15, c4.nr16,
                       b1.nr1, b1.nr2, b1.nr3, b1.nr4, b1.nr5, b1.nr6, b1.nr7, b1.nr8,
                       b2.nr1, b2.nr2, b2.nr3, b2.nr4, b2.nr5, b2.nr6, b2.nr7, b2.nr8,
                       b3.nr1, b3.nr2, b3.nr3, b3.nr4, b3.nr5, b3.nr6, b3.nr7, b3.nr8,
                       b4.nr1, b4.nr2, b4.nr3, b4.nr4, b4.nr5, b4.nr6, b4.nr7, b4.nr8,
                       b5.nr1, b5.nr2, b5.nr3, b5.nr4, b5.nr5, b5.nr6, b5.nr7, b5.nr8,
                       b6.nr1, b6.nr2, b6.nr3, b6.nr4, b6.nr5, b6.nr6, b6.nr7, b6.nr8,
                       b7.nr1, b7.nr2, b7.nr3, b7.nr4, b7.nr5, b7.nr6, b7.nr7, b7.nr8,
                       b8.nr1, b8.nr2, b8.nr3, b8.nr4, b8.nr5, b8.nr6, b8.nr7, b8.nr8)

            # for coupling to a Piece2x2
            self._set_4x4_side2b_side3a(c1)
            self._set_4x4_side2b_side3a(c2)
            self._set_4x4_side2b_side3a(c3)
            self._set_4x4_side2b_side3a(c4)

            self._set_4x2_side3a_side3b(b1)
            self._set_4x2_side3a_side3b(b2)
            self._set_4x2_side3a_side3b(b3)
            self._set_4x2_side3a_side3b(b4)
            self._set_4x2_side3a_side3b(b5)
            self._set_4x2_side3a_side3b(b6)
            self._set_4x2_side3a_side3b(b7)
            self._set_4x2_side3a_side3b(b8)

            self._find_ring4(sol, sol_nrs, c1, c2, c3, c4, b1, b2, b3, b4, b5, b6, b7, b8)
        # for

        self.stdout.write('[INFO] Found %s Ring4 solutions' % self.nr)

# end of file
