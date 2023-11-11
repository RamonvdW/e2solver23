# -*- coding: utf-8 -*-

#  Copyright (c) 2023 Ramon van der Winkel.
#  All rights reserved.
#  Licensed under BSD-3-Clause-Clear. See LICENSE file for details.

# maak een account HWL van specifieke vereniging, vanaf de commandline

from django.core.management.base import BaseCommand
from BasePieces.models import BasePiece
from Borders4x2.models import Border4x2
from BorderSolutions.models import BorderSolution
from Pieces2x2.models import TwoSides, Piece2x2
from Pieces4x4.models import Piece4x4


class Command(BaseCommand):

    help = "Generate border solutions from Piece4x4 and Border4x2"

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

    def get_4x4_side2a_reverse(self, piece4x4):
        p4 = self.base_pieces[piece4x4.nr4]
        p8 = self.base_pieces[piece4x4.nr8]
        # side2a = p4.get_side(2, piece4x4.rot4) + p8.get_side(2, piece4x4.rot8)
        side2a_reverse = p8.get_side(2, piece4x4.rot8) + p4.get_side(2, piece4x4.rot4)
        return side2a_reverse

    def get_4x4_side2b_reverse(self, piece4x4):
        p12 = self.base_pieces[piece4x4.nr12]
        p16 = self.base_pieces[piece4x4.nr16]
        side2b_reverse = p16.get_side(2, piece4x4.rot16) + p12.get_side(2, piece4x4.rot12)
        return side2b_reverse

    def get_4x4_side3a_reverse(self, piece4x4):
        p15 = self.base_pieces[piece4x4.nr15]
        p16 = self.base_pieces[piece4x4.nr16]
        side3a_reverse = p15.get_side(3, piece4x4.rot15) + p16.get_side(3, piece4x4.rot16)
        return side3a_reverse

    def get_4x4_side3b_reverse(self, piece4x4):
        p13 = self.base_pieces[piece4x4.nr13]
        p14 = self.base_pieces[piece4x4.nr14]
        # side3b = p14.get_side(3, piece4x4.rot14) + p13.get_side(3, piece4x4.rot13)
        side3b_reverse = p13.get_side(3, piece4x4.rot13) + p14.get_side(3, piece4x4.rot14)
        return side3b_reverse

    def _iter_corner(self, used_nrs, hint_nr):
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

        for c in (Piece4x4
                  .objects
                  .filter(nr11=hint_nr)
                  .exclude(nr1__in=used_nrs)
                  .exclude(nr2__in=used_nrs)
                  .exclude(nr3__in=used_nrs)
                  .exclude(nr4__in=used_nrs)
                  .exclude(nr5__in=used_nrs)
                  .exclude(nr6__in=used_nrs)
                  .exclude(nr7__in=used_nrs)
                  .exclude(nr8__in=used_nrs)
                  .exclude(nr9__in=used_nrs)
                  .exclude(nr10__in=used_nrs)
                  .exclude(nr12__in=used_nrs)
                  .exclude(nr13__in=used_nrs)
                  .exclude(nr14__in=used_nrs)
                  .exclude(nr15__in=used_nrs)
                  .exclude(nr16__in=used_nrs)
                  .order_by('nr')
                  .iterator(chunk_size=1000)):

            c_nrs = (c.nr1, c.nr2, c.nr3, c.nr4, c.nr5, c.nr6, c.nr7, c.nr8,
                     c.nr9, c.nr10, c.nr11, c.nr12, c.nr13, c.nr14, c.nr15, c.nr16)

            # for coupling to a Border4x2
            c.side2a = self.get_4x4_side2a_reverse(c)
            c.side3b = self.get_4x4_side3b_reverse(c)

            # for coupling to a Piece2x2
            c.side2b = self.two_sides2nr[self.get_4x4_side2b_reverse(c)]
            c.side3a = self.two_sides2nr[self.get_4x4_side3a_reverse(c)]

            used_nrs2 = used_nrs + c_nrs

            yield c, used_nrs2
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
            b.side3a = self.two_sides2nr[b.side3[1] + b.side3[0]]   # 7+8
            b.side3b = self.two_sides2nr[b.side3[3] + b.side3[2]]   # 5+6

            exp_side2 = b.side4[1] + b.side4[0]

            yield b, exp_side2, used_nrs2
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
            b.side3a = self.two_sides2nr[b.side3[1] + b.side3[0]]   # 7+8
            b.side3b = self.two_sides2nr[b.side3[3] + b.side3[2]]   # 5+6

            exp_side4 = b.side2[1] + b.side2[0]

            yield b, exp_side4, used_nrs2
        # for

    def _iter_border_side2_side4(self, used_nrs, exp_side2, exp_side4):
        """
                   side1 = border
                +---+---+---+---+
                | 1 | 2 | 3 | 4 |
         side 4 +---+---+---+---+ side 2
                | 5 | 6 | 7 | 8 |
                +---+---+---+---+
                 side3b  side3a
        """
        # assert isinstance(exp_side2, str)
        # assert isinstance(exp_side4, str)
        for b in (Border4x2
                  .objects
                  .filter(side4=exp_side4,
                          side2=exp_side2)
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
            b.side3a = self.two_sides2nr[b.side3[1] + b.side3[0]]   # 7+8
            b.side3b = self.two_sides2nr[b.side3[3] + b.side3[2]]   # 5+6

            yield b, used_nrs2
        # for

    @staticmethod
    def _test_piece2x2(used_nrs, exp_side4, exp_side1):
        # assert isinstance(exp_side4, int)
        # assert isinstance(exp_side1, int)
        p = (Piece2x2
             .objects
             .filter(side4=exp_side4,
                     side1=exp_side1)
             .exclude(nr1__in=used_nrs)
             .exclude(nr2__in=used_nrs)
             .exclude(nr3__in=used_nrs)
             .exclude(nr4__in=used_nrs)
             .iterator(chunk_size=10)
             .first())
        return p is not None

    def handle(self, *args, **options):

        """ a corner solution consists of 4 Piece4x4, each under a certain rotation
            each corner has one of the 4 hint pieces
            total solution must have 4x16 = 64 unique base pieces

                   +---+      +---+
                   |4x4|      |4x4|
                   +---+      +---+

                   +---+      +---+
                   |4x4|      |4x4|
                   +---+      +---+

            The corner is in position 1
            The hint is in position 11

               +---+---+---+---+
               | 1 | 2 | 3 | 4 |
               +---+---+---+---+ side 2a
               | 5 | 6 | 7 | 8 |
               +---+---+---+---+
               | 9 |10 |11 |12 |  11 = hint piece
               +---+---+---+---+
               |13 |14 |15 |16 |
               +---+---+---+---+
                side 3b


            A 4x2 piece consists of 8 base pieces, each under a certain rotation
            the four sides start at the top and follow the piece clockwise

                      side1 = border
                +---+---+---+---+
                | 1 | 2 | 3 | 4 |
         side 4 +---+---+---+---+ side 2
                | 5 | 6 | 7 | 8 |
                +---+---+---+---+
                      side 3


           Border Solution:

              +--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
              |  Piece4x4 | Border4x2 | Border4x2 |  Piece4x4 |
              +         2a+     b1    +     b2    +3b         +
              |           |  3b    3a |  3b    3a |           |
              +    c1     +--+--+--+--+--+--+--+--+     c2    +
              |           |     |           |     |           |
              +         2b+ p1  +           +  p2 +3a         +
              | 3b    3a  |     |           |     |  2b    2a |
              +--+--+--+--+--+--+           +--+--+--+--+--+--+
              |     |     |                       |     |     |
              +   3a+ p8  +                       +  p3 +3b   +
              |     |     |                       |     |     |
              + b8  +--+--+                       +--+--+  b3 +
              |     |                                   |     |
              +     +                                   +     +
              |     |                                   |     |
              +--+--+                                   +--+--+
              |     |                                   |     |
              +     +                                   +     +
              |     |                                   |     |
              + b7  +--+--+                       +--+--+  b4 +
              |     |     |                       |     |     |
              +   3b+ p7  +                       +  p4 +3a   +
              |     |     |                       |     |     |
              +--+--+--+--+--+--+           +--+--+--+--+--+--+
              | 2a    2b  |     |           |     |  3a    3b |
              +         3a+ p6  +           + p5  +2b         +
              |           |     |           |     |           |
              +    c4     +--+--+--+--+--+--+--+--+     c3    +
              |           |  3a       |        3b |           |
              +         3b+     b6    +     b5    +2a         +
              |  Piece4x4 | Border4x2 | Border4x2 |  Piece4x4 |
              +--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+

            order: c1, b8,p8, b1,p1
                   c2, b2,p2, b3,p3
                   c4, b7,p7, b6,p6
                   c3, b4,p4, b5,p5

        """

        # delete the old solutions
        BorderSolution.objects.all().delete()

        # 208: top left
        # 181: bottom left
        # 249: bottom right
        # 255: top right
        hint_c1, hint_c2, hint_c3, hint_c4 = (208, 255, 249, 181)

        nr = 0
        used_nrs0 = (139,)      # don't ever use this piece

        # take one corner and fit two border pieces
        # b8 c1 b1
        for c1, used_nrs1 in self._iter_corner(used_nrs0, hint_c1):
            print('c1: %s' % c1.nr)
            for b8, b7_exp_s2, used_nrs2 in self._iter_border_side2(used_nrs1, c1.side3b):
                print('b8: %s' % b8.nr)

                # check p8
                if not self._test_piece2x2(used_nrs2, b8.side3a, c1.side3a):
                    continue
                print('p8 ok')

                for b1, b2_exp_side4, used_nrs3 in self._iter_border_side4(used_nrs2, c1.side2a):
                    print('b1: %s' % b1.nr)

                    # check p1
                    if not self._test_piece2x2(used_nrs3, c1.side2b, b1.side3b):
                        continue
                    print('p1 ok')

                    # take one corner and fit two border pieces
                    # b2 c2 b3
                    for c2, used_nrs4 in self._iter_corner(used_nrs3, hint_c2):
                        print('c2: %s' % c2.nr)
                        for b2, used_nrs5 in self._iter_border_side2_side4(used_nrs4,
                                                                           c2.side3b,
                                                                           b2_exp_side4):
                            print('b2: %s' % b2.nr)

                            # check p2
                            if not self._test_piece2x2(used_nrs5, b2.side3a, c2.side3a):
                                continue
                            print('p2 ok')

                            for b3, b4_exp_side4, used_nrs6 in self._iter_border_side4(used_nrs5, c2.side2a):
                                print('b3: %s' % b3.nr)

                                # check p3
                                if not self._test_piece2x2(used_nrs6, c2.side2b, b3.side3b):
                                    continue
                                print('p3 ok')

                                # take one corner and fit two border pieces
                                # b6 c4 b7
                                for c4, used_nrs7 in self._iter_corner(used_nrs6, hint_c4):
                                    print('c4: %s' % c4.nr)
                                    for b7, used_nrs8 in self._iter_border_side2_side4(used_nrs7,
                                                                                       b7_exp_s2,
                                                                                       c4.side2a):
                                        print('b7: %s' % b7.nr)

                                        # check p7
                                        if not self._test_piece2x2(used_nrs8, c4.side2b, b7.side3b):
                                            continue
                                        print('p7 ok')

                                        for b6, b5_exp_side2, used_nrs9 in self._iter_border_side2(used_nrs8,
                                                                                                   c4.side3b):
                                            print('b6: %s' % b6.nr)

                                            # check p6
                                            if not self._test_piece2x2(used_nrs9, b6.side3a, c4.side3a):
                                                continue
                                            print('p6 ok')

                                            # take one corner and fit two border pieces
                                            # b4 c3 b5
                                            for c3, used_nrs10 in self._iter_corner(used_nrs9, hint_c3):
                                                print('c3: %s' % c3.nr)
                                                for b4, used_nrs11 in self._iter_border_side2_side4(used_nrs10,
                                                                                                    c3.side3b,
                                                                                                    b4_exp_side4):
                                                    print('b4: %s' % b4.nr)

                                                    # check p4
                                                    if not self._test_piece2x2(used_nrs11, b4.side3a, c3.side3a):
                                                        continue
                                                    print('p4 ok')

                                                    for b5, used_nrs12 in self._iter_border_side2_side4(used_nrs11,
                                                                                                        b5_exp_side2,
                                                                                                        c3.side2a):
                                                        print('b5: %s' % b5.nr)

                                                        # check p5
                                                        if not self._test_piece2x2(used_nrs12, c3.side2b, b5.side3b):
                                                            continue
                                                        print('p5 ok')

                                                        nr += 1
                                                        solution = BorderSolution(
                                                                        nr=nr,
                                                                        c1=c1.nr,
                                                                        c2=c2.nr,
                                                                        c3=c3.nr,
                                                                        c4=c4.nr,
                                                                        b1=b1.nr,
                                                                        b2=b2.nr,
                                                                        b3=b3.nr,
                                                                        b4=b4.nr,
                                                                        b5=b5.nr,
                                                                        b6=b6.nr,
                                                                        b7=b7.nr,
                                                                        b8=b8.nr)
                                                        solution.save()
                                                        print('[INFO] Solutions: %s' % nr)
                                                    # for
                                                # for
                                            # for
                                        # for
                                    # for
                                # for
                            # for
                        # for
                    # for
                # for
            # for
        # for

# end of file
