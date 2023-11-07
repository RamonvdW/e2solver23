# -*- coding: utf-8 -*-

#  Copyright (c) 2023 Ramon van der Winkel.
#  All rights reserved.
#  Licensed under BSD-3-Clause-Clear. See LICENSE file for details.

# maak een account HWL van specifieke vereniging, vanaf de commandline

from django.core.management.base import BaseCommand
from BasePieces.models import BasePiece
from BasePieces.hints import HINT_NRS
from Borders4x2.models import Border4x2
from BorderSolutions.models import BorderSolution
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

    def _iter_corner(self, used_nrs, hint_nr, nr_floor):
        for c in (Piece4x4
                  .objects
                  .filter(nr__gt=nr_floor,
                          nr11=hint_nr)
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
                  .iterator(chunk_size=10000)):

            c_nrs = (c.nr1, c.nr2, c.nr3, c.nr4, c.nr5, c.nr6, c.nr7, c.nr8,
                     c.nr9, c.nr10, c.nr11, c.nr12, c.nr13, c.nr14, c.nr15, c.nr16)

            exp_side4 = self.get_4x4_side2a_reverse(c)
            exp_side2 = self.get_4x4_side3b_reverse(c)

            used_nrs2 = used_nrs + c_nrs

            yield c, used_nrs2, exp_side4, exp_side2
        # for

    @staticmethod
    def _iter_border(used_nrs1, b1_exp_side4, b2_exp_side2):
        for b1 in (Border4x2
                   .objects
                   .filter(side4=b1_exp_side4)
                   .exclude(nr1__in=used_nrs1)
                   .exclude(nr2__in=used_nrs1)
                   .exclude(nr3__in=used_nrs1)
                   .exclude(nr4__in=used_nrs1)
                   .exclude(nr5__in=used_nrs1)
                   .exclude(nr6__in=used_nrs1)
                   .exclude(nr7__in=used_nrs1)
                   .exclude(nr8__in=used_nrs1)
                   .iterator(chunk_size=10000)):

            b1_nrs = (b1.nr1, b1.nr2, b1.nr3, b1.nr4, b1.nr5, b1.nr6, b1.nr7, b1.nr8)
            used_nrs2 = used_nrs1 + b1_nrs

            b2_exp_side4 = b1.side2[1] + b1.side2[0]

            for b2 in (Border4x2
                       .objects
                       .filter(side4=b2_exp_side4,
                               side2=b2_exp_side2)
                       .exclude(nr1__in=used_nrs2)
                       .exclude(nr2__in=used_nrs2)
                       .exclude(nr3__in=used_nrs2)
                       .exclude(nr4__in=used_nrs2)
                       .exclude(nr5__in=used_nrs2)
                       .exclude(nr6__in=used_nrs2)
                       .exclude(nr7__in=used_nrs2)
                       .exclude(nr8__in=used_nrs2)):

                b2_nrs = (b2.nr1, b2.nr2, b2.nr3, b2.nr4, b2.nr5, b2.nr6, b2.nr7, b2.nr8)
                used_nrs3 = used_nrs2 + b2_nrs

                yield b1, b2, used_nrs3

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

        hint_c1, hint_c2, hint_c3, hint_c4 = HINT_NRS

        nr = 0
        used_nrs = (0,)

        # take 2 corners, then fit two borders in between
        # c1 b1 b2 c2
        for c1, used_nrs1, b1_exp_side4, b8_exp_side2 in self._iter_corner(used_nrs, hint_c1, 0):
            print('c1: %s' % c1.nr)

            for c2, used_nrs2, b3_exp_side4, b2_exp_side2 in self._iter_corner(used_nrs1, hint_c2, c1.nr):
                print('c2: %s' % c2.nr)

                for b1, b2, used_nrs3 in self._iter_border(used_nrs2, b1_exp_side4, b2_exp_side2):
                    print('b1: %s, b2: %s' % (b1.nr, b2.nr))
                    print('used_nrs3: %s' % repr(used_nrs3))

                    # take then next corner, then fit two borders in between
                    # c2 b3 b4 c3
                    for c3, used_nrs4, b5_exp_side4, b4_exp_side2 in self._iter_corner(used_nrs3, hint_c3, c2.nr):
                        print('c3: %s' % c3.nr)
                        print('used_nrs4: %s' % repr(used_nrs4))

                        for b3, b4, used_nrs5 in self._iter_border(used_nrs4, b3_exp_side4, b4_exp_side2):
                            print('b3: %s, b4: %s' % (b3.nr, b4.nr))
                            print('used_nrs5: %s' % repr(used_nrs5))

                            # take then next corner, then fit two borders in between
                            # c3 b5 b6 c4
                            for c4, used_nrs6, b7_exp_side4, b6_exp_side2 in self._iter_corner(used_nrs5, hint_c4, c3.nr):
                                print('c4: %s' % c4.nr)
                                print('used_nrs6: %s' % repr(used_nrs6))

                                for b5, b6, used_nrs7 in self._iter_border(used_nrs6, b5_exp_side4, b6_exp_side2):
                                    print('b5: %s, b6: %s' % (b5.nr, b6.nr))
                                    print('used_nrs7: %s' % repr(used_nrs7))

                                    # find the final two borders
                                    # c4 b7 b8 c1
                                    for b7, b8, _ in self._iter_border(used_nrs7, b7_exp_side4, b8_exp_side2):

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

# end of file
