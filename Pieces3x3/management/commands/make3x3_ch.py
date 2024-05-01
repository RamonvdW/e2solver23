# -*- coding: utf-8 -*-

#  Copyright (c) 2024 Ramon van der Winkel.
#  All rights reserved.
#  Licensed under BSD-3-Clause-Clear. See LICENSE file for details.

from django.core.management.base import BaseCommand
from BasePieces.models import BasePiece
from Pieces2x2.models import TwoSide, Piece2x2


class Command(BaseCommand):

    help = "Generate all 3x3 pieces with a Corner and a Hint"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.two_sides = dict()  # ['XX'] = nr
        self.two_sides_nr = 0

        self.base_with_side1 = dict()   # [side] = [(piece, rot), ..]
        self.base_with_side2 = dict()   # [side] = [(piece, rot), ..]
        self.base_with_side3 = dict()   # [side] = [(piece, rot), ..]
        self.base_with_side4 = dict()   # [side] = [(piece, rot), ..]

        self.with_interior = False
        self.with_corners = False
        self.with_center = False
        self.with_sides = False

        self.exclude_piece_nrs = ()
        self.allow_hint_piece_nrs = (208, 255, 181, 249, 139)

    def _make_cache_base_with_side(self):
        all_sides = []
        for piece in BasePiece.objects.exclude(nr__in=self.exclude_piece_nrs):
            side = piece.side4          # the only side where all possibilities are found
            if side not in all_sides:
                all_sides.append(side)
                self.base_with_side1[side] = []
                self.base_with_side2[side] = []
                self.base_with_side3[side] = []
                self.base_with_side4[side] = []
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

    def _iter_piece1(self):
        for piece in BasePiece.objects.exclude(nr__in=self.exclude_piece_nrs):
            yield piece, 0
            yield piece, 1
            yield piece, 2
            yield piece, 3
        # for

    def _iter_piece2(self, expected_side4, used_nrs):
        # we want to match on side4
        for piece, rot in self.base_with_side4[expected_side4]:
            if piece.nr not in used_nrs:
                yield piece, rot
        # for

    def _iter_piece3(self, expected_side1, used_nrs):
        # we want to match on side1
        for piece, rot in self.base_with_side1[expected_side1]:
            if piece.nr not in used_nrs:
                yield piece, rot
        # for

    def _iter_piece4(self, expected_side4, expected_side1, used_nrs):
        # we want to match on side4 and side1
        for piece, rot in self.base_with_side1[expected_side1]:
            if piece.nr not in used_nrs:
                if piece.get_side(4, rot) == expected_side4:
                    yield piece, rot
        # for

    def _get_two_sides_nr(self, side1, side2):
        two_sides = side1 + side2
        try:
            nr = self.two_sides[two_sides]
        except KeyError:
            nr = self.two_sides_nr + 1
            self.two_sides_nr = nr
            TwoSide(
                 nr=nr,
                 two_sides=two_sides).save()
            self.two_sides[two_sides] = nr
        return nr

    def handle(self, *args, **options):

        self.stdout.write('[INFO] Filling caches')
        self._make_cache_base_with_side()

        self.stdout.write('[INFO] Deleting all Piece2x2 and TwoSide')
        Piece2x2.objects.all().delete()
        TwoSide.objects.all().delete()

        self.stdout.write('[INFO] Generating all 2x2 including rotation variants')

        """ a 2x2 piece consists of 4 base pieces, each under a certain rotation

            each side consists of 2 base piece sides and is given a new simple numeric

                     side 1
                   +---+---+
                   | 1 | 2 |
            side 4 +---+---+ side 2
                   | 3 | 4 |
                   +---+---+
                     side 3
        """

        all_hints = (139, 181, 208, 249, 255)

        nr = 0
        print_nr = print_interval = 100000

        bulk = []
        for piece1, rot1 in self._iter_piece1():
            piece1_side1 = piece1.get_side(1, rot1)
            piece1_side2 = piece1.get_side(2, rot1)
            piece1_side3 = piece1.get_side(3, rot1)
            piece1_side4 = piece1.get_side(4, rot1)

            # prevent borders on the inside
            if piece1_side2 == 'X' or piece1_side3 == 'X':
                continue

            # check the hint positions
            piece1_is_hint = piece1.nr in all_hints
            if piece1_is_hint:
                # number 208 can be here under rotation 1
                if piece1.nr == 208 and rot1 != 1:
                    continue
                # other hints are not needed on p1
                if piece1.nr in (139, 181, 249, 255):
                    continue

            for piece2, rot2 in self._iter_piece2(piece1_side2, (piece1.nr,)):
                piece2_side1 = piece2.get_side(1, rot2)
                piece2_side2 = piece2.get_side(2, rot2)
                piece2_side3 = piece2.get_side(3, rot2)

                # prevent borders on the inside
                if piece2_side3 == 'X':
                    continue

                # check border compatibility piece1 and piece2
                if piece1_side1 == 'X':
                    if piece2_side1 != 'X':
                        continue
                else:
                    if piece2_side1 == 'X':
                        continue

                # avoid impossible piece (borders on multiple sides)
                if piece1_side4 == 'X':
                    if piece2_side2 == 'X':
                        continue

                piece2_is_hint = piece2.nr in all_hints
                if piece2_is_hint:
                    # hints cannot be together in the same 2x2
                    if piece1_is_hint:
                        continue
                    # number 139 can be here under rotation 2
                    if piece2.nr == 139 and rot2 != 2:
                        continue
                    # number 255 can be here under rotation 1
                    if piece2.nr == 255 and rot2 != 1:
                        continue
                    # other hints are not needed on p2
                    if piece2.nr in (181, 208, 249):
                        continue

                for piece3, rot3 in self._iter_piece3(piece1_side3, (piece1.nr, piece2.nr)):
                    piece3_side2 = piece3.get_side(2, rot3)
                    piece3_side3 = piece3.get_side(3, rot3)
                    piece3_side4 = piece3.get_side(4, rot3)

                    # prevent borders on the inside
                    if piece3_side2 == 'X':
                        continue

                    # check border compatibility piece1 and piece2
                    if piece1_side4 == 'X':
                        if piece3_side4 != 'X':
                            continue
                    else:
                        if piece3_side4 == 'X':
                            continue

                    # prevent 2x2 with border of top and bottom
                    if piece1_side1 == 'X' and piece3_side3 == 'X':
                        continue

                    piece3_is_hint = piece3.nr in all_hints
                    if piece3_is_hint:
                        # hints cannot be together in the same 2x2
                        if piece1_is_hint or piece2_is_hint:
                            continue
                        # number 181 can be here under rotation 1
                        if piece3.nr == 181 and rot3 != 1:
                            continue
                        # other hints are not needed on p3
                        if piece3.nr in (139, 208, 249, 255):
                            continue

                    for piece4, rot4 in self._iter_piece4(piece3_side2, piece2_side3,
                                                          (piece1.nr, piece2.nr, piece3.nr)):
                        piece4_side2 = piece4.get_side(2, rot4)
                        piece4_side3 = piece4.get_side(3, rot4)

                        piece4_is_hint = piece4.nr in all_hints
                        if piece4_is_hint:
                            # hints cannot be together in the same 2x2
                            if piece1_is_hint or piece2_is_hint or piece3_is_hint:
                                continue
                            # number 249 can be here under rotation 0
                            if piece4.nr == 249 and rot4 != 0:
                                continue
                            # other hints are not needed on p4
                            if piece4.nr in (139, 181, 208, 255):
                                continue

                        # check border compatibility piece2 and piece4
                        if piece2_side2 == 'X':
                            if piece4_side2 != 'X':
                                continue
                        else:
                            if piece4_side2 == 'X':
                                continue

                        # check border compatibility piece3 and piece4
                        if piece3_side3 == 'X':
                            if piece4_side3 != 'X':
                                continue
                        else:
                            if piece4_side3 == 'X':
                                continue

                        is_border = (piece1_side4 == 'X' or piece1_side1 == 'X' or
                                     piece4_side2 == 'X' or piece4_side3 == 'X')

                        has_hint = piece1_is_hint or piece2_is_hint or piece3_is_hint or piece4_is_hint

                        if is_border and has_hint:
                            continue

                        nr += 1
                        piece = Piece2x2(
                                        nr=nr,
                                        is_border=is_border,
                                        has_hint=has_hint,
                                        side1=self._get_two_sides_nr(piece1.get_side(1, rot1),      # A = nr1
                                                                     piece2.get_side(1, rot2)),     # B = nr2
                                        side2=self._get_two_sides_nr(piece2.get_side(2, rot2),      # A = nr2
                                                                     piece4.get_side(2, rot4)),     # B = nr4
                                        side3=self._get_two_sides_nr(piece3.get_side(3, rot3),      # A = nr3
                                                                     piece4.get_side(3, rot4)),     # B = nr4
                                        side4=self._get_two_sides_nr(piece1.get_side(4, rot1),      # A = nr1
                                                                     piece3.get_side(4, rot3)),     # B = nr3
                                        nr1=piece1.nr,
                                        nr2=piece2.nr,
                                        nr3=piece3.nr,
                                        nr4=piece4.nr,
                                        rot1=rot1,
                                        rot2=rot2,
                                        rot3=rot3,
                                        rot4=rot4)
                        bulk.append(piece)

                        if len(bulk) >= 10000:
                            Piece2x2.objects.bulk_create(bulk)
                            bulk = []

                        if nr > print_nr:
                            print_nr += print_interval
                            print(self.two_sides_nr, nr, piece1)
                # for
            # for
        # for

        if len(bulk):
            Piece2x2.objects.bulk_create(bulk)

        self.stdout.write('[INFO] Generated %s Piece2x2 (includes rotation variants)' % nr)

# end of file
