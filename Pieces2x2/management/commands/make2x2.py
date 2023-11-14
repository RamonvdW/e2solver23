# -*- coding: utf-8 -*-

#  Copyright (c) 2023 Ramon van der Winkel.
#  All rights reserved.
#  Licensed under BSD-3-Clause-Clear. See LICENSE file for details.

from django.core.management.base import BaseCommand
from BasePieces.models import BasePiece
from Pieces2x2.models import TwoSides, Piece2x2

DO_STORE = True


class Command(BaseCommand):

    help = "Generate all 2x2 pieces, with rotation variants"

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

    def _generate_base_with_side(self):
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

    def add_arguments(self, parser):
        parser.add_argument('--subset', required=True, choices=['corners', 'borders', 'center', 'center+hints'],
                            help="Which subset of Piece2x2 to generate")

    def _iter_piece1(self):
        for piece in BasePiece.objects.exclude(nr__in=self.exclude_piece_nrs):
            yield piece, 0
            yield piece, 1
            yield piece, 2
            yield piece, 3
        # for

    def _iter_piece2(self, expected_side4, nr1: int):
        # rotations are counter-clockwise
        # we want to match on side4
        for piece, rot in self.base_with_side4[expected_side4]:
            # if piece.nr != used_nr:
            if piece.nr > nr1:      # bigger-than avoids rotation variants
                yield piece, rot
        # for

    def _iter_piece3(self, expected_side1, nr1: int, nr2: int):
        # rotations are counter-clockwise
        # we want to match on side1
        for piece, rot in self.base_with_side1[expected_side1]:
            # if piece.nr not in (nr1, nr2):
            if piece.nr > nr1 and piece.nr != nr2:
                yield piece, rot
        # for

    def _iter_piece4(self, expected_side4, expected_side1, nr1: int, nr2: int, nr3: int):
        # rotations are counter-clockwise
        # we want to match on side4 and side1
        for piece, rot in self.base_with_side1[expected_side1]:
            # if piece.nr not in used_nrs:
            if piece.nr > nr1 and piece.nr not in (nr2, nr3):
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
            TwoSides(
                 nr=nr,
                 two_sides=two_sides).save()
            self.two_sides[two_sides] = nr
        return nr

    def handle(self, *args, **options):

        subset = options['subset']

        if subset == 'corners':
            self.allow_hint_piece_nrs = (208, 255, 181, 249)
            self.exclude_piece_nrs = (139,)
            self.with_interior = True
            self.with_corners = True
            self.with_center = False
            self.with_sides = True
        elif subset == 'borders':
            # hints have already been used in the corner
            self.allow_hint_piece_nrs = ()
            self.exclude_piece_nrs = (208, 255, 181, 249, 139)
            self.with_interior = False
            self.with_corners = False
            self.with_center = False
            self.with_sides = True
        elif subset == 'center':
            self.allow_hint_piece_nrs = (139,)
            self.exclude_piece_nrs = (208, 255, 181, 249)
            self.with_interior = True
            self.with_corners = False
            self.with_center = True
            self.with_sides = False
        else:   # subset == 'center+hints':
            self.allow_hint_piece_nrs = (139, 208, 255, 181, 249)
            self.exclude_piece_nrs = ()
            self.with_interior = True
            self.with_corners = False
            self.with_center = True
            self.with_sides = False

        hints = [str(nr) for nr in self.allow_hint_piece_nrs]
        if len(hints) > 0:
            hints_str = "with hint pieces %s" % ", ".join(hints)
        else:
            hints_str = "without any hint pieces"
        self.stdout.write('[INFO] Generating subset Piece2x2 for %s %s allowed' % (repr(subset), hints_str))

        self._generate_base_with_side()

        # delete all previously generate 2x2 pieces
        Piece2x2.objects.all().delete()
        TwoSides.objects.all().delete()

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

        bulk = list()
        nr = 0
        print_nr = print_interval = 10000
        for piece1, rot1 in self._iter_piece1():
            piece1_side1 = piece1.get_side(1, rot1)
            piece1_side2 = piece1.get_side(2, rot1)
            piece1_side3 = piece1.get_side(3, rot1)
            piece1_side4 = piece1.get_side(4, rot1)

            # prevent borders on the inside
            if piece1_side2 == 'X' or piece1_side3 == 'X':
                continue

            piece1_has_side = piece1_side4 == 'X' or piece1_side1 == 'X'
            piece1_is_corner = piece1_side4 == 'X' and piece1_side1 == 'X'

            keep = False
            if not piece1_has_side:
                if self.with_interior:
                    keep = True
            else:
                if self.with_corners:
                    keep = True

                if not piece1_is_corner:
                    if piece1_has_side and self.with_sides:
                        keep = True

            # print('piece1=%s, is_corner=%s, has_side=%s --> keep=%s' % (
            #       piece1.nr, piece1_is_corner, piece1_has_side, keep))

            if not keep:
                continue

            # check the hint positions
            piece1_is_hint = piece1.nr in self.allow_hint_piece_nrs
            if piece1_is_hint:
                # number 208 can be here under rotation 1
                if piece1.nr == 208 and rot1 != 1:
                    continue
                # number 255 can be here under rotation 2
                if piece1.nr == 255 and rot1 != 2:
                    continue
                # number 181 can be here under rotation 0
                if piece1.nr == 181 and rot1 != 0:
                    continue
                # number 249 can be here under rotation 2
                if piece1.nr == 249 and rot1 != 2:
                    continue
                # number 139 can be here under rotation 3
                if piece1.nr == 139 and rot1 != 3:
                    continue

            for piece2, rot2 in self._iter_piece2(piece1_side2, piece1.nr):
                piece2_side1 = piece2.get_side(1, rot2)
                piece2_side2 = piece2.get_side(2, rot2)
                piece2_side3 = piece2.get_side(3, rot2)

                # prevent 2x2 with border left and right
                if piece1_side4 == 'X' and piece2_side2 == 'X':
                    continue

                # prevent borders on the inside
                if piece2_side3 == 'X':
                    continue

                piece2_has_side = piece2_side1 == 'X'

                if not self.with_sides and piece2_has_side:
                    continue

                piece2_is_hint = piece2.nr in self.allow_hint_piece_nrs
                if piece2_is_hint:
                    if piece1_has_side:
                        continue
                    # hints cannot be together in the same 2x2
                    if piece1_is_hint:
                        continue
                    # number 208 can be here under rotation 0
                    if piece2.nr == 208 and rot2 != 0:
                        continue
                    # number 255 can be here under rotation 1
                    if piece2.nr == 255 and rot2 != 1:
                        continue
                    # number 181 can be here under rotation 3
                    if piece2.nr == 181 and rot2 != 3:
                        continue
                    # number 249 can be here under rotation 1
                    if piece2.nr == 249 and rot2 != 1:
                        continue
                    # number 139 can be here under rotation 2
                    if piece2.nr == 139 and rot2 != 2:
                        continue

                for piece3, rot3 in self._iter_piece3(piece1_side3, piece1.nr, piece2.nr):
                    piece3_side2 = piece3.get_side(2, rot3)
                    piece3_side3 = piece3.get_side(3, rot3)
                    piece3_side4 = piece3.get_side(4, rot3)

                    # prevent 2x2 with border of top and bottom
                    if piece1_side1 == 'X' and piece3_side3 == 'X':
                        continue

                    # prevent borders on the inside
                    if piece3_side2 == 'X' or piece3_side3 == 'X':
                        continue

                    piece3_has_side = piece3_side4 == 'X'

                    if not self.with_sides and piece3_has_side:
                        continue

                    piece3_is_hint = piece3.nr in self.allow_hint_piece_nrs
                    if piece3_is_hint:
                        if piece1_has_side or piece2_has_side:
                            continue
                        # hints cannot be together in the same 2x2
                        if piece1_is_hint or piece2_is_hint:
                            continue
                        # number 208 can be here under rotation 2
                        if piece3.nr == 208 and rot3 != 2:
                            continue
                        # number 255 can be here under rotation 3
                        if piece3.nr == 255 and rot3 != 3:
                            continue
                        # number 181 can be here under rotation 1
                        if piece3.nr == 181 and rot3 != 1:
                            continue
                        # number 249 can be here under rotation 3
                        if piece3.nr == 249 and rot3 != 3:
                            continue
                        # number 139 can be here under rotation 0
                        if piece3.nr == 139 and rot3 != 0:
                            continue

                    for piece4, rot4 in self._iter_piece4(piece3_side2, piece2_side3,
                                                          piece1.nr, piece2.nr, piece3.nr):

                        piece4_is_hint = piece4.nr in self.allow_hint_piece_nrs
                        if piece4_is_hint:
                            if piece1_has_side or piece2_has_side or piece3_has_side:
                                continue
                            # hints cannot be together in the same 2x2
                            if piece1_is_hint or piece2_is_hint or piece3_is_hint:
                                continue
                            # number 208 can be here under rotation 3
                            if piece4.nr == 208 and rot4 != 3:
                                continue
                            # number 255 can be here under rotation 0
                            if piece4.nr == 255 and rot4 != 0:
                                continue
                            # number 181 can be here under rotation 2
                            if piece4.nr == 181 and rot4 != 2:
                                continue
                            # number 249 can be here under rotation 0
                            if piece4.nr == 249 and rot4 != 0:
                                continue
                            # number 139 can be here under rotation 1
                            if piece4.nr == 139 and rot4 != 1:
                                continue

                        if self.with_corners:
                            if not (piece1_is_hint or piece2_is_hint or piece3_is_hint or piece4_is_hint or
                                    piece1_has_side or piece2_has_side or piece3_has_side):
                                continue

                        nr += 1
                        piece = Piece2x2(
                            nr=nr,
                            side1=self._get_two_sides_nr(piece1.get_side(1, rot1), piece2.get_side(1, rot2)),
                            side2=self._get_two_sides_nr(piece2.get_side(2, rot2), piece4.get_side(2, rot4)),
                            side3=self._get_two_sides_nr(piece4.get_side(3, rot4), piece3.get_side(3, rot3)),
                            side4=self._get_two_sides_nr(piece3.get_side(4, rot3), piece1.get_side(4, rot1)),
                            nr1=piece1.nr,
                            nr2=piece2.nr,
                            nr3=piece3.nr,
                            nr4=piece4.nr,
                            rot1=rot1,
                            rot2=rot2,
                            rot3=rot3,
                            rot4=rot4)
                        if DO_STORE:
                            bulk.append(piece)

                        if piece1_is_corner:
                            # store once
                            pass

                        elif piece2_has_side:
                            # also store rotated (counter-clockwise)
                            nr += 1
                            if DO_STORE:
                                piece_rot = Piece2x2(
                                    nr=nr,
                                    side1=piece.side2,
                                    side2=piece.side3,
                                    side3=piece.side4,
                                    side4=piece.side1,
                                    nr1=piece.nr2, rot1=(piece.rot2 + 1) % 4,
                                    nr2=piece.nr4, rot2=(piece.rot4 + 1) % 4,
                                    nr3=piece.nr1, rot3=(piece.rot1 + 1) % 4,
                                    nr4=piece.nr3, rot4=(piece.rot3 + 1) % 4)
                                bulk.append(piece_rot)
                        elif piece3_has_side:
                            # also store rotated (clockwise)
                            nr += 1
                            if DO_STORE:
                                piece_rot = Piece2x2(
                                    nr=nr,
                                    side1=piece.side4,
                                    side2=piece.side1,
                                    side3=piece.side2,
                                    side4=piece.side3,
                                    nr1=piece.nr3, rot1=(piece.rot3 + 3) % 4,
                                    nr2=piece.nr1, rot2=(piece.rot1 + 3) % 4,
                                    nr3=piece.nr4, rot3=(piece.rot4 + 3) % 4,
                                    nr4=piece.nr2, rot4=(piece.rot2 + 3) % 4)
                                bulk.append(piece_rot)

                        else:
                            # store under all four rotations
                            nr += 1
                            if DO_STORE:
                                piece_rot = Piece2x2(
                                    nr=nr,
                                    side1=piece.side2,
                                    side2=piece.side3,
                                    side3=piece.side4,
                                    side4=piece.side1,
                                    nr1=piece.nr2, rot1=(piece.rot2 + 1) % 4,
                                    nr2=piece.nr4, rot2=(piece.rot4 + 1) % 4,
                                    nr3=piece.nr1, rot3=(piece.rot1 + 1) % 4,
                                    nr4=piece.nr3, rot4=(piece.rot3 + 1) % 4)
                                bulk.append(piece_rot)

                            nr += 1
                            if DO_STORE:
                                piece_rot = Piece2x2(
                                    nr=nr,
                                    side1=piece.side3,
                                    side2=piece.side4,
                                    side3=piece.side1,
                                    side4=piece.side2,
                                    nr1=piece.nr4, rot1=(piece.rot4 + 2) % 4,
                                    nr2=piece.nr3, rot2=(piece.rot3 + 2) % 4,
                                    nr3=piece.nr2, rot3=(piece.rot2 + 2) % 4,
                                    nr4=piece.nr1, rot4=(piece.rot1 + 2) % 4)
                                bulk.append(piece_rot)

                            nr += 1
                            if DO_STORE:
                                piece_rot = Piece2x2(
                                    nr=nr,
                                    side1=piece.side4,
                                    side2=piece.side1,
                                    side3=piece.side2,
                                    side4=piece.side3,
                                    nr1=piece.nr3, rot1=(piece.rot3 + 3) % 4,
                                    nr2=piece.nr1, rot2=(piece.rot1 + 3) % 4,
                                    nr3=piece.nr4, rot3=(piece.rot4 + 3) % 4,
                                    nr4=piece.nr2, rot4=(piece.rot2 + 3) % 4)
                                bulk.append(piece_rot)

                        if len(bulk) >= 1000:
                            Piece2x2.objects.bulk_create(bulk)
                            bulk = list()

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
