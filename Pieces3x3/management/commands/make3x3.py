# -*- coding: utf-8 -*-

#  Copyright (c) 2023 Ramon van der Winkel.
#  All rights reserved.
#  Licensed under BSD-3-Clause-Clear. See LICENSE file for details.

from django.core.management.base import BaseCommand
from django.db import transaction
from BasePieces.models import BasePiece
from Pieces3x3.models import ThreeSide, Piece3x3, Make3x3Next
import sys

ALL_HINT_NRS = (139, 181, 208, 249, 255)
CENTER_HINT_NR = 139
CORNER_HINT_NRS = (181, 208, 249, 255)


class Command(BaseCommand):

    help = "Generate all 3x3 pieces, with rotation variants"

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

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.three_sides = dict()       # ['XXX'] = nr

        self.base_with_side1 = dict()   # [side] = [(piece, rot), ..]
        self.base_with_side2 = dict()   # [side] = [(piece, rot), ..]
        self.base_with_side3 = dict()   # [side] = [(piece, rot), ..]
        self.base_with_side4 = dict()   # [side] = [(piece, rot), ..]

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

    def _load_three_sides(self):
        for obj in ThreeSide.objects.all():
            self.three_sides[obj.three_sides] = obj.nr
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

    @staticmethod
    def _iter_piece1(p1_nr):
        """ this generator is used for position 1 """
        piece = BasePiece.objects.get(nr=p1_nr)
        if p1_nr == 208:
            # hint 208 is found on p1 in a specific rotation only
            yield piece, 1
        else:
            # all 4 rotations
            yield piece, 0
            yield piece, 1
            yield piece, 2
            yield piece, 3

        # # only hint 208 is found on position 1, so exclude the rest
        # exclude_nrs = self.exclude_piece_nrs[:]
        # exclude_nrs.extend([139, 181, 249, 255])
        # for piece in BasePiece.objects.exclude(nr__in=self.exclude_piece_nrs):
        #     # some pieces are known to require a specific rotation
        #     if piece.nr == 208:
        #         yield piece, 1
        #     else:
        #         # all 4 rotations
        #         yield piece, 0
        #         yield piece, 1
        #         yield piece, 2
        #         yield piece, 3
        # # for

    def _iter_piece_with_side4(self, expected_side4, used_nrs):
        """ this generator is used for positions 2 and 3 """
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
            return self.three_sides[three_sides]
        except KeyError:
            pass

        self.stderr.write('[ERROR] Missing ThreeSide for %s' % repr(three_sides))
        sys.exit(1)

    def _iter_row1(self, p1_nr):
        """
                      side 1
                   +---+---+---+
            side 4 | 1 | 2 | 3 | side 2
                   +---+---+---+
                       side 3
        """
        for piece1, rot1 in self._iter_piece1(p1_nr):
            piece1_side2 = piece1.get_side(2, rot1)

            piece1_is_hint = piece1 in ALL_HINT_NRS

            for piece2, rot2 in self._iter_piece_with_side4(piece1_side2,
                                                            (piece1.nr,)):
                # no hints on p2
                if piece2.nr in ALL_HINT_NRS:
                    continue

                piece2_side2 = piece2.get_side(2, rot2)

                for piece3, rot3 in self._iter_piece_with_side4(piece2_side2,
                                                                (piece1.nr, piece2.nr)):

                    piece3_is_hint = piece3.nr in ALL_HINT_NRS

                    if piece3_is_hint:
                        # hints cannot be together in the same 3x3
                        if piece1_is_hint:
                            continue

                        # p3 can only be certain hints: 139, 255
                        if piece3.nr in (181, 208, 249):
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
            side 4 +---+---+---+ side 2
                   | 4 | 5 | 6 |
                   +---+---+---+
                       side 3
        """

        piece1, rot1, piece2, rot2, piece3, rot3 = row1
        piece1_side3 = piece1.get_side(3, rot1)
        piece2_side3 = piece2.get_side(3, rot2)
        piece3_side3 = piece3.get_side(3, rot3)

        for piece4, rot4 in self._iter_piece_with_side1(piece1_side3,
                                                        (piece1.nr, piece2.nr, piece3.nr)):
            # no hints on p4
            if piece4.nr in ALL_HINT_NRS:
                continue

            piece4_side2 = piece4.get_side(2, rot4)

            for piece5, rot5 in self._iter_piece_with_side4_side1(piece4_side2, piece2_side3,
                                                                  (piece1.nr, piece2.nr, piece3.nr,
                                                                   piece4.nr)):
                # no hints on p5
                if piece5.nr in ALL_HINT_NRS:
                    continue

                piece5_side2 = piece5.get_side(2, rot5)

                for piece6, rot6 in self._iter_piece_with_side4_side1(piece5_side2, piece3_side3,
                                                                      (piece1.nr, piece2.nr, piece3.nr,
                                                                       piece4.nr, piece5.nr)):
                    # no hints on p6
                    if piece6.nr in ALL_HINT_NRS:
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
        has_hints = (piece1.nr in ALL_HINT_NRS or piece2.nr in ALL_HINT_NRS or piece3.nr in ALL_HINT_NRS)

        piece4_side3 = piece4.get_side(3, rot4)
        piece5_side3 = piece5.get_side(3, rot5)
        piece6_side3 = piece6.get_side(3, rot6)

        for piece7, rot7 in self._iter_piece_with_side1(piece4_side3,
                                                        (piece1.nr, piece2.nr, piece3.nr,
                                                         piece4.nr, piece5.nr, piece6.nr)):
            # max 1 hint in a 3x3
            piece7_is_hint = piece7.nr in ALL_HINT_NRS
            if piece7_is_hint:
                # only hint 181 on p7
                if piece7.nr != 181:
                    continue
                # max 1 hint in a 3x3
                if has_hints:
                    continue

            piece7_side2 = piece7.get_side(2, rot7)

            for piece8, rot8 in self._iter_piece_with_side4_side1(piece7_side2, piece5_side3,
                                                                  (piece1.nr, piece2.nr, piece3.nr,
                                                                   piece4.nr, piece5.nr, piece6.nr,
                                                                   piece7.nr)):
                # no hint on p8
                if piece8.nr in ALL_HINT_NRS:
                    continue

                piece8_side2 = piece8.get_side(2, rot8)

                for piece9, rot9 in self._iter_piece_with_side4_side1(piece8_side2, piece6_side3,
                                                                      (piece1.nr, piece2.nr, piece3.nr,
                                                                       piece4.nr, piece5.nr, piece6.nr,
                                                                       piece7.nr, piece8.nr)):
                    piece9_is_hint = piece9.nr in ALL_HINT_NRS
                    if piece9_is_hint:
                        # only hint 249 on p9
                        if piece9.nr != 249:
                            continue
                        # max 1 hint in a 3x3
                        if has_hints or piece7_is_hint:
                            continue

                    yield piece7, rot7, piece8, rot8, piece9, rot9
                # for
            # for
        # for

    def handle(self, *args, **options):

        self._load_three_sides()

        self.stdout.write('[INFO] Filling caches')
        self._make_cache_base_with_side()

        # self.stdout.write('[INFO] Deleting old pieces')
        # last = Piece3x3.objects.order_by('pk').last()
        # if last:
        #     last_pk = last.pk
        #     pk = 1000000
        #     while pk < last_pk:
        #         Piece3x3.objects.filter(pk__lt=pk).delete()
        #         pk += 1000000
        #     # for

        with transaction.atomic():                  # avoid concurrent update
            obj = Make3x3Next.objects.select_for_update().first()
            p1_nr = obj.next_p1
            obj.next_p1 += 1
            obj.save()

        self.stdout.write('[INFO] {%s} Generating 3x3 with rotation variants' % p1_nr)

        nr = 0
        print_nr = print_interval = 100000

        bulk = list()
        for row1 in self._iter_row1(p1_nr):
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
                                    # automatic numbering
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
                        print('{%s} %s' % (p1_nr, nr))
                # for
            # for
        # for

        if len(bulk):
            Piece3x3.objects.bulk_create(bulk)

        self.stdout.write('[INFO] {%s} Generated %s Piece3x3 (includes rotation variants)' % (p1_nr, nr))

# end of file
