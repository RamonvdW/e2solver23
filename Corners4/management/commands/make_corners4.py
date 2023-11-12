# -*- coding: utf-8 -*-

#  Copyright (c) 2023 Ramon van der Winkel.
#  All rights reserved.
#  Licensed under BSD-3-Clause-Clear. See LICENSE file for details.

from django.core.management.base import BaseCommand
from BasePieces.models import BasePiece
from Borders4x2.models import Border4x2
from Corners4.models import Corner4
from Pieces2x2.models import TwoSides, Piece2x2
from Pieces4x4.models import Piece4x4


class Command(BaseCommand):

    help = "Generate Corner4 solutions from a corner (Piece4x4), two Border4x4 and 4 central Piece2x2"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # cache all base pieces
        self.base_pieces = dict()       # [nr] = BasePiece()
        for piece in BasePiece.objects.all():
            self.base_pieces[piece.nr] = piece
        # for

        # load all TwoSides
        self.two_sides2nr = dict()   # ['XX'] = nr
        self.nr2two_sides = dict()   # [nr] = 'XX'
        for two in TwoSides.objects.all():
            self.nr2two_sides[two.nr] = two.two_sides
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

        self._cache_test_2x2 = dict()   # [(side2, side4)] = dict() [used_nrs] = True/False

        self.nr = 0

    def add_arguments(self, parser):
        parser.add_argument('c_nr', nargs=1, help="Base piece for corner: 1,2,3,4")

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

    def _test_2x2_side4_1(self, used_nrs, exp_side4, exp_side1):
        tup = (exp_side4, exp_side1)
        try:
            cache = self._cache_test_2x2[tup]
        except KeyError:
            self._cache_test_2x2[tup] = cache = dict()

        try:
            result = cache[used_nrs]
        except KeyError:
            result = False
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
                result = True
            # for
            cache[used_nrs] = result

        return result

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

    def _iter_border_side2(self, used_nrs, exp_side2):
        # assert isinstance(exp_side2, str)
        for b in (Border4x2
                  .objects
                  .filter(side2=exp_side2)
                  .exclude(nr1__in=used_nrs)
                  .exclude(nr2__in=used_nrs)
                  .exclude(nr3__in=used_nrs)
                  .exclude(nr4__in=used_nrs)
                  .exclude(nr5__in=used_nrs)
                  .exclude(nr6__in=used_nrs)
                  .exclude(nr7__in=used_nrs)
                  .exclude(nr8__in=used_nrs)
                  .iterator(chunk_size=10000)):

            b_nrs = (b.nr1, b.nr2, b.nr3, b.nr4, b.nr5, b.nr6, b.nr7, b.nr8)
            used_nrs2 = used_nrs + b_nrs

            # side3 = "8765"
            b.side3a = self.two_sides2nr[b.side3[1] + b.side3[0]]  # 7+8
            b.side3b = self.two_sides2nr[b.side3[3] + b.side3[2]]  # 5+6

            yield b, used_nrs2
        # for

    def _iter_border_side4(self, used_nrs, exp_side4):
        # assert isinstance(exp_side4, str)
        for b in (Border4x2
                  .objects
                  .filter(side4=exp_side4)
                  .exclude(nr1__in=used_nrs)
                  .exclude(nr2__in=used_nrs)
                  .exclude(nr3__in=used_nrs)
                  .exclude(nr4__in=used_nrs)
                  .exclude(nr5__in=used_nrs)
                  .exclude(nr6__in=used_nrs)
                  .exclude(nr7__in=used_nrs)
                  .exclude(nr8__in=used_nrs)
                  .iterator(chunk_size=10000)):

            b_nrs = (b.nr1, b.nr2, b.nr3, b.nr4, b.nr5, b.nr6, b.nr7, b.nr8)
            used_nrs2 = used_nrs + b_nrs

            # side3 = "8765"
            b.side3a = self.two_sides2nr[b.side3[1] + b.side3[0]]  # 7+8
            b.side3b = self.two_sides2nr[b.side3[3] + b.side3[2]]  # 5+6

            yield b, used_nrs2
        # for

    def _find_corner4(self, c, used_nrs0):
        """
          c1              b2
            +-------+  +-------+
            |       |  |  4x2  |
            +  4x4  +  +---+---+ side 2
            |       |  |2x2|2x2|
            +---+---+  +---+---+
                         p3  p4
            +---+---+
            |   |2x2| p2
         b1 |4x2+---+
            |   |2x2| p1
            +---+---+
              side 3

              +--+--+--+--+--+--+--+--+
              |  Piece4x4 | Border4x2 |
              +         2a+     b2    +  side2
              |           |  3b    3a |
              +    c1     +--+--+--+--+
              |           |     |     |
              +         2b+  p2 +  q3 +
              | 3b    3a  |     |     |
              +--+--+--+--+--+--+--+--+
              |     |     |     |
              +   3a+  p1 +  q2 +   q = quality check
              |     |     |     |
              + b1  +--+--+--+--+
              |     |     |
              +   3b+  q1 +
              |     |     |
              +--+--+--+--+
              side3
        """

        q_fail = 0
        bulk = list()
        for b1, used_nrs1 in self._iter_border_side2(used_nrs0, c.side3b):
            q1_exp_side4 = b1.side3b

            for p1, used_nrs2 in self._iter_2x2_side4_1(used_nrs1, b1.side3a, c.side3a):
                q1_exp_side1 = self.side_nr2reverse[p1.side3]
                q2_exp_side4 = self.side_nr2reverse[p1.side2]

                for b2, used_nrs3 in self._iter_border_side4(used_nrs2, c.side2a):
                    q3_exp_side1 = b2.side3a

                    for p2, used_nrs4 in self._iter_2x2_side4_1(used_nrs3, c.side2b, b2.side3b):
                        q2_exp_side1 = self.side_nr2reverse[p2.side3]
                        q3_exp_side4 = self.side_nr2reverse[p2.side2]

                        if not self._test_2x2_side4_1(used_nrs4, q1_exp_side4, q1_exp_side1):
                            q_fail += 1
                            continue

                        if not self._test_2x2_side4_1(used_nrs4, q2_exp_side4, q2_exp_side1):
                            q_fail += 1
                            continue

                        if not self._test_2x2_side4_1(used_nrs4, q3_exp_side4, q3_exp_side1):
                            q_fail += 1
                            continue

                        self.nr += 1
                        corner = Corner4(
                                    nr=self.nr,
                                    c=c.nr,
                                    b1=b1.nr,
                                    b2=b2.nr,
                                    p1=p1.nr,
                                    p2=p2.nr)
                        bulk.append(corner)

                        if len(bulk) >= 1000:
                            Corner4.objects.bulk_create(bulk)
                            print('[INFO] Solutions: %s (q-fail %s)' % (self.nr, q_fail))
                            q_fail = 0
                            bulk = list()

                    # for
                # for

            # for
        # for

    def handle(self, *args, **options):

        try:
            c_nr = int(options['c_nr'][0])
        except ValueError:
            self.stderr.write('[ERROR] Illegal number')
            return
        else:
            if c_nr not in (1, 2, 3, 4):
                self.stderr.write('[ERROR] Illegal number')
                return
        self.stdout.write('[INFO] Corner base piece number: %s' % c_nr)

        self.nr = c_nr * 100 * 1000000  # = 100M
        next_nr = (c_nr + 1) * 100 * 1000000

        # delete the old solutions
        Corner4.objects.filter(nr__gte=self.nr, nr__lt=next_nr).delete()

        for c in Piece4x4.objects.filter(nr1=c_nr).order_by('nr').iterator(chunk_size=1000):
            """
                   +---+---+---+---+
                   | 1 | 2 | 3 | 4 |
                   +---+---+---+---+ side 2a
                   | 5 | 6 | 7 | 8 |
                   +---+---+---+---+
                   | 9 |10 |11 |12 |  11 = hint piece
                   +---+---+---+---+
                   |13 |14 |15 |16 | side 2b
                   +---+---+---+---+
                    side 3b side 3a
            """
            used_nrs = (139,   # never to be used
                        c.nr1, c.nr2, c.nr3, c.nr4, c.nr5, c.nr6, c.nr7, c.nr8,
                        c.nr9, c.nr10, c.nr11, c.nr12, c.nr13, c.nr14, c.nr15, c.nr16)

            p4 = self.base_pieces[c.nr4]
            p8 = self.base_pieces[c.nr8]
            p12 = self.base_pieces[c.nr12]
            p13 = self.base_pieces[c.nr13]
            p14 = self.base_pieces[c.nr14]
            p15 = self.base_pieces[c.nr15]
            p16 = self.base_pieces[c.nr16]

            # for coupling to a Border4x2
            c.side2a = p8.get_side(2, c.rot8) + p4.get_side(2, c.rot4)
            c.side3b = p13.get_side(3, c.rot13) + p14.get_side(3, c.rot14)

            # for coupling to a Piece2x2
            c.side2b = self.two_sides2nr[p16.get_side(2, c.rot16) + p12.get_side(2, c.rot12)]
            c.side3a = self.two_sides2nr[p15.get_side(3, c.rot15) + p16.get_side(3, c.rot16)]

            self._find_corner4(c, used_nrs)
        # for

        self.stdout.write('[INFO] Found %s Corner4 solutions' % self.nr)

# end of file
