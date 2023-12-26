# -*- coding: utf-8 -*-

#  Copyright (c) 2023 Ramon van der Winkel.
#  All rights reserved.
#  Licensed under BSD-3-Clause-Clear. See LICENSE file for details.

from django.core.management.base import BaseCommand
from BasePieces.models import BasePiece
from Pieces3x3.models import ThreeSide, Piece3x3

ALL_HINT_NRS = (139, 181, 208, 249, 255)
CENTER_HINT_NR = 139
CORNER_HINT_NRS = (181, 208, 249, 255)


class Command(BaseCommand):

    help = "Generate all 3x3 pieces, with rotation variants"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.three_sides = dict()       # ['XXX'] = nr
        self.three_sides_nr = 0

        self.base_with_side1 = dict()   # [side] = [(piece, rot), ..]
        self.base_with_side2 = dict()   # [side] = [(piece, rot), ..]
        self.base_with_side3 = dict()   # [side] = [(piece, rot), ..]
        self.base_with_side4 = dict()   # [side] = [(piece, rot), ..]

        self.with_interior = False
        self.with_corners = False
        self.with_center = False
        self.with_sides = False

        self.exclude_piece_nrs = list(range(1, 60+1))
        self.allow_hint_piece_nrs = (208, 255, 181, 249, 139)

    def _make_cache_base_with_side(self):
        all_sides = list()
        for piece in BasePiece.objects.exclude(nr__in=self.exclude_piece_nrs):
            side = piece.side4          # the only side where all possibilities are found
            if side not in all_sides:
                all_sides.append(side)
                self.base_with_side1[side] = list()
                self.base_with_side2[side] = list()
                self.base_with_side3[side] = list()
                self.base_with_side4[side] = list()
        # for
        all_sides.sort()

        for piece in BasePiece.objects.exclude(nr__in=self.exclude_piece_nrs):
            # rotations are counter-clockwise
            self.base_with_side1[piece.side1].append((piece, 0))
            self.base_with_side2[piece.side1].append((piece, 3))
            self.base_with_side3[piece.side1].append((piece, 2))
            self.base_with_side4[piece.side1].append((piece, 1))

            self.base_with_side1[piece.side2].append((piece, 1))
            self.base_with_side2[piece.side2].append((piece, 0))
            self.base_with_side3[piece.side2].append((piece, 3))
            self.base_with_side4[piece.side2].append((piece, 2))

            self.base_with_side1[piece.side3].append((piece, 2))
            self.base_with_side2[piece.side3].append((piece, 1))
            self.base_with_side3[piece.side3].append((piece, 0))
            self.base_with_side4[piece.side3].append((piece, 3))

            self.base_with_side1[piece.side4].append((piece, 3))
            self.base_with_side2[piece.side4].append((piece, 2))
            self.base_with_side3[piece.side4].append((piece, 1))
            self.base_with_side4[piece.side4].append((piece, 0))
        # for

    @staticmethod
    def _check_hint_piece_rot(nr, rot):
        if nr in (181, 208, 255):
            return rot == 1
        if nr == 139:
            return rot == 2
        if nr == 249:
            return rot == 0
        return True

    def _iter_piece1(self):
        for piece in BasePiece.objects.exclude(nr__in=self.exclude_piece_nrs):
            # some pieces are known to require a specific rotation
            if piece.nr in (181, 208, 255):
                yield piece, 1
            elif piece.nr == 139:
                yield piece, 2
            elif piece.nr == 249:
                yield piece, 0
            else:
                yield piece, 0
                yield piece, 1
                yield piece, 2
                yield piece, 3
        # for

    def _iter_piece_with_side4(self, expected_side4, used_nrs):
        # we want to match on side4
        for piece, rot in self.base_with_side4[expected_side4]:
            if piece.nr not in used_nrs:
                if self._check_hint_piece_rot(piece.nr, rot):
                    yield piece, rot
        # for

    def _iter_piece_with_side1(self, expected_side1, used_nrs):
        # we want to match on side1
        for piece, rot in self.base_with_side1[expected_side1]:
            if piece.nr not in used_nrs:
                if self._check_hint_piece_rot(piece.nr, rot):
                    yield piece, rot
        # for

    def _iter_piece_with_side4_side1(self, expected_side4, expected_side1, used_nrs):
        # we want to match on side4 and side1
        for piece, rot in self.base_with_side1[expected_side1]:
            if piece.nr not in used_nrs:
                if piece.get_side(4, rot) == expected_side4:
                    if self._check_hint_piece_rot(piece.nr, rot):
                        yield piece, rot
        # for

    def _get_three_sides_nr(self, side1, side2, side3):
        three_sides = side1 + side2 + side3
        try:
            nr = self.three_sides[three_sides]
        except KeyError:
            nr = self.three_sides_nr + 1
            self.three_sides_nr = nr
            ThreeSide(
                 nr=nr,
                 three_sides=three_sides).save()
            self.three_sides[three_sides] = nr
        return nr

    def _iter_row1(self):
        """
                      side 1
                   +---+---+---+
                   | 1 | 2 | 3 |
                   +---+---+---+
            side 4 | 4 | 5 | 6 | side 2
                   +---+---+---+
                   | 7 | 8 | 9 |
                   +---+---+---+
                       side 3
        """
        for piece1, rot1 in self._iter_piece1():
            piece1_side1 = piece1.get_side(1, rot1)
            piece1_side2 = piece1.get_side(2, rot1)
            piece1_side3 = piece1.get_side(3, rot1)
            piece1_side4 = piece1.get_side(4, rot1)

            # prevent borders on the inside
            if piece1_side2 == 'X' or piece1_side3 == 'X':
                continue

            piece1_is_hint = piece1 in ALL_HINT_NRS
            piece1_is_corner = piece1_side1 == 'X' and piece1_side4 == 'X'

            for piece2, rot2 in self._iter_piece_with_side4(piece1_side2,
                                                            (piece1.nr,)):
                if piece2.nr in CORNER_HINT_NRS:
                    continue

                piece2_side1 = piece2.get_side(1, rot2)
                piece2_side2 = piece2.get_side(2, rot2)
                piece2_side3 = piece2.get_side(3, rot2)

                # prevent borders on the inside
                if piece2_side2 == 'X' or piece2_side3 == 'X':
                    continue

                # check border compatibility piece1 and piece2
                if piece1_side1 == 'X':
                    if piece2_side1 != 'X':
                        continue
                else:
                    if piece2_side1 == 'X':
                        continue

                piece2_is_hint = piece2.nr in ALL_HINT_NRS

                if piece2_is_hint:
                    # hints cannot be together in the same 3x3
                    if piece1_is_hint:
                        continue
                    # if piece1_is_corner:        # not possible due to border
                    #     continue

                for piece3, rot3 in self._iter_piece_with_side4(piece2_side2,
                                                                (piece1.nr, piece2.nr)):
                    piece3_side1 = piece3.get_side(1, rot3)
                    piece3_side2 = piece3.get_side(2, rot3)
                    piece3_side3 = piece3.get_side(3, rot3)

                    # prevent borders on the inside
                    if piece3_side3 == 'X':
                        continue

                    # check border compatibility piece2
                    if piece2_side1 == 'X':
                        if piece3_side1 != 'X':
                            continue
                    else:
                        if piece3_side1 == 'X':
                            continue

                    # avoid impossible piece (borders on multiple sides)
                    if piece1_side4 == 'X':
                        if piece3_side2 == 'X':
                            continue

                    piece3_is_hint = piece3.nr in ALL_HINT_NRS

                    if piece3_is_hint:
                        # hints cannot be together in the same 3x3
                        if piece1_is_hint or piece2_is_hint:
                            continue
                        # if piece1_is_corner:      # not possible due to border
                        #     continue

                    piece3_is_corner = piece3_side1 == 'X' and piece3_side2 == 'X'
                    if piece3_is_corner:
                        if piece1_is_hint or piece2_is_hint:
                            continue

                    yield piece1, rot1, piece2, rot2, piece3, rot3

                # for
            # for
        # for

    def _iter_row2(self, row1):
        """
                      side 1
                   +---+---+---+
                   | 1 | 2 | 3 |
                   +---+---+---+
            side 4 | 4 | 5 | 6 | side 2
                   +---+---+---+
                   | 7 | 8 | 9 |
                   +---+---+---+
                       side 3
        """

        piece1, rot1, piece2, rot2, piece3, rot3 = row1
        has_hints = (piece1.nr in ALL_HINT_NRS or piece2.nr in ALL_HINT_NRS or piece3.nr in ALL_HINT_NRS)
        piece1_side4 = piece1.get_side(4, rot1)
        piece1_side1 = piece1.get_side(1, rot1)
        piece3_side1 = piece3.get_side(1, rot1)
        piece3_side2 = piece3.get_side(2, rot3)

        piece1_is_corner = piece1_side4 == 'X' and piece1_side1 == 'X'
        piece3_is_corner = piece3_side1 == 'X' and piece3_side2 == 'X'

        piece1_side3 = piece1.get_side(3, rot1)
        piece2_side3 = piece2.get_side(3, rot2)
        piece3_side3 = piece3.get_side(3, rot3)

        for piece4, rot4 in self._iter_piece_with_side1(piece1_side3,
                                                        (piece1.nr, piece2.nr, piece3.nr)):
            if piece4.nr in CORNER_HINT_NRS:
                continue

            piece4_side2 = piece4.get_side(2, rot4)
            piece4_side3 = piece4.get_side(3, rot4)
            piece4_side4 = piece4.get_side(4, rot4)

            # max 1 hint in a 3x3
            piece4_is_hint = piece4.nr in ALL_HINT_NRS
            if piece4_is_hint:
                if has_hints:
                    continue
                if piece1_is_corner or piece3_is_corner:
                    continue

            # avoid border on the inside
            if piece4_side2 == 'X' or piece4_side3 == 'X':
                continue

            # check border compatibility
            if piece4_side4 == 'X':
                if piece1_side4 != 'X':
                    continue
            else:
                if piece1_side4 == 'X':
                    continue

            for piece5, rot5 in self._iter_piece_with_side4_side1(piece4_side2, piece2_side3,
                                                                  (piece1.nr, piece2.nr, piece3.nr,
                                                                   piece4.nr)):
                if piece5.nr in CORNER_HINT_NRS:
                    continue

                piece5_side2 = piece5.get_side(2, rot5)
                piece5_side3 = piece5.get_side(3, rot5)

                # max 1 hint in a 3x3
                piece5_is_hint = piece5.nr in ALL_HINT_NRS
                if piece5_is_hint:
                    if has_hints or piece4_is_hint:
                        continue
                    if piece1_is_corner or piece3_is_corner:
                        continue

                # avoid border on the inside
                if piece5_side2 == 'X' or piece5_side3 == 'X':
                    continue

                for piece6, rot6 in self._iter_piece_with_side4_side1(piece5_side2, piece3_side3,
                                                                      (piece1.nr, piece2.nr, piece3.nr,
                                                                       piece4.nr, piece5.nr)):
                    if piece6.nr in CORNER_HINT_NRS:
                        continue

                    piece6_side2 = piece6.get_side(2, rot6)
                    piece6_side3 = piece6.get_side(3, rot6)

                    # max 1 hint in a 3x3
                    piece6_is_hint = piece6.nr in ALL_HINT_NRS
                    if piece6_is_hint:
                        if has_hints or piece4_is_hint or piece5_is_hint:
                            continue
                        if piece1_is_corner or piece3_is_corner:
                            continue

                    # avoid border on the inside
                    if piece6_side3 == 'X':
                        continue

                    # check border compatibility
                    if piece6_side2 == 'X':
                        if piece3_side2 != 'X':
                            continue
                    else:
                        if piece3_side2 == 'X':
                            continue

                    yield piece4, rot4, piece5, rot5, piece6, rot6

                # for
            # for
        # for

    def _iter_row3(self, row1, row2):
        """
                      side 1
                   +---+---+---+
                   | 1 | 2 | 3 |
                   +---+---+---+
            side 4 | 4 | 5 | 6 | side 2
                   +---+---+---+
                   | 7 | 8 | 9 |
                   +---+---+---+
                       side 3
        """
        piece1, rot1, piece2, rot2, piece3, rot3 = row1
        piece4, rot4, piece5, rot5, piece6, rot6 = row2
        has_hints = (piece1.nr in ALL_HINT_NRS or piece2.nr in ALL_HINT_NRS or piece3.nr in ALL_HINT_NRS or
                     piece4.nr in ALL_HINT_NRS or piece5.nr in ALL_HINT_NRS or piece6.nr in ALL_HINT_NRS)

        piece1_side1 = piece1.get_side(1, rot1)
        piece4_side4 = piece4.get_side(4, rot4)
        piece6_side2 = piece6.get_side(2, rot6)

        piece4_side3 = piece4.get_side(3, rot4)
        piece5_side3 = piece5.get_side(3, rot5)
        piece6_side3 = piece6.get_side(3, rot6)

        for piece7, rot7 in self._iter_piece_with_side1(piece4_side3,
                                                        (piece1.nr, piece2.nr, piece3.nr,
                                                         piece4.nr, piece5.nr, piece6.nr)):
            piece7_side2 = piece7.get_side(2, rot7)
            piece7_side3 = piece7.get_side(3, rot7)
            piece7_side4 = piece7.get_side(4, rot7)

            # max 1 hint in a 3x3
            piece7_is_hint = piece7.nr in ALL_HINT_NRS
            if piece7_is_hint:
                if has_hints:
                    continue

            # avoid border on the inside
            if piece7_side2 == 'X':
                continue

            # check border compatibility
            if piece7_side4 == 'X':
                if piece4_side4 != 'X':
                    continue
            else:
                if piece4_side4 == 'X':
                    continue

            if piece7_side3 == 'X':
                if piece1_side1 == 'X':
                    continue

            for piece8, rot8 in self._iter_piece_with_side4_side1(piece7_side2, piece5_side3,
                                                                  (piece1.nr, piece2.nr, piece3.nr,
                                                                   piece4.nr, piece5.nr, piece6.nr,
                                                                   piece7.nr)):
                if piece8.nr in CORNER_HINT_NRS:
                    continue

                piece8_side2 = piece8.get_side(2, rot8)
                piece8_side3 = piece8.get_side(3, rot8)

                # max 1 hint in a 3x3
                piece8_is_hint = piece5.nr in ALL_HINT_NRS
                if piece8_is_hint:
                    if has_hints or piece7_is_hint:
                        continue

                # avoid border on the inside
                if piece8_side2 == 'X':
                    continue

                # check border compatibility
                if piece8_side3 == 'X':
                    if piece7_side3 != 'X':
                        continue

                    # avoid border on both sides
                    if piece1_side1 == 'X':
                        continue
                else:
                    if piece7_side3 == 'X':
                        continue

                for piece9, rot9 in self._iter_piece_with_side4_side1(piece8_side2, piece6_side3,
                                                                      (piece1.nr, piece2.nr, piece3.nr,
                                                                       piece4.nr, piece5.nr, piece6.nr,
                                                                       piece7.nr, piece8.nr)):
                    piece9_side2 = piece9.get_side(2, rot9)
                    piece9_side3 = piece9.get_side(3, rot9)

                    # max 1 hint in a 3x3
                    piece9_is_hint = piece9.nr in ALL_HINT_NRS
                    if piece9_is_hint:
                        if has_hints or piece7_is_hint or piece8_is_hint:
                            continue

                    # avoid border on both sides
                    # check border compatibility
                    if piece9_side2 == 'X':
                        if piece6_side2 != 'X':
                            continue

                        # avoid border on both sides
                        if piece7_side4 == 'X':
                            continue
                    else:
                        if piece6_side2 == 'X':
                            continue

                    if piece9_side3 == 'X':
                        if piece8_side3 != 'X':
                            continue
                    else:
                        if piece8_side3 == 'X':
                            continue

                    yield piece7, rot7, piece8, rot8, piece9, rot9

                # for
            # for
        # for

    def handle(self, *args, **options):

        self.stdout.write('[INFO] Filling caches')
        self._make_cache_base_with_side()

        self.stdout.write('[INFO] Deleting old pieces')
        Piece3x3.objects.all().delete()
        ThreeSide.objects.all().delete()

        self.stdout.write('[INFO] Generating all 3x3 including rotation variants')

        """ a 3x3 piece consists of 9 base pieces, each under a certain rotation

            each side consists of 3 base piece sides and is given a new simple numeric reference

                      side 1
                   +---+---+---+
                   | 1 | 2 | 3 |
                   +---+---+---+
            side 4 | 4 | 5 | 6 | side 2
                   +---+---+---+
                   | 7 | 8 | 9 |
                   +---+---+---+
                       side 3
        """

        nr = 0
        print_nr = print_interval = 100000

        bulk = list()
        for row1 in self._iter_row1():
            for row2 in self._iter_row2(row1):
                for row3 in self._iter_row3(row1, row2):

                    piece1, rot1, piece2, rot2, piece3, rot3 = row1
                    piece4, rot4, piece5, rot5, piece6, rot6 = row2
                    piece7, rot7, piece8, rot8, piece9, rot9 = row3

                    piece1_side1 = piece1.get_side(1, rot1)
                    piece2_side1 = piece2.get_side(1, rot2)
                    piece3_side1 = piece3.get_side(1, rot3)

                    piece3_side2 = piece3.get_side(2, rot3)
                    piece6_side2 = piece6.get_side(2, rot6)
                    piece9_side2 = piece9.get_side(2, rot9)

                    piece7_side3 = piece7.get_side(3, rot7)
                    piece8_side3 = piece8.get_side(3, rot8)
                    piece9_side3 = piece9.get_side(3, rot9)

                    piece1_side4 = piece1.get_side(4, rot1)
                    piece4_side4 = piece4.get_side(4, rot4)
                    piece7_side4 = piece7.get_side(4, rot7)

                    has_hint = (piece1.nr in ALL_HINT_NRS or piece2.nr in ALL_HINT_NRS or piece3.nr in ALL_HINT_NRS or
                                piece4.nr in ALL_HINT_NRS or piece5.nr in ALL_HINT_NRS or piece6.nr in ALL_HINT_NRS or
                                piece7.nr in ALL_HINT_NRS or piece8.nr in ALL_HINT_NRS or piece9.nr in ALL_HINT_NRS)

                    nr += 1
                    piece = Piece3x3(
                                    nr=nr,
                                    is_border=(piece1_side4 == 'X' or piece1_side1 == 'X' or
                                               piece9_side2 == 'X' or piece9_side3 == 'X'),
                                    has_hint=has_hint,
                                    side1=self._get_three_sides_nr(piece1_side1, piece2_side1, piece3_side1),
                                    side2=self._get_three_sides_nr(piece3_side2, piece6_side2, piece9_side2),
                                    side3=self._get_three_sides_nr(piece9_side3, piece8_side3, piece7_side3),
                                    side4=self._get_three_sides_nr(piece7_side4, piece4_side4, piece1_side4),
                                    nr1=piece1.nr,
                                    nr2=piece2.nr,
                                    nr3=piece3.nr,
                                    nr4=piece4.nr,
                                    nr5=piece5.nr,
                                    nr6=piece6.nr,
                                    nr7=piece7.nr,
                                    nr8=piece8.nr,
                                    nr9=piece9.nr,
                                    rot1=rot1,
                                    rot2=rot2,
                                    rot3=rot3,
                                    rot4=rot4,
                                    rot5=rot5,
                                    rot6=rot6,
                                    rot7=rot7,
                                    rot8=rot8,
                                    rot9=rot9)
                    bulk.append(piece)

                    if len(bulk) >= 10000:
                        Piece3x3.objects.bulk_create(bulk)
                        bulk = list()

                    if nr > print_nr:
                        print_nr += print_interval
                        print(self.three_sides_nr, nr, piece1)
                # for
            # for
        # for

        if len(bulk):
            Piece3x3.objects.bulk_create(bulk)

        self.stdout.write('[INFO] Generated %s Piece3x3 (includes rotation variants)' % nr)

# end of file
