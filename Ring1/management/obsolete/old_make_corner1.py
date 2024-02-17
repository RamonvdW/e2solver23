# -*- coding: utf-8 -*-

#  Copyright (c) 2024 Ramon van der Winkel.
#  All rights reserved.
#  Licensed under BSD-3-Clause-Clear. See LICENSE file for details.

from django.core.management.base import BaseCommand
from BasePieces.border import GenerateBorder
from Pieces2x2.models import TwoSide, Piece2x2
from Ring1.models import Corner1
from copy import deepcopy
import random


class Command(BaseCommand):

    help = "Make all possible combinations of corner 1"

    """
        +----+----+----+----+
        | 1  | 2  | 3  | 4  |
        +----+----+----+----+
        | 9  | 10 | 11 |
        +----+----+----+
        | 17 | 18 |
        +----+----+
        | 25 |
        +----+
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.corner = 1
        self.unused = list()

        self.twoside_border = TwoSide.objects.get(two_sides='XX').nr

        two2nr = dict()
        for two in TwoSide.objects.all():
            two2nr[two.two_sides] = two.nr
        # for
        self.twoside2reverse = dict()
        for two_sides, nr in two2nr.items():
            two_rev = two_sides[1] + two_sides[0]
            rev_nr = two2nr[two_rev]
            self.twoside2reverse[nr] = rev_nr
        # for

        self.select_central = 136
        # self.select_corners = (1, 2, 3, 4)
        self.select_hints = (208, 255, 249, 181)
        # self.select_borders = list(range(5, 60+1))
        self.select_rest = list(range(61, 256+1))
        self.select_rest.remove(self.select_central)
        for hint in self.select_hints:
            self.select_rest.remove(hint)
        # for

        # 1=10, 2=15, 3=55, 4=50
        self.uniq_nrs = {
            1: (63, 67, 70, 72, 74, 75, 79, 96, 112, 118, 148, 152, 153, 186, 189, 191, 200, 209, 210, 217, 224, 226),
            2: (65, 69, 98, 100, 120, 206, 239, 247, 256),
            3: (82, 84, 86, 93, 94, 95, 101, 105, 110, 111, 132, 155, 156, 203, 204, 235, 236, 237, 242, 243, 248, 252),
            4: (61, 68, 107, 131, 141, 142, 144, 159, 169, 173, 179),
        }

        # solve order: 10, 9, 1, 2, 3, 11, 17, 18, (19), 25, (26), 4 (12)
        self.loc1_exp_s3 = 0
        self.loc2_exp_s4 = 0
        self.loc2_exp_s3 = 0
        self.loc3_exp_s4 = 0
        self.loc4_exp_s4 = 0
        self.loc9_exp_s2 = 0
        self.loc11_exp_s1 = 0
        self.loc11_exp_s4 = 0
        self.loc17_exp_s1 = 0
        self.loc18_exp_s1 = 0
        self.loc18_exp_s4 = 0
        self.loc25_exp_s1 = 0
        self.loc12_exp_s1 = 0
        self.loc12_exp_s4 = 0
        self.loc19_exp_s1 = 0
        self.loc19_exp_s4 = 0
        self.loc26_exp_s1 = 0
        self.loc26_exp_s4 = 0

        self.count = 0
        self.count_print = 5000
        self.bulk = list()

    def add_arguments(self, parser):
        parser.add_argument('seed', type=int, help='Randomization seed')

    def _fill_unused(self, seed):
        self.stdout.write('[INFO] Seed: %s' % seed)
        self.unused = list()

        # distribution of the 256 pieces over the 4 quadrants
        # initial numbers are due to the hints
        counts = {1: 1, 2: 1, 3: 1, 4: 2}

        # # give the specific unique numbers to this corner
        # for nr in self.uniq_nrs[self.corner]:
        #     if nr in self.select_rest:
        #         self.unused.append(nr)
        #         self.select_rest.remove(nr)
        # # for
        # for corner, uniq_nrs in self.uniq_nrs.items():
        #     counts[corner] += len(uniq_nrs)
        #     if corner != self.corner:
        #         for nr in uniq_nrs:
        #             self.select_rest.remove(nr)
        #     # for
        # # for

        print('A counts: %s (total %s)' % (repr(counts), sum(counts.values())))
        # print('A chosen: (%s) %s' % (len(self.unused), repr(self.unused)))
        # print('A select_rest: (%s) %s' % (len(self.select_rest), repr(self.select_rest)))

        # select_rest are all non-border/corner pieces except the hints
        r = random.Random(seed)
        upper = len(self.select_rest)
        for lp in range(100000):
            idx = int(r.uniform(0, upper))
            nr = self.select_rest.pop(idx)
            self.select_rest.append(nr)
        # for

        # generate a full-ring border of 1x1's
        gen = GenerateBorder(seed)
        borders = gen.get_first_solution()
        del gen

        # add the border pieces
        borders = borders[(self.corner - 1) * 15:]
        self.unused.extend(borders[:15])

        counts[1] += 15
        counts[2] += 15
        counts[3] += 15
        counts[4] += 15

        print('B counts: %s (total %s)' % (repr(counts), sum(counts.values())))
        # print('B chosen: (%s) %s' % (len(self.unused), repr(self.unused)))
        # print('B select_rest: (%s) %s' % (len(self.select_rest), repr(self.select_rest)))

        border_claims = {1: [], 2: [], 3: [], 4: []}
        for corner in (1, 2, 3, 4):
            sub = borders[(corner - 1) * 15:]
            sub = sub[:15]
            # print('sub=%s' % sub)

            # find the claims for the sides
            if corner == 1:
                side = 4
            else:
                side = corner - 1
            left = 3        # on this side before switching to next side
            while len(sub):
                bb = sub[:2]
                unused = self.select_rest

                if side == 4:
                    qset = Piece2x2.objects.filter(nr3=bb[0], nr1=bb[1], nr2__in=unused, nr4__in=unused)
                    d = [(p.nr2, p.nr4) for p in qset.distinct('nr2', 'nr4')]
                elif side == 1:
                    qset = Piece2x2.objects.filter(nr1=bb[0], nr2=bb[1], nr3__in=unused, nr4__in=unused)
                    d = [(p.nr3, p.nr4) for p in qset.distinct('nr3', 'nr4')]
                elif side == 2:
                    qset = Piece2x2.objects.filter(nr2=bb[0], nr4=bb[1], nr1__in=unused, nr3__in=unused)
                    d = [(p.nr1, p.nr3) for p in qset.distinct('nr1', 'nr3')]
                else:  # if side == 3:
                    qset = Piece2x2.objects.filter(nr4=bb[0], nr3=bb[1], nr1__in=unused, nr2__in=unused)
                    d = [(p.nr2, p.nr1) for p in qset.distinct('nr2', 'nr1')]

                # print('corner %s: bb=%s --> d=%s' % (corner, bb, len(d)))

                # grant 3 claims
                if len(d):
                    for nr1, nr2 in (d[0], d[-1]):
                        if nr1 not in border_claims[corner]:
                            border_claims[corner].append(nr1)
                            counts[corner] += 1
                        if nr2 not in border_claims[corner]:
                            border_claims[corner].append(nr2)
                            counts[corner] += 1

                        if nr1 in self.select_rest:
                            self.select_rest.remove(nr1)
                        if nr1 != nr2 and nr2 in self.select_rest:
                            self.select_rest.remove(nr2)
                    # for

                sub = sub[2:]
                if len(sub) == 9:
                    # chop off the corner with its 2 borders
                    sub = sub[3:]

                left -= 1
                if left == 0:
                    if side == 4:
                        side = 1
                    else:
                        side += 1
                    left = 6
            # while
        # for

        # print('total border claims: %s' % (len(border_claims[1]) + len(border_claims[2]) + len(border_claims[3]) + len(border_claims[4])))
        self.unused.extend(border_claims[self.corner])
        del border_claims

        print('C counts: %s (total %s)' % (repr(counts), sum(counts.values())))
        # print('C chosen: (%s) %s' % (len(self.unused), repr(self.unused)))
        # print('C select_rest: (%s) %s' % (len(self.select_rest), repr(self.select_rest)))

        corner_claims = {1: [], 2: [], 3: [], 4: []}
        for corner in (1, 2, 3, 4):
            sub = borders[(corner - 1) * 15:]
            sub = sub[:15]
            # print('sub=%s' % sub)

            # find the claim for the corner
            bcb_nrs = sub[6:6+3]
            unused = self.select_rest
            if corner == 1:
                d = list(Piece2x2.objects.filter(nr3=bcb_nrs[0], nr1=bcb_nrs[1], nr2=bcb_nrs[2], nr4__in=unused)
                         .distinct('nr4').values_list('nr4', flat=True))
                # print('p2x2 count for c1.nr4: %s' % repr(d))
            elif corner == 2:
                d = list(Piece2x2.objects.filter(nr1=bcb_nrs[0], nr2=bcb_nrs[1], nr4=bcb_nrs[2], nr3__in=unused)
                         .distinct('nr3').values_list('nr3', flat=True))
                # print('p2x2 count for c2.nr3: %s' % repr(d))
            elif corner == 3:
                d = list(Piece2x2.objects.filter(nr2=bcb_nrs[0], nr4=bcb_nrs[1], nr3=bcb_nrs[2], nr1__in=unused)
                         .distinct('nr1').values_list('nr1', flat=True))
                # print('p2x2 count for c3.nr1: %s' % repr(d))
            else:
                d = list(Piece2x2.objects.filter(nr4=bcb_nrs[0], nr3=bcb_nrs[1], nr1=bcb_nrs[2], nr2__in=unused)
                         .distinct('nr2').values_list('nr2', flat=True))
                # print('p2x2 count for c4.nr2: %s' % repr(d))

            # print('corner %s claims %s' % (corner, repr(d)))

            if len(d):
                claim = d[0]
                if corner == self.corner:
                    # print('adding corner claim %s' % claim)
                    self.unused.append(claim)

                # print('removing corner claim %s' % claim)
                self.select_rest.remove(claim)
                counts[corner] += 1
        # for

        del borders

        print('D counts: %s (total %s)' % (repr(counts), sum(counts.values())))
        print('D chosen: (%s) %s' % (len(self.unused), repr(self.unused)))
        print('D select_rest: (%s) %s' % (len(self.select_rest), repr(self.select_rest)))

        # distribute the remaining pieces
        idx = 1
        while len(self.select_rest):
            nr = self.select_rest.pop(0)

            # idx: 1, 2, 3, 4, (repeat)
            if idx == self.corner:
                self.unused.append(nr)

            counts[idx] += 1
            idx += 1
            if idx > 4:
                idx = 1

            # skip if full
            limit = 4
            while limit > 0 and counts[idx] == 64:
                limit -= 1
                idx += 1
                if idx > 4:
                    idx = 1
            # while

        # while

        print('E counts: %s (total %s)' % (repr(counts), sum(counts.values())))
        print('E chosen: (%s) %s' % (len(self.unused), repr(self.unused)))
        print('E select_rest: (%s) %s' % (len(self.select_rest), repr(self.select_rest)))

    def _save(self, c1):
        self.count += 1
        self.bulk.append(deepcopy(c1))
        if len(self.bulk) >= 1000:
            if self.count >= self.count_print:
                print('count: %s --> 10=%s, 9=%s, 1=%s, 2=%s, 3=%s, 17=%s, 18=%s' % (
                    self.count, c1.loc10, c1.loc9, c1.loc1, c1.loc2, c1.loc3, c1.loc17, c1.loc18))
                self.count_print += 5000
            Corner1.objects.bulk_create(self.bulk)
            self.bulk = list()

    def _check(self, c1):

        used = [c1.nr1, c1.nr2, c1.nr3, c1.nr4, c1.nr5, c1.nr6, c1.nr7, c1.nr8, c1.nr9, c1.nr10, c1.nr11, c1.nr12,
                c1.nr13, c1.nr14, c1.nr15, c1.nr16, c1.nr17, c1.nr18, c1.nr19, c1.nr20, c1.nr21, c1.nr22, c1.nr23,
                c1.nr24, c1.nr25, c1.nr26, c1.nr27, c1.nr28, c1.nr29, c1.nr30, c1.nr31, c1.nr32, c1.nr33, c1.nr34,
                c1.nr35, c1.nr36, c1.nr37, c1.nr38, c1.nr39, c1.nr40]

        # check loc12
        chk12 = (Piece2x2
                 .objects
                 .filter(side1=self.loc12_exp_s1,
                         side4=self.loc12_exp_s4)
                 .exclude(nr1__in=used)
                 .exclude(nr2__in=used)
                 .exclude(nr3__in=used)
                 .exclude(nr4__in=used)
                 .first())
        if not chk12:
            return

        # check loc19
        chk19 = (Piece2x2
                 .objects
                 .filter(side1=self.loc19_exp_s1,
                         side4=self.loc19_exp_s4)
                 .exclude(nr1__in=used)
                 .exclude(nr2__in=used)
                 .exclude(nr3__in=used)
                 .exclude(nr4__in=used)
                 .first())
        if not chk19:
            return

        # check loc26
        chk26 = (Piece2x2
                 .objects
                 .filter(side1=self.loc26_exp_s1,
                         side4=self.loc26_exp_s4)
                 .exclude(nr1__in=used)
                 .exclude(nr2__in=used)
                 .exclude(nr3__in=used)
                 .exclude(nr4__in=used)
                 .first())
        if not chk26:
            return

        self._save(c1)

    def _find_nr4(self, c1):
        exp_s1 = self.twoside_border
        for p2x2 in (Piece2x2
                     .objects
                     .filter(is_border=True,
                             side1=exp_s1, side4=self.loc4_exp_s4,
                             nr1__in=self.unused, nr2__in=self.unused, nr3__in=self.unused, nr4__in=self.unused)
                     .exclude(side2=self.twoside_border)):
            c1.loc4 = p2x2.nr
            c1.side2 = p2x2.side2

            self.loc12_exp_s1 = self.twoside2reverse[p2x2.side3]

            c1.nr37 = p2x2.nr1
            c1.nr38 = p2x2.nr2
            c1.nr39 = p2x2.nr3
            c1.nr40 = p2x2.nr4

            self._check(c1)
        # for

    def _find_nr25(self, c1):
        exp_s4 = self.twoside_border
        for p2x2 in (Piece2x2
                     .objects
                     .filter(is_border=True,
                             side1=self.loc25_exp_s1, side4=exp_s4,
                             nr1__in=self.unused, nr2__in=self.unused, nr3__in=self.unused, nr4__in=self.unused)
                     .exclude(side3=self.twoside_border)):
            c1.loc25 = p2x2.nr
            c1.side3 = p2x2.side3

            self.loc26_exp_s4 = self.twoside2reverse[p2x2.side2]

            c1.nr33 = p2x2.nr1
            c1.nr34 = p2x2.nr2
            c1.nr35 = p2x2.nr3
            c1.nr36 = p2x2.nr4

            self.unused.remove(p2x2.nr1)
            self.unused.remove(p2x2.nr2)
            self.unused.remove(p2x2.nr3)
            self.unused.remove(p2x2.nr4)

            self._find_nr4(c1)

            self.unused.extend([p2x2.nr1, p2x2.nr2, p2x2.nr3, p2x2.nr4])
        # for

    def _find_nr18(self, c1):
        for p2x2 in (Piece2x2
                     .objects
                     .filter(is_border=False,
                             side1=self.loc18_exp_s1, side4=self.loc18_exp_s4,
                             nr1__in=self.unused, nr2__in=self.unused, nr3__in=self.unused, nr4__in=self.unused)):
            c1.loc18 = p2x2.nr

            self.loc26_exp_s1 = self.twoside2reverse[p2x2.side3]
            self.loc19_exp_s4 = self.twoside2reverse[p2x2.side2]

            c1.nr29 = p2x2.nr1
            c1.nr30 = p2x2.nr2
            c1.nr31 = p2x2.nr3
            c1.nr32 = p2x2.nr4

            self.unused.remove(p2x2.nr1)
            self.unused.remove(p2x2.nr2)
            self.unused.remove(p2x2.nr3)
            self.unused.remove(p2x2.nr4)

            # check loc19
            used = [c1.nr1, c1.nr2, c1.nr3, c1.nr4, c1.nr5, c1.nr6, c1.nr7, c1.nr8, c1.nr9, c1.nr10, c1.nr11, c1.nr12,
                    c1.nr13, c1.nr14, c1.nr15, c1.nr16, c1.nr17, c1.nr18, c1.nr19, c1.nr20, c1.nr21, c1.nr22, c1.nr23,
                    c1.nr24, c1.nr25, c1.nr26, c1.nr27, c1.nr28, c1.nr29, c1.nr30, c1.nr31, c1.nr32]
            chk19 = (Piece2x2
                     .objects
                     .filter(side1=self.loc19_exp_s1,
                             side4=self.loc19_exp_s4)
                     .exclude(nr1__in=used)
                     .exclude(nr2__in=used)
                     .exclude(nr3__in=used)
                     .exclude(nr4__in=used)
                     .first())
            if chk19:
                self._find_nr25(c1)

            self.unused.extend([p2x2.nr1, p2x2.nr2, p2x2.nr3, p2x2.nr4])
        # for

    def _find_nr17(self, c1):
        exp_s4 = self.twoside_border
        qset = (Piece2x2
                .objects
                .filter(is_border=True,
                        side1=self.loc17_exp_s1, side4=exp_s4,
                        nr1__in=self.unused, nr2__in=self.unused, nr3__in=self.unused, nr4__in=self.unused)
                .exclude(side3=self.twoside_border))
        # print('17 count: %s' % qset.count())
        for p2x2 in qset:
            c1.loc17 = p2x2.nr
            self.loc18_exp_s4 = self.twoside2reverse[p2x2.side2]
            self.loc25_exp_s1 = self.twoside2reverse[p2x2.side3]

            c1.nr25 = p2x2.nr1
            c1.nr26 = p2x2.nr2
            c1.nr27 = p2x2.nr3
            c1.nr28 = p2x2.nr4

            self.unused.remove(p2x2.nr1)
            self.unused.remove(p2x2.nr2)
            self.unused.remove(p2x2.nr3)
            self.unused.remove(p2x2.nr4)

            self._find_nr18(c1)

            self.unused.extend([p2x2.nr1, p2x2.nr2, p2x2.nr3, p2x2.nr4])
        # for

    def _find_nr11(self, c1):
        qset = (Piece2x2
                .objects
                .filter(is_border=False,
                        side1=self.loc11_exp_s1, side4=self.loc11_exp_s4,
                        nr1__in=self.unused, nr2__in=self.unused, nr3__in=self.unused, nr4__in=self.unused))
        # print('11 count: %s' % qset.count())
        for p2x2 in qset:
            c1.loc11 = p2x2.nr

            self.loc12_exp_s4 = self.twoside2reverse[p2x2.side2]
            self.loc19_exp_s1 = self.twoside2reverse[p2x2.side3]

            c1.nr21 = p2x2.nr1
            c1.nr22 = p2x2.nr2
            c1.nr23 = p2x2.nr3
            c1.nr24 = p2x2.nr4

            self.unused.remove(p2x2.nr1)
            self.unused.remove(p2x2.nr2)
            self.unused.remove(p2x2.nr3)
            self.unused.remove(p2x2.nr4)

            self._find_nr17(c1)

            self.unused.extend([p2x2.nr1, p2x2.nr2, p2x2.nr3, p2x2.nr4])
        # for

    def _find_nr3(self, c1):
        exp_s1 = self.twoside_border
        qset = (Piece2x2
                .objects
                .filter(is_border=True,
                        side1=exp_s1, side4=self.loc3_exp_s4,
                        nr1__in=self.unused, nr2__in=self.unused, nr3__in=self.unused, nr4__in=self.unused)
                .exclude(side2=self.twoside_border))
        # print('3 count: %s' % qset.count())
        for p2x2 in qset:
            c1.loc3 = p2x2.nr
            self.loc4_exp_s4 = self.twoside2reverse[p2x2.side2]
            self.loc11_exp_s1 = self.twoside2reverse[p2x2.side3]

            c1.nr17 = p2x2.nr1
            c1.nr18 = p2x2.nr2
            c1.nr19 = p2x2.nr3
            c1.nr20 = p2x2.nr4

            self.unused.remove(p2x2.nr1)
            self.unused.remove(p2x2.nr2)
            self.unused.remove(p2x2.nr3)
            self.unused.remove(p2x2.nr4)

            self._find_nr11(c1)

            self.unused.extend([p2x2.nr1, p2x2.nr2, p2x2.nr3, p2x2.nr4])
        # for

    def _find_nr2(self, c1):
        self.unused.sort()
        print('loc2 unused: (%s) %s' % (len(self.unused), repr(self.unused)))
        exp_s1 = self.twoside_border
        qset = (Piece2x2
                .objects
                .filter(is_border=True,
                        side1=exp_s1, side4=self.loc2_exp_s4, side3=self.loc2_exp_s3,
                        nr1__in=self.unused, nr2__in=self.unused, nr3__in=self.unused, nr4__in=self.unused)
                .exclude(side2=self.twoside_border))
        print('2 count: %s' % qset.count())
        for p2x2 in qset:
            c1.loc2 = p2x2.nr
            self.loc3_exp_s4 = self.twoside2reverse[p2x2.side2]

            c1.nr13 = p2x2.nr1
            c1.nr14 = p2x2.nr2
            c1.nr15 = p2x2.nr3
            c1.nr16 = p2x2.nr4

            self.unused.remove(p2x2.nr1)
            self.unused.remove(p2x2.nr2)
            self.unused.remove(p2x2.nr3)
            self.unused.remove(p2x2.nr4)

            self._find_nr3(c1)

            self.unused.extend([p2x2.nr1, p2x2.nr2, p2x2.nr3, p2x2.nr4])
        # for

    def _find_nr1(self, c1):
        # self.unused.sort()
        # print('loc1 unused: (%s) %s' % (len(self.unused), repr(self.unused)))

        exp_s1 = exp_s4 = self.twoside_border
        qset = (Piece2x2
                .objects
                .filter(is_border=True,
                        side1=exp_s1, side4=exp_s4, side3=self.loc1_exp_s3,
                        nr1__in=self.unused, nr2__in=self.unused, nr3__in=self.unused, nr4__in=self.unused))
        # print('1 count: %s' % qset.count())
        for p2x2 in qset:
            c1.loc1 = p2x2.nr
            self.loc2_exp_s4 = self.twoside2reverse[p2x2.side2]

            c1.nr9 = p2x2.nr1
            c1.nr10 = p2x2.nr2
            c1.nr11 = p2x2.nr3
            c1.nr12 = p2x2.nr4

            self.unused.remove(p2x2.nr1)
            self.unused.remove(p2x2.nr2)
            self.unused.remove(p2x2.nr3)
            self.unused.remove(p2x2.nr4)

            self._find_nr2(c1)

            self.unused.extend([p2x2.nr1, p2x2.nr2, p2x2.nr3, p2x2.nr4])
        # for

    def _find_nr9(self, c1):
        # self.unused.sort()
        # print('loc9 unused: (%s) %s' % (len(self.unused), repr(self.unused)))
        exp_s4 = self.twoside_border
        qset = (Piece2x2
                .objects
                .filter(is_border=True,
                        side2=self.loc9_exp_s2, side4=exp_s4,
                        nr1__in=self.unused, nr2__in=self.unused, nr3__in=self.unused, nr4__in=self.unused)
                .exclude(side3=self.twoside_border)
                .exclude(side1=self.twoside_border))
        # print('9 count: %s' % qset.count())
        for p2x2 in qset:
            c1.loc9 = p2x2.nr
            self.loc1_exp_s3 = self.twoside2reverse[p2x2.side1]
            self.loc17_exp_s1 = self.twoside2reverse[p2x2.side3]

            c1.nr5 = p2x2.nr1
            c1.nr6 = p2x2.nr2
            c1.nr7 = p2x2.nr3
            c1.nr8 = p2x2.nr4

            # print('loc9: %s, %s, %s, %s' % (c1.nr5, c1.nr6, c1.nr7, c1.nr8))

            self.unused.remove(p2x2.nr1)
            self.unused.remove(p2x2.nr2)
            self.unused.remove(p2x2.nr3)
            self.unused.remove(p2x2.nr4)

            self._find_nr1(c1)

            self.unused.extend([p2x2.nr1, p2x2.nr2, p2x2.nr3, p2x2.nr4])
        # for

    def _find_nr10(self, c1):
        # self.unused.sort()
        # print('loc10 unused: (%s) %s' % (len(self.unused), repr(self.unused)))
        qset = (Piece2x2
                .objects
                .filter(is_border=False,
                        has_hint=True,
                        nr1=208,
                        nr2__in=self.unused, nr3__in=self.unused, nr4__in=self.unused))
        # print('10 count: %s' % qset.count())
        for p2x2 in qset:
            c1.loc10 = p2x2.nr
            self.loc2_exp_s3 = self.twoside2reverse[p2x2.side1]
            self.loc11_exp_s4 = self.twoside2reverse[p2x2.side2]
            self.loc18_exp_s1 = self.twoside2reverse[p2x2.side3]
            self.loc9_exp_s2 = self.twoside2reverse[p2x2.side4]

            c1.nr1 = p2x2.nr1
            c1.nr2 = p2x2.nr2
            c1.nr3 = p2x2.nr3
            c1.nr4 = p2x2.nr4

            # print('loc10: %s, %s, %s, %s' % (c1.nr1, c1.nr2, c1.nr3, c1.nr4))

            # self.unused.remove(p2x2.nr1)
            self.unused.remove(p2x2.nr2)
            self.unused.remove(p2x2.nr3)
            self.unused.remove(p2x2.nr4)

            self._find_nr9(c1)

            self.unused.extend([p2x2.nr2, p2x2.nr3, p2x2.nr4])
        # for

    def handle(self, *args, **options):

        seed = options['seed']
        self._fill_unused(seed)

        self.unused.sort()
        self.stdout.write('[INFO] Selected base pieces: (%s) %s' % (len(self.unused), repr(self.unused)))

        Corner1.objects.filter(seed=seed).delete()

        c1 = Corner1(seed=seed)
        try:
            self._find_nr10(c1)
        except KeyboardInterrupt:
            pass
        else:
            if len(self.bulk):
                Corner1.objects.bulk_create(self.bulk)
                self.bulk = list()

            self.stdout.write('[INFO] Created %s Corner1' % self.count)

            count1 = Corner1.objects.filter(seed=seed).distinct('side3').count()
            count2 = Corner1.objects.filter(seed=seed).distinct('side2').count()
            self.stdout.write('[INFO] Distinct sides: %s, %s' % (count1, count2))

# end of file
