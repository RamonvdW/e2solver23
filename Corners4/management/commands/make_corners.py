# -*- coding: utf-8 -*-

#  Copyright (c) 2023 Ramon van der Winkel.
#  All rights reserved.
#  Licensed under BSD-3-Clause-Clear. See LICENSE file for details.

from django.core.management.base import BaseCommand
from BasePieces.models import BasePiece
from Borders4x2.models import Border4x2
from Corners4.models import Corner4
from Pieces2x2.models import TwoSides, Piece2x2
from Pieces4x4.models import Piece4x4


class Command(BaseCommand):

    help = "Generate all Corner4 with two Border4x4 + 2 central Piece2x2 without storing the corner Piece4x4"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # cache all base pieces
        self.base_pieces = dict()       # [nr] = BasePiece()
        for piece in BasePiece.objects.all():
            self.base_pieces[piece.nr] = piece
        # for

        # load all TwoSides
        self.two_sides2nr = dict()   # ['XX'] = nr
        self.nr2two_sides = dict()   # [nr] = 'XX'
        for two in TwoSides.objects.all():
            self.nr2two_sides[two.nr] = two.two_sides
            self.two_sides2nr[two.two_sides] = two.nr
        # for

        self.side_nr2reverse = dict()       # [side nr] = reverse side nr
        for two in TwoSides.objects.all():
            reverse = two.two_sides[1] + two.two_sides[0]
            try:
                self.side_nr2reverse[two.nr] = self.two_sides2nr[reverse]
            except KeyError:
                self.side_nr2reverse[two.nr] = 9999   # bestaat niet
        # for

        self.counter_rot = {
            0: 0,
            1: 3,
            2: 2,
            3: 1
        }

        self._cache_test_2x2 = dict()   # [(side2, side4)] = dict() [used_nrs] = True/False
        self._cache_test_4x4 = dict()   # [(side2, side3)] = dict() [used_nrs] = True/False

        self.nr = 0

    def _set_4x2_side3a_side3b(self, border4x2):
        # side3 = "8765"
        border4x2.side3a = self.two_sides2nr[border4x2.side3[1] + border4x2.side3[0]]  # 7+8
        border4x2.side3b = self.two_sides2nr[border4x2.side3[3] + border4x2.side3[2]]  # 5+6

    def _test_2x2_side4_1(self, used_nrs, exp_side4, exp_side1):
        tup = (exp_side4, exp_side1)
        try:
            cache = self._cache_test_2x2[tup]
        except KeyError:
            self._cache_test_2x2[tup] = cache = dict()

        try:
            result = cache[used_nrs]
        except KeyError:
            result = False
            for _ in (Piece2x2
                      .objects
                      .filter(side4=exp_side4,
                              side1=exp_side1)
                      .exclude(nr1__in=used_nrs)
                      .exclude(nr2__in=used_nrs)
                      .exclude(nr3__in=used_nrs)
                      .exclude(nr4__in=used_nrs)
                      .iterator(chunk_size=10)):
                # found a solution
                result = True
            # for
            cache[used_nrs] = result

        return result

    def _test_4x4_side2_3(self, used_nrs, exp_side2, exp_side3):
        tup = (exp_side2, exp_side3)
        try:
            cache = self._cache_test_4x4[tup]
        except KeyError:
            self._cache_test_4x4[tup] = cache = dict()

        try:
            result = cache[used_nrs]
        except KeyError:
            result = False
            for _ in (Piece4x4
                     .objects
                     .filter(side2=exp_side2,
                             side3=exp_side3)
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
                     .exclude(nr11__in=used_nrs)
                     .exclude(nr12__in=used_nrs)
                     .exclude(nr13__in=used_nrs)
                     .exclude(nr14__in=used_nrs)
                     .exclude(nr15__in=used_nrs)
                     .exclude(nr16__in=used_nrs)
                     .iterator(chunk_size=10)):
                # found a solution
                result = True
            # for
            cache[used_nrs] = result

        return result

    @staticmethod
    def _iter_2x2_side1(used_nrs, exp_side1):
        for p in (Piece2x2
                  .objects
                  .filter(side1=exp_side1)
                  .exclude(nr1__in=used_nrs)
                  .exclude(nr2__in=used_nrs)
                  .exclude(nr3__in=used_nrs)
                  .exclude(nr4__in=used_nrs)
                  .iterator(chunk_size=1000)):

            used_nrs2 = used_nrs + (p.nr1, p.nr2, p.nr3, p.nr4)
            yield p, used_nrs2
        # for

    @staticmethod
    def _iter_2x2_side4(used_nrs, exp_side4):
        for p in (Piece2x2
                  .objects
                  .filter(side4=exp_side4)
                  .exclude(nr1__in=used_nrs)
                  .exclude(nr2__in=used_nrs)
                  .exclude(nr3__in=used_nrs)
                  .exclude(nr4__in=used_nrs)
                  .iterator(chunk_size=1000)):

            used_nrs2 = used_nrs + (p.nr1, p.nr2, p.nr3, p.nr4)
            yield p, used_nrs2
        # for

    @staticmethod
    def _iter_2x2_side4_1(used_nrs, exp_side4, exp_side1):
        for p in (Piece2x2
                  .objects
                  .filter(side4=exp_side4,
                          side1=exp_side1)
                  .exclude(nr1__in=used_nrs)
                  .exclude(nr2__in=used_nrs)
                  .exclude(nr3__in=used_nrs)
                  .exclude(nr4__in=used_nrs)
                  .iterator(chunk_size=1000)):

            used_nrs2 = used_nrs + (p.nr1, p.nr2, p.nr3, p.nr4)
            yield p, used_nrs2
        # for

    def _iter_border(self, used_nrs):
        for b in (Border4x2
                  .objects
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

            # side3 = "8765"
            b.side3a = self.two_sides2nr[b.side3[1] + b.side3[0]]  # 7+8
            b.side3b = self.two_sides2nr[b.side3[3] + b.side3[2]]  # 5+6

            yield b, used_nrs2
        # for

    def _iter_border_side2(self, used_nrs, exp_side2):
        # assert isinstance(exp_side2, str)
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

            # side3 = "8765"
            b.side3a = self.two_sides2nr[b.side3[1] + b.side3[0]]  # 7+8
            b.side3b = self.two_sides2nr[b.side3[3] + b.side3[2]]  # 5+6

            yield b, used_nrs2
        # for

    def _iter_border_side4(self, used_nrs, exp_side4):
        # assert isinstance(exp_side4, str)
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

            # side3 = "8765"
            b.side3a = self.two_sides2nr[b.side3[1] + b.side3[0]]  # 7+8
            b.side3b = self.two_sides2nr[b.side3[3] + b.side3[2]]  # 5+6

            yield b, used_nrs2
        # for

    def handle(self, *args, **options):

        # delete the old solutions
        Corner4.objects.all().delete()

        """
              +--+--+--+--+--+--+--+--+
              |Piece4x4   | Border4x2 |
              +         s +     b2    + 
              |  q0     i |  3b    3a |
              +         d +--+--+--+--+
              |         e |     |     |
              +         2 +  p2 +  q3 +
              |   side3   |     |     |
              +--+--+--+--+--+--+--+--+
              |     |     |     |
              +   3a+  p1 +  q2 +   q = quality check
              |     |     |     |
              + b1  +--+--+--+--+
              |     |     |
              +   3b+  q1 +
              |     |     |
              +--+--+--+--+
        """

        used_nrs0 = (139,)
        bulk = list()
        for b1, used_nrs1 in self._iter_border(used_nrs0):
            print('b1: %s' % b1.nr)
            p1_exp_side4 = b1.side3a
            q1_exp_side4 = b1.side3b

            for b2, used_nrs2 in self._iter_border(used_nrs1):
                print('b2: %s' % b2.nr)
                q3_exp_side1 = b2.side3a
                p2_exp_side1 = b2.side3b

                for p1, used_nrs3 in self._iter_2x2_side4(used_nrs2, p1_exp_side4):
                    print('p1: %s' % p1.nr)
                    q1_exp_side1 = self.side_nr2reverse[p1.side3]
                    q2_exp_side4 = self.side_nr2reverse[p1.side2]

                    if not self._test_2x2_side4_1(used_nrs3, q1_exp_side4, q1_exp_side1):
                        continue

                    two_p1_side1 = self.nr2two_sides[p1.side1]
                    two_b1_side2 = b1.side2
                    q0_side3 = two_p1_side1[1] + two_p1_side1[0] + two_b1_side2[1] + two_b1_side2[0]

                    for p2, used_nrs4 in self._iter_2x2_side1(used_nrs3, p2_exp_side1):
                        print('p2: %s' % p2.nr)
                        q3_exp_side4 = self.side_nr2reverse[p2.side2]
                        q2_exp_side1 = self.side_nr2reverse[p1.side3]

                        if not self._test_2x2_side4_1(used_nrs4, q2_exp_side4, q2_exp_side1):
                            print('no q2')
                            continue

                        if not self._test_2x2_side4_1(used_nrs4, q3_exp_side4, q3_exp_side1):
                            print('no q3')
                            continue

                        two_p2_side4 = self.nr2two_sides[p2.side4]
                        two_b2_side4 = b2.side4
                        q0_side2 = two_b2_side4[1] + two_b2_side4[0] + two_p2_side4[1] + two_p2_side4[0]

                        if not self._test_4x4_side2_3(used_nrs4, q0_side2, q0_side3):
                            print('no q0')
                            continue

                        self.nr += 1
                        corner = Corner4(
                                    nr=self.nr,
                                    c=0,            # not used
                                    b1=b1.nr,
                                    b2=b2.nr,
                                    p1=p1.nr,
                                    p2=p2.nr)
                        bulk.append(corner)

                        if len(bulk) >= 1000:
                            Corner4.objects.bulk_create(bulk)
                            print('[INFO] Solutions: %s' % self.nr)
                            bulk = list()
                    # for
                # for
            # for
        # for

        if len(bulk):
            Corner4.objects.bulk_create(bulk)
            bulk = list()

        self.stdout.write('[INFO] Found %s Corner4 solutions' % self.nr)

# end of file
