# -*- coding: utf-8 -*-

#  Copyright (c) 2023 Ramon van der Winkel.
#  All rights reserved.
#  Licensed under BSD-3-Clause-Clear. See LICENSE file for details.

# maak een account HWL van specifieke vereniging, vanaf de commandline

from django.core.management.base import BaseCommand
from BasePieces.hints import HINT_NRS
from Pieces2x2.models import TwoSides, Piece2x2
from Pieces4x4.models import Piece4x4

USE_CACHE = True
DO_STORE = True


class Command(BaseCommand):

    help = "Generate all 4x4 pieces"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.stdout.write('[INFO] Creating side reverse look-up table')

        # load all TwoSides and calculate to what number it matches
        self.side_nr2reverse = dict()       # [side nr] = reverse side nr
        self.side_nr_is_border = dict()     # [side nr] = True/False

        two_sides2nr = dict()   # ['XX'] = nr
        for two in TwoSides.objects.all():
            two_sides2nr[two.two_sides] = two.nr
            self.side_nr_is_border[two.nr] = two.two_sides == 'XX'
        # for
        for two in TwoSides.objects.all():
            reverse = two.two_sides[1] + two.two_sides[0]
            try:
                self.side_nr2reverse[two.nr] = two_sides2nr[reverse]
            except KeyError:
                self.side_nr2reverse[two.nr] = 9999   # bestaat niet
        # for
        self.side_border = two_sides2nr['XX']

        self.stdout.write('[INFO] Creating piece4 cache')

        self.piece4 = dict()    # [(side1, side2)] = [Piece2x2, ...]
        for piece in Piece2x2.objects.all():
            tup = (piece.side1, piece.side2)
            try:
                self.piece4[tup].append(piece)
            except KeyError:
                self.piece4[tup] = [piece]
        # for

        self.stdout.write('[INFO] Done')

    def add_arguments(self, parser):
        parser.add_argument('nr', nargs=1, help="piece2x2 nr for first position")

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

    def _iter_piece4(self, expected_side1, expected_side2, nr1, used_nrs):
        if USE_CACHE:
            tup = (expected_side1, expected_side2)
            try:
                for piece in self.piece4[tup]:
                    if piece.nr < nr1:
                        continue
                    if piece.nr1 in used_nrs or piece.nr2 in used_nrs or piece.nr3 in used_nrs or piece.nr4 in used_nrs:
                        continue
                    yield piece
                # for
            except KeyError:
                pass
        else:
            for piece in (Piece2x2
                          .objects
                          .filter(side1=expected_side1,
                                  side2=expected_side2)
                          .exclude(nr__lte=nr1)                 # prevents rotation variants
                          .exclude(nr1__in=used_nrs)
                          .exclude(nr2__in=used_nrs)
                          .exclude(nr3__in=used_nrs)
                          .exclude(nr4__in=used_nrs)):
                yield piece
            # for

    def handle(self, *args, **options):

        first_nr = int(options['nr'][0])
        print('[INFO] Select first piece2x2 nr: %s' % first_nr)

        # delete all previously generate 4x4 pieces with this starting piece
        if DO_STORE:
            Piece4x4.objects.filter(nr1=first_nr).delete()

        base_nr = first_nr * 100 * 1000000  # = 100M
        print('[INFO] base_nr: %s' % base_nr)

        """ a 4x4 piece consists of 4 Piece2x2, each under a certain rotation

            each side consists of 4 base piece sides and is given a new simple numeric

                     side 1
                   +---+---+
                   | 1 | 2 |
            side 4 +---+---+ side 2
                   | 4 | 3 |
                   +---+---+
                     side 3
        """

        tup1 = tup2 = tup3 = tup4 = tup5 = tup6 = tup7 = tup8 = tup11 = tup12 = tup15 = tup16 = (0, 0)

        count_piece1 = 0
        todo_piece1 = 0
        for _ in self._iter_piece1(first_nr):
            todo_piece1 += 1
        # for
        print('[INFO] Todo piece1: %s' % todo_piece1)

        nr = 0
        print_nr = print_interval = 50000
        limit = -1
        bulk = list()
        for piece1 in self._iter_piece1(first_nr):

            perc_piece1 = 1 - (count_piece1 / todo_piece1)
            count_piece1 += 1
            print('[INFO] piece1: %s / %s (%.2f%% left)' % (count_piece1, todo_piece1, perc_piece1 * 100))

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

                            piece = Piece4x4(
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
                            bulk.append(piece)

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
