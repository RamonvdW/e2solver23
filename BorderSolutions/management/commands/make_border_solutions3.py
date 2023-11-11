# -*- coding: utf-8 -*-

#  Copyright (c) 2023 Ramon van der Winkel.
#  All rights reserved.
#  Licensed under BSD-3-Clause-Clear. See LICENSE file for details.

from django.core.management.base import BaseCommand
from BasePieces.models import BasePiece
from Borders4x2.models import Border4x2
from BorderSolutions.models import BorderSolution
from Pieces4x4.models import Piece4x4


class Command(BaseCommand):

    help = "Generate border solutions from Piece4x4 and Border4x2"

    # 208: top left
    # 181: bottom left
    # 249: bottom right
    # 255: top right
    hint_c1, hint_c2, hint_c3, hint_c4 = (208, 255, 249, 181)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.nr = 0

        # cache all base pieces
        self.base_pieces = dict()       # [nr] = BasePiece()
        for piece in BasePiece.objects.all():
            self.base_pieces[piece.nr] = piece
        # for

    def get_4x4_side2a_reverse(self, piece4x4):
        p4 = self.base_pieces[piece4x4.nr4]
        p8 = self.base_pieces[piece4x4.nr8]
        # side2a = p4.get_side(2, piece4x4.rot4) + p8.get_side(2, piece4x4.rot8)
        side2a_reverse = p8.get_side(2, piece4x4.rot8) + p4.get_side(2, piece4x4.rot4)
        return side2a_reverse

    def get_4x4_side3b_reverse(self, piece4x4):
        p13 = self.base_pieces[piece4x4.nr13]
        p14 = self.base_pieces[piece4x4.nr14]
        # side3b = p14.get_side(3, piece4x4.rot14) + p13.get_side(3, piece4x4.rot13)
        side3b_reverse = p13.get_side(3, piece4x4.rot13) + p14.get_side(3, piece4x4.rot14)
        return side3b_reverse

    def _iter_corner(self, used_nrs, hint_nr):
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

            exp_side4 = self.get_4x4_side2a_reverse(c)
            exp_side2 = self.get_4x4_side3b_reverse(c)

            used_nrs2 = used_nrs + c_nrs

            yield c, used_nrs2, exp_side4, exp_side2
        # for

    @staticmethod
    def _iter_border_side2(used_nrs, exp_side2):
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

            exp_side2 = b.side4[1] + b.side4[0]

            yield b, used_nrs2, exp_side2
        # for
            
    @staticmethod
    def _iter_border_side4(used_nrs, exp_side4):
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

            exp_side4 = b.side2[1] + b.side2[0]

            yield b, used_nrs, exp_side4
        # for

    @staticmethod
    def _iter_border_side2_side4(used_nrs, exp_side2, exp_side4):
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

            yield b, used_nrs2
        # for

    def _find_solution_with_c1(self, c1, used_nrs1, b1_exp_side4, b8_exp_side2):
        """ Find and store the first solution with c1 """
        for b8, used_nrs2, b7_exp_side2 in self._iter_border_side2(used_nrs1,
                                                                   b8_exp_side2):
            # self.stdout.write('b8: %s' % b8.nr)
            for b1, used_nrs3, b2_exp_side4 in self._iter_border_side4(used_nrs2,
                                                                       b1_exp_side4):
                # self.stdout.write('b1: %s' % b1.nr)

                # take one corner and fit two border pieces
                # b2 c2 b3
                for c2, used_nrs4, b3_exp_side4, b2_exp_side2 in self._iter_corner(used_nrs3,
                                                                                   self.hint_c2):
                    # self.stdout.write('c2: %s' % c2.nr)
                    for b2, used_nrs5 in self._iter_border_side2_side4(used_nrs4,
                                                                       b2_exp_side2,
                                                                       b2_exp_side4):
                        # self.stdout.write('b2: %s' % b2.nr)
                        for b3, used_nrs6, b4_exp_side4 in self._iter_border_side4(used_nrs5,
                                                                                   b3_exp_side4):
                            # self.stdout.write('b3: %s' % b3.nr)

                            # take one corner and connect to existing border on one side
                            # c4 b7
                            for c4, used_nrs7, b7_exp_side4, b6_exp_side2 in self._iter_corner(used_nrs6,
                                                                                               self.hint_c4):
                                # self.stdout.write('c4: %s' % c4.nr)
                                for b7, used_nrs8 in self._iter_border_side2_side4(used_nrs7,
                                                                                   b7_exp_side2,
                                                                                   b7_exp_side4):
                                    # self.stdout.write('b7: %s' % b7.nr)

                                    # take last corner and fit to existing border on one side
                                    # b4 c3
                                    for c3, used_nrs9, b5_exp_side4, b4_exp_side2 in self._iter_corner(used_nrs8,
                                                                                                       self.hint_c3):
                                        # self.stdout.write('c3: %s' % c3.nr)
                                        for b4, used_nrs10 in self._iter_border_side2_side4(used_nrs9,
                                                                                            b4_exp_side2,
                                                                                            b4_exp_side4):
                                            # self.stdout.write('b4: %s' % b4.nr)

                                            # fill the last two borders
                                            # b5 b6
                                            for b5, used_nrs11, b6_exp_side4 in self._iter_border_side4(used_nrs10,
                                                                                                        b5_exp_side4):
                                                # self.stdout.write('b5: %s' % b5.nr)

                                                for b6, _ in self._iter_border_side2_side4(used_nrs11,
                                                                                           b6_exp_side2,
                                                                                           b6_exp_side4):
                                                    # self.stdout.write('b6: %s' % b6.nr)

                                                    self.nr += 1
                                                    solution = BorderSolution(
                                                        nr=self.nr,
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
                                                    self.stdout.write('[INFO] Solutions: %s' % self.nr)

                                                    # found enough solutions with c1
                                                    return
                                                
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

        """

        # delete the old solutions
        BorderSolution.objects.all().delete()

        self.nr = 0

        # take one corner and fit two border pieces
        # b8 c1 b1
        used_nrs = ()
        for c1, used_nrs1, b1_exp_side4, b8_exp_side2 in self._iter_corner(used_nrs,
                                                                           self.hint_c1):
            self.stdout.write('c1: %s' % c1.nr)
            self._find_solution_with_c1(c1, used_nrs1, b1_exp_side4, b8_exp_side2)
        # for

        self.stdout.write('[INFO] Done!')

# end of file
