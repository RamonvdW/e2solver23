# -*- coding: utf-8 -*-

#  Copyright (c) 2023 Ramon van der Winkel.
#  All rights reserved.
#  Licensed under BSD-3-Clause-Clear. See LICENSE file for details.

# maak een account HWL van specifieke vereniging, vanaf de commandline

from django.core.management.base import BaseCommand
from BasePieces.models import BasePiece
from Pieces2x2.models import Piece2x2, TwoSides
from Borders4x2.models import Border4x2


class Command(BaseCommand):

    help = "Generate all 8x2 pieces along the border"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.skip_base_nrs = (181, 208, 249, 255, 139)

        self.base_nr2piece = dict()     # [nr] = BasePiece
        for piece in BasePiece.objects.all():
            self.base_nr2piece[piece.nr] = piece
        # for

        # load all TwoSides and calculate to what number it matches
        self.side_nr2reverse = dict()       # [side nr] = reverse side nr

        two_sides2nr = dict()   # ['XX'] = nr
        for two in TwoSides.objects.all():
            two_sides2nr[two.two_sides] = two.nr
        # for
        for two in TwoSides.objects.all():
            reverse = two.two_sides[1] + two.two_sides[0]
            try:
                self.side_nr2reverse[two.nr] = two_sides2nr[reverse]
            except KeyError:
                self.side_nr2reverse[two.nr] = 9999   # bestaat niet
        # for

    def handle(self, *args, **options):

        # delete all previously generate 8x2 pieces
        Border4x2.objects.all().delete()

        """ a 8x2 piece consists of 16 base pieces, each under a certain rotation
            the four sides start at the top and follow the piece clockwise

                              side1 = border
                    +---+---+---+---+---+---+---+---+
                    | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 |
             side 4 +---+---+---+---+---+---+---+---+ side 2
                    | 9 |10 |11 |12 |13 |14 |15 |16 |
                    +---+---+---+---+---+---+---+---+
                                side 3

                              side1 = border
                    +---+---+---+---+---+---+---+---+
                    |       |       |       |       |
                    +   A   +   B   +   C   +   D   +
                    |       |       |       |       |
                    +---+---+---+---+---+---+---+---+

            Piece 2x2:
             
                      side 1
                    +---+---+
                    | 1 | 2 |
             side 4 +---+---+ side 2
                    | 3 | 4 |
                    +---+---+
                      side 3
        """

        side_border_nr = TwoSides.objects.filter(two_sides='XX').first().nr

        nr = 0
        bulk = list()
        print_nr = print_interval = 250000
        for piece_a in (Piece2x2
                        .objects
                        .filter(side1=side_border_nr)
                        .exclude(side4=side_border_nr)
                        .exclude(side2=side_border_nr)):

            print('piece_a.nr=%s' % piece_a.nr)

            base_a = (piece_a.nr1, piece_a.nr2, piece_a.nr3, piece_a.nr4)
            used_nrs = set(base_a)

            final_side4 = self.base_nr2piece[piece_a.nr3].get_side(4, piece_a.rot3)
            final_side4 += self.base_nr2piece[piece_a.nr1].get_side(4, piece_a.rot1)

            piece_b_side_4 = self.side_nr2reverse[piece_a.side2]

            for piece_b in (Piece2x2
                            .objects
                            .filter(side1=side_border_nr, side4=piece_b_side_4)
                            .exclude(nr1__in=used_nrs)
                            .exclude(nr2__in=used_nrs)
                            .exclude(nr3__in=used_nrs)
                            .exclude(nr4__in=used_nrs)):

                base_b = (piece_b.nr1, piece_b.nr2, piece_b.nr3, piece_b.nr4)
                used_nrs = set(base_a + base_b)

                piece_c_side_4 = self.side_nr2reverse[piece_b.side2]

                for piece_c in (Piece2x2
                                .objects
                                .filter(side1=side_border_nr,
                                        side4=piece_c_side_4)
                                .exclude(nr1__in=used_nrs)
                                .exclude(nr2__in=used_nrs)
                                .exclude(nr3__in=used_nrs)
                                .exclude(nr4__in=used_nrs)):

                    base_c = (piece_c.nr1, piece_c.nr2, piece_c.nr3, piece_c.nr4)
                    used_nrs = set(base_a + base_b + base_c)

                    piece_d_side_4 = self.side_nr2reverse[piece_c.side2]

                    for piece_d in (Piece2x2
                                    .objects
                                    .filter(side1=side_border_nr,
                                            side4=piece_d_side_4)
                                    .exclude(nr1__in=used_nrs)
                                    .exclude(nr2__in=used_nrs)
                                    .exclude(nr3__in=used_nrs)
                                    .exclude(nr4__in=used_nrs)):

                        nr += 1

                        final_side2 = self.base_nr2piece[piece_d.nr2].get_side(2, piece_d.rot2)
                        final_side2 += self.base_nr2piece[piece_d.nr4].get_side(2, piece_d.rot4)

                        piece = Border4x2(
                                    nr=nr,
                                    side2=final_side2,
                                    side4=final_side4,
                                    nr1=piece_a.nr1,
                                    nr2=piece_a.nr2,
                                    nr3=piece_b.nr1,
                                    nr4=piece_b.nr2,
                                    nr5=piece_c.nr1,
                                    nr6=piece_c.nr2,
                                    nr7=piece_d.nr1,
                                    nr8=piece_d.nr2,
                                    rot1=piece_a.rot1,
                                    rot2=piece_a.rot2,
                                    rot3=piece_b.rot1,
                                    rot4=piece_b.rot2,
                                    rot5=piece_c.rot1,
                                    rot6=piece_c.rot2,
                                    rot7=piece_d.rot1,
                                    rot8=piece_d.rot2)
                        bulk.append(piece)

                        if len(bulk) > 1000:
                            Border4x2.objects.bulk_create(bulk)
                            bulk = list()

                        if nr >= print_nr:
                            self.stdout.write('%s' % nr)
                            print_nr += print_interval
                    # for
                # for
            # for
        # for

        self.stdout.write('[INFO] Total generated: %s' % nr)

# end of file
