# -*- coding: utf-8 -*-

#  Copyright (c) 2023 Ramon van der Winkel.
#  All rights reserved.
#  Licensed under BSD-3-Clause-Clear. See LICENSE file for details.

# maak een account HWL van specifieke vereniging, vanaf de commandline

from django.core.management.base import BaseCommand
from BasePieces.hints import HINT_NRS
from BasePieces.models import BasePiece
from Pieces2x2.models import TwoSides, Piece2x2
from Pieces4x4.models import Piece4x4


class Command(BaseCommand):

    help = "Check all 4x4 pieces"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.stdout.write('[INFO] Creating base piece cache')
        self.base_pieces = dict()   # [nr] = BasePiece
        for piece in BasePiece.objects.all():
            self.base_pieces[piece.nr] = piece
        # for

        self.stdout.write('[INFO] Creating side reverse look-up table')

        # load all TwoSides and calculate to what number it matches
        self.two_sides2nr = dict()          # ["AB"] = side nr
        self.side_nr2reverse = dict()       # [side nr] = reverse side nr
        # self.side_nr_is_border = dict()     # [side nr] = True/False

        for two in TwoSides.objects.all():
            self.two_sides2nr[two.two_sides] = two.nr
            # self.side_nr_is_border[two.nr] = two.two_sides == 'XX'
        # for
        for two in TwoSides.objects.all():
            reverse = two.two_sides[1] + two.two_sides[0]
            try:
                self.side_nr2reverse[two.nr] = self.two_sides2nr[reverse]
            except KeyError:
                self.side_nr2reverse[two.nr] = 9999   # bestaat niet
        # for
        self.border_side_nr = self.two_sides2nr['XX']

    def add_arguments(self, parser):
        parser.add_argument('nr', nargs=1, help="piece4x4 to start checking")
        parser.add_argument('count', nargs=1, help="number of pieces to check")

    def _iter_piece1(self, nr):
        # no inner border wanted on the internals of the 2x2 (sides 2 and 3 of the top-left piece)
        for piece in Piece2x2.objects.filter(nr1=nr).exclude(side2=self.side_border).exclude(side3=self.side_border):
            yield piece
        # for

    def _iter_piece2(self, expected_side4, nr1, used_nrs):
        # zoek stukken met de gevraagde kleur aan de juiste kant
        for piece in (Piece2x2
                      .objects
                      .filter(side4=expected_side4)
                      .exclude(side2=self.side_border)
                      .exclude(side3=self.side_border)
                      .exclude(nr__lte=nr1)                 # prevents rotation variants
                      .exclude(nr1__in=used_nrs)
                      .exclude(nr2__in=used_nrs)
                      .exclude(nr3__in=used_nrs)
                      .exclude(nr4__in=used_nrs)):
            yield piece
        # for

    @staticmethod
    def _iter_piece3(expected_side1, nr1, piece1_is_corner, used_nrs):
        qset = (Piece2x2
                .objects
                .filter(side1=expected_side1)
                .exclude(nr__lte=nr1)                 # prevents rotation variants
                .exclude(nr1__in=used_nrs)
                .exclude(nr2__in=used_nrs)
                .exclude(nr3__in=used_nrs)
                .exclude(nr4__in=used_nrs))

        if piece1_is_corner:
            # top-left base piece of piece 3 needs to be one of the 4 hint pieces
            qset = qset.filter(nr1__in=HINT_NRS)

        for piece in qset:
            yield piece
        # for

    def find_a(self, p4x4, used_nrs):
        """ piece A has side1=border and side4 must fit the piece4x4 """

        expected_side1 = self.border_side_nr

        nr4_side2 = self.base_pieces[p4x4.nr4].get_side(2, p4x4.rot4)
        nr8_side2 = self.base_pieces[p4x4.nr8].get_side(2, p4x4.rot8)
        side2 = self.two_sides2nr[nr4_side2 + nr8_side2]
        expected_side4 = self.side_nr2reverse[side2]

        qset = (Piece2x2
                .objects
                .filter(side1=expected_side1,
                        side4=expected_side4)
                .exclude(nr1__in=used_nrs)
                .exclude(nr2__in=used_nrs)
                .exclude(nr3__in=used_nrs)
                .exclude(nr4__in=used_nrs))

        for piece in qset:
            yield piece

    def find_b(self, p4x4, used_nrs):
        """ piece B has side4=border and side1 must fit the piece4x4 """

        expected_side4 = self.border_side_nr

        nr14_side3 = self.base_pieces[p4x4.nr14].get_side(3, p4x4.rot14)
        nr13_side3 = self.base_pieces[p4x4.nr13].get_side(3, p4x4.rot13)
        side3 = self.two_sides2nr[nr14_side3 + nr13_side3]
        expected_side1 = self.side_nr2reverse[side3]

        qset = (Piece2x2
                .objects
                .filter(side1=expected_side1,
                        side4=expected_side4)
                .exclude(nr1__in=used_nrs)
                .exclude(nr2__in=used_nrs)
                .exclude(nr3__in=used_nrs)
                .exclude(nr4__in=used_nrs))

        for piece in qset:
            yield piece

    def find_c(self, p4x4, expected_side4, used_nrs):
        """ piece C has side4=must fit piece B and side1 must fit the piece4x4 """

        nr16_side3 = self.base_pieces[p4x4.nr16].get_side(3, p4x4.rot16)
        nr15_side3 = self.base_pieces[p4x4.nr15].get_side(3, p4x4.rot15)
        side3 = self.two_sides2nr[nr16_side3 + nr15_side3]
        expected_side1 = self.side_nr2reverse[side3]

        qset = (Piece2x2
                .objects
                .filter(side1=expected_side1,
                        side4=expected_side4)
                .exclude(nr1__in=used_nrs)
                .exclude(nr2__in=used_nrs)
                .exclude(nr3__in=used_nrs)
                .exclude(nr4__in=used_nrs))

        for piece in qset:
            yield piece

    def find_d(self, p4x4, expected_side1, used_nrs):
        """ piece D has side1=must fit piece A and side4 must fit the piece4x4 """

        nr12_side2 = self.base_pieces[p4x4.nr12].get_side(2, p4x4.rot12)
        nr16_side2 = self.base_pieces[p4x4.nr16].get_side(2, p4x4.rot16)
        side2 = self.two_sides2nr[nr12_side2 + nr16_side2]
        expected_side4 = self.side_nr2reverse[side2]

        qset = (Piece2x2
                .objects
                .filter(side1=expected_side1,
                        side4=expected_side4)
                .exclude(nr1__in=used_nrs)
                .exclude(nr2__in=used_nrs)
                .exclude(nr3__in=used_nrs)
                .exclude(nr4__in=used_nrs))

        for piece in qset:
            yield piece

    @staticmethod
    def find_e(expected_side1, expected_side4, used_nrs):
        qset = (Piece2x2
                .objects
                .filter(side1=expected_side1,
                        side4=expected_side4)
                .exclude(nr1__in=used_nrs)
                .exclude(nr2__in=used_nrs)
                .exclude(nr3__in=used_nrs)
                .exclude(nr4__in=used_nrs))

        piece = qset.first()
        return piece is not None

    def check_piece4x4(self, p4x4, used_nrs):
        """
            Check that the 4x4 can be covered in 2x2 pieces around it
            Returns True when piece is OK
        
                +---+---+---+---+---+---+
                | 1 | 2 | 3 | 4 |       |
                +---+---+---+---+   A   +
                | 5 | 6 | 7 | 8 |       |
                +---+---+---+---+---+---+
                | 9 |10 |11 |12 |       |
                +---+---+---+---+   D   +
                |13 |14 |15 |16 |       |
                +---+---+---+---+---+---+
                |       |       |       |
                +   B   +   C   +   E   +
                |       |       |       |
                +---+---+---+---+---+---+
        """
        self.stdout.write('[INFO] Checking Piece4x4 nr %s' % p4x4.nr)

        for piece_a in self.find_a(p4x4, used_nrs):
            used_nrs2 = used_nrs + [piece_a.nr1, piece_a.nr2, piece_a.nr3, piece_a.nr4]
            piece_d_expected_side1 = self.side_nr2reverse[piece_a.side3]

            for piece_b in self.find_b(p4x4, used_nrs2):
                used_nrs3 = used_nrs2 + [piece_b.nr1, piece_b.nr2, piece_b.nr3, piece_b.nr4]
                piece_c_expected_side4 = self.side_nr2reverse[piece_b.side2]

                for piece_c in self.find_c(p4x4, piece_c_expected_side4, used_nrs3):
                    used_nrs4 = used_nrs3 + [piece_c.nr1, piece_c.nr2, piece_c.nr3, piece_c.nr4]
                    piece_e_expected_side4 = self.side_nr2reverse[piece_c.side2]

                    for piece_d in self.find_d(p4x4, piece_d_expected_side1, used_nrs4):
                        used_nrs5 = used_nrs4 + [piece_d.nr1, piece_d.nr2, piece_d.nr3, piece_d.nr4]
                        piece_e_expected_side1 = self.side_nr2reverse[piece_d.side3]

                        if self.find_e(piece_e_expected_side1, piece_e_expected_side4, used_nrs5):
                            return True
                    # for
                # for
            # for
        # for

        return False

    def handle(self, *args, **options):

        check_nr = int(options['nr'][0])
        check_todo = int(options['count'][0])

        limit = -1
        bulk = list()
        while check_todo > 0:
            try:
                p4x4 = Piece4x4.objects.get(nr=check_nr)
            except Piece4x4.DoesNotExist:
                pass
            else:
                used_nrs = [p4x4.nr1, p4x4.nr2, p4x4.nr3, p4x4.nr4, p4x4.nr5, p4x4.nr6, p4x4.nr7, p4x4.nr8,
                            p4x4.nr9, p4x4.nr10, p4x4.nr11, p4x4.nr12, p4x4.nr13, p4x4.nr14, p4x4.nr15, p4x4.nr16]
                if len(set(used_nrs)) != 16:
                    self.stdout.write('[ERROR] Piece %s does not have 16 unique base pieces: %s' % (p4x4.nr, repr(used_nrs)))
                else:
                    if not self.check_piece4x4(p4x4, used_nrs):
                        self.stdout.write('[ERROR] Piece %s is bad' % p4x4.nr)

            check_nr += 1
            check_todo -=1
        # while

        return
        for piece1 in self._iter_piece1(first_nr):

            piece1_is_corner = piece1.side4 == self.side_border and piece1.side1 == self.side_border

            base1 = [piece1.nr1, piece1.nr2, piece1.nr3, piece1.nr4]
            used_nrs1 = set(base1)
            # if len(used_nrs1) != 4:
            #     print('piece1 not 4 unique pieces!')
            #     continue

            if DO_STORE:
                tup1 = (piece1.nr1, piece1.rot1)
                tup2 = (piece1.nr2, piece1.rot2)
                tup5 = (piece1.nr3, piece1.rot3)
                tup6 = (piece1.nr4, piece1.rot4)

            expected_side4 = self.side_nr2reverse[piece1.side2]
            for piece2 in self._iter_piece2(expected_side4, piece1.nr, used_nrs1):

                base2 = [piece2.nr1, piece2.nr2, piece2.nr3, piece2.nr4]
                used_nrs2 = set(base1 + base2)
                # if len(used_nrs2) != 8:
                #     print('piece1 + piece2 not 8 unique pieces!')
                #     continue

                if DO_STORE:
                    tup3 = (piece2.nr1, piece2.rot1)
                    tup4 = (piece2.nr2, piece2.rot2)
                    tup7 = (piece2.nr3, piece2.rot3)
                    tup8 = (piece2.nr4, piece2.rot4)

                expected_side1 = self.side_nr2reverse[piece2.side3]
                for piece3 in self._iter_piece3(expected_side1, piece1.nr, piece1_is_corner, used_nrs2):

                    base3 = [piece3.nr1, piece3.nr2, piece3.nr3, piece3.nr4]
                    used_nrs3 = set(base1 + base2 + base3)
                    # if len(used_nrs3) != 12:
                    #     print('piece1 + piece2 + piece3 not 12 unique pieces!')
                    #     continue

                    if DO_STORE:
                        tup11 = (piece3.nr1, piece3.rot1)
                        tup12 = (piece3.nr2, piece3.rot2)
                        tup15 = (piece3.nr3, piece3.rot3)
                        tup16 = (piece3.nr4, piece3.rot4)

                    expected_side1 = self.side_nr2reverse[piece1.side3]
                    expected_side2 = self.side_nr2reverse[piece3.side4]
                    for piece4 in self._iter_piece4(expected_side1, expected_side2, piece1.nr, used_nrs3):

                        # base4 = [piece4.nr1, piece4.nr2, piece4.nr3, piece4.nr4]
                        # used_nrs4 = set(base1 + base2 + base3 + base4)
                        # if len(used_nrs4) != 16:
                        #     print('piece1 + piece2 + piece3 + piece4 not 16 unique pieces!')
                        #     continue

                        nr += 1

                        if DO_STORE:
                            tup9 = (piece4.nr1, piece4.rot1)
                            tup10 = (piece4.nr2, piece4.rot2)
                            tup13 = (piece4.nr3, piece4.rot3)
                            tup14 = (piece4.nr4, piece4.rot4)

                            p4x4 = Piece4x4(
                                        nr=base_nr + nr,
                                        side1=0,
                                        side2=0,
                                        side3=0,
                                        side4=0,
                                        nr1=tup1[0], rot1=tup1[1],
                                        nr2=tup2[0], rot2=tup2[1],
                                        nr3=tup3[0], rot3=tup3[1],
                                        nr4=tup4[0], rot4=tup4[1],
                                        nr5=tup5[0], rot5=tup5[1],
                                        nr6=tup6[0], rot6=tup6[1],
                                        nr7=tup7[0], rot7=tup7[1],
                                        nr8=tup8[0], rot8=tup8[1],
                                        nr9=tup9[0], rot9=tup9[1],
                                        nr10=tup10[0], rot10=tup10[1],
                                        nr11=tup11[0], rot11=tup11[1],
                                        nr12=tup12[0], rot12=tup12[1],
                                        nr13=tup13[0], rot13=tup13[1],
                                        nr14=tup14[0], rot14=tup14[1],
                                        nr15=tup15[0], rot15=tup15[1],
                                        nr16=tup16[0], rot16=tup16[1],
                                        piece2x2_nr1=piece1.nr)
                            bulk.append(p4x4)

                            if len(bulk) >= 1000:
                                Piece4x4.objects.bulk_create(bulk)
                                bulk = list()
                                if limit != -1 and nr > limit:
                                    return

                        if nr >= print_nr:
                            print(nr, piece2.nr)
                            print_nr += print_interval
                    # for
                # for
            # for
        # for

        if len(bulk):
            Piece4x4.objects.bulk_create(bulk)

        print('[INFO] Totaal: %s' % nr)

# end of file
