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

    help = "Check the generated border solutions"

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

    def add_arguments(self, parser):
        parser.add_argument('nr', nargs=1, help="Which border solution to use")

    def _calc_piece4x4_side2b_side3a(self, piece4x4):
        """
                      side 1
                +---+---+---+---+
                | 1 | 2 | 3 | 4 |
                +---+---+---+---+
                | 5 | 6 | 7 | 8 |
        side 4  +---+---+---+---+
                | 9 |10 |11 |12 |
                +---+---+---+---+ side 2b
                |13 |14 |15 |16 |
                +---+---+---+---+
                         side 3a
        """

        side2b_2 = self.base_pieces[piece4x4.nr12].get_side(2, piece4x4.rot12)
        side2b_1 = self.base_pieces[piece4x4.nr16].get_side(2, piece4x4.rot16)

        side3a_2 = self.base_pieces[piece4x4.nr16].get_side(3, piece4x4.rot16)
        side3a_1 = self.base_pieces[piece4x4.nr15].get_side(3, piece4x4.rot15)

        piece4x4.side2b = self.two_sides2nr[side2b_1 + side2b_2]
        piece4x4.side3a = self.two_sides2nr[side3a_1 + side3a_2]

    def _calc_border4x2_side3a_side3b(self, border4x2):
        """
                  side1 = border
                +---+---+---+---+
                | 1 | 2 | 3 | 4 |
         side 4 +---+---+---+---+ side 2
                | 5 | 6 | 7 | 8 |
                +---+---+---+---+
                 side3b   side3a
        """
        side3a_2 = self.base_pieces[border4x2.nr8].get_side(3, border4x2.rot8)
        side3a_1 = self.base_pieces[border4x2.nr7].get_side(3, border4x2.rot7)

        side3b_2 = self.base_pieces[border4x2.nr6].get_side(3, border4x2.rot6)
        side3b_1 = self.base_pieces[border4x2.nr5].get_side(3, border4x2.rot5)

        border4x2.side3a = self.two_sides2nr[side3a_1 + side3a_2]
        border4x2.side3b = self.two_sides2nr[side3b_1 + side3b_2]

    def _load_solution(self, nr):
        solution = BorderSolution.objects.get(nr=nr)
        self.stdout.write('[INFO] Using solution %s' % solution.nr)

        # replace the reference numbers with real objects
        print('solution.c1=%s' % solution.c1)
        solution.c1 = Piece4x4.objects.get(nr=solution.c1)
        solution.c2 = Piece4x4.objects.get(nr=solution.c2)
        solution.c3 = Piece4x4.objects.get(nr=solution.c3)
        solution.c4 = Piece4x4.objects.get(nr=solution.c4)

        print('solution.b1=%s' % solution.b1)
        solution.b1 = Border4x2.objects.get(nr=solution.b1)
        solution.b2 = Border4x2.objects.get(nr=solution.b2)
        solution.b3 = Border4x2.objects.get(nr=solution.b3)
        solution.b4 = Border4x2.objects.get(nr=solution.b4)
        solution.b5 = Border4x2.objects.get(nr=solution.b5)
        solution.b6 = Border4x2.objects.get(nr=solution.b6)
        solution.b7 = Border4x2.objects.get(nr=solution.b7)
        solution.b8 = Border4x2.objects.get(nr=solution.b8)

        # pre-calculate the sides
        self._calc_piece4x4_side2b_side3a(solution.c1)
        self._calc_piece4x4_side2b_side3a(solution.c2)
        self._calc_piece4x4_side2b_side3a(solution.c3)
        self._calc_piece4x4_side2b_side3a(solution.c4)

        self._calc_border4x2_side3a_side3b(solution.b1)
        self._calc_border4x2_side3a_side3b(solution.b2)
        self._calc_border4x2_side3a_side3b(solution.b3)
        self._calc_border4x2_side3a_side3b(solution.b4)
        self._calc_border4x2_side3a_side3b(solution.b5)
        self._calc_border4x2_side3a_side3b(solution.b6)
        self._calc_border4x2_side3a_side3b(solution.b7)
        self._calc_border4x2_side3a_side3b(solution.b8)

        return solution

    @staticmethod
    def _find_p_4_1(used_nrs, expected_side4, expected_side1):
        for p in (Piece2x2
                  .objects
                  .filter(side4=expected_side4,
                          side1=expected_side1)
                  .exclude(nr1__in=used_nrs)
                  .exclude(nr2__in=used_nrs)
                  .exclude(nr3__in=used_nrs)
                  .exclude(nr4__in=used_nrs)):

            base_nrs = (p.nr1, p.nr2, p.nr3, p.nr4)
            used_nrs2 = used_nrs + base_nrs
            yield p, used_nrs2

    @staticmethod
    def _find_p_1_2(used_nrs, expected_side1, expected_side2):
        for p in (Piece2x2
                  .objects
                  .filter(side1=expected_side1,
                          side2=expected_side2)
                  .exclude(nr1__in=used_nrs)
                  .exclude(nr2__in=used_nrs)
                  .exclude(nr3__in=used_nrs)
                  .exclude(nr4__in=used_nrs)):

            base_nrs = (p.nr1, p.nr2, p.nr3, p.nr4)
            used_nrs2 = used_nrs + base_nrs
            yield p, used_nrs2

    @staticmethod
    def _find_p_2_3(used_nrs, expected_side2, expected_side4):
        for p in (Piece2x2
                  .objects
                  .filter(side2=expected_side2,
                          side4=expected_side4)
                  .exclude(nr1__in=used_nrs)
                  .exclude(nr2__in=used_nrs)
                  .exclude(nr3__in=used_nrs)
                  .exclude(nr4__in=used_nrs)):

            base_nrs = (p.nr1, p.nr2, p.nr3, p.nr4)
            used_nrs2 = used_nrs + base_nrs
            yield p, used_nrs2

    @staticmethod
    def _find_p_3_4(used_nrs, expected_side3, expected_side4):
        for p in (Piece2x2
                  .objects
                  .filter(side3=expected_side3,
                          side4=expected_side4)
                  .exclude(nr1__in=used_nrs)
                  .exclude(nr2__in=used_nrs)
                  .exclude(nr3__in=used_nrs)
                  .exclude(nr4__in=used_nrs)):

            base_nrs = (p.nr1, p.nr2, p.nr3, p.nr4)
            used_nrs2 = used_nrs + base_nrs
            yield p, used_nrs2

    def handle(self, *args, **options):

        """ a border solution has 4 corners that we know can fit together.
            for each c1 we only store 1 solution, including the border.

            We try to solve it further with Piece2x2 for the center.

            A Piece2x2 consists of 4 base pieces, each under a certain rotation
            the four sides start at the top and follow the piece clockwise

                      side1
                    +---+---+
                    | 1 | 2 |
             side 4 +---+---+ side 2
                    | 5 | 6 |
                    +---+---+
                      side 3


            A 4x2 piece consists of 8 base pieces, each under a certain rotation
            the four sides start at the top and follow the piece clockwise

                          side1 = border
                    +---+---+---+---+
                    | 1 | 2 | 3 | 4 |
             side 4 +---+---+---+---+ side 2
                    | 5 | 6 | 7 | 8 |
                    +---+---+---+---+
                     side 3b side 3a

            The corner is in position 1
            The hint is in position 11

                         border
                    +---+---+---+---+
                    | 1 | 2 | 3 | 4 |  1 = corner piece
                    +---+---+---+---+
                    | 5 | 6 | 7 | 8 |
                    +---+---+---+---+  11 = hint piece
                    | 9 |10 |11 |12 |
                    +---+---+---+---+ side 2b
                    |13 |14 |15 |16 |
                    +---+---+---+---+
                             side 3a

            corner solution consists of 4 Piece4x4, each under a certain rotation
            each corner has one of the 4 hint pieces
            total solution must have 4x16 = 64 unique base pieces

              +--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
              |  Piece4x4 | Border4x2 | Border4x2 |  Piece4x4 |
              +           +     b1    +     b2    +           +
              |           |  3b    3a |  3b    3a |           |
              +    c1     +--+--+--+--+--+--+--+--+     c2    +
              |           |     |           |     |           |
              +         2b+ p1  +           +  p2 +3a         +
              |       3a  |     |           |     |  2b       |
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
              |       2b  |     |           |     |  3a       |
              +         3a+ p6  +           + p5  +2b         +
              |           |     |           |     |           |
              +    c4     +--+--+--+--+--+--+--+--+     c3    +
              |           |  3a       |        3b |           |
              +           +     b6    +     b5    +           +
              |  Piece4x4 | Border4x2 | Border4x2 |  Piece4x4 |
              +--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+

        """

        nr = options['nr'][0]
        sol = self._load_solution(nr)

        print('c1.side2b=%s' % sol.c1.side2b)
        print('b1.side3b=%s' % sol.b1.side3b)

        count = 0
        used_nrs0 = (139,)
        for p1, used_nrs1 in self._find_p_4_1(used_nrs0, sol.c1.side2b, sol.b1.side3b):
            print('p1=%s' % p1.nr)
            for p2, used_nrs2 in self._find_p_1_2(used_nrs1, sol.b2.side3a, sol.c1.side3a):
                for p3, used_nrs3 in self._find_p_1_2(used_nrs2, sol.c2.side2b, sol.b3.side3b):
                    for p4, used_nrs4 in self._find_p_2_3(used_nrs3, sol.b4.side3a, sol.c3.side3a):
                        for p5, used_nrs5 in self._find_p_2_3(used_nrs4, sol.c3.side2b, sol.b5.side3b):
                            for p6, used_nrs6 in self._find_p_3_4(used_nrs5, sol.b6.side3a, sol.c4.side3a):
                                for p7, used_nrs7 in self._find_p_3_4(used_nrs6, sol.c4.side2b, sol.b7.side3b):
                                    for p8, _ in self._find_p_4_1(used_nrs7, sol.b8.side3a, sol.c1.side3a):
                                        count += 1
                                        self.stdout.write('p1=%s, p2=%s, p3=%s, p4=%s, p5=%s, p6=%s, p7=%s, p8=%s' % (
                                                          p1.nr, p2.nr, p3.nr, p4.nr, p5.nr, p6.nr, p7.nr, p8.nr))
                                    #for
                                # for
                            # for
                        # for
                    # for
                # for
            # for
        # for

        self.stdout.write('[INFO] Found %s solutions' % count)

# end of file
