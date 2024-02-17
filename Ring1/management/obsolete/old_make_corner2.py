# -*- coding: utf-8 -*-

#  Copyright (c) 2024 Ramon van der Winkel.
#  All rights reserved.
#  Licensed under BSD-3-Clause-Clear. See LICENSE file for details.

from django.core.management.base import BaseCommand
from BasePieces.border import GenerateBorder
from Pieces2x2.models import TwoSide, Piece2x2
from Ring1.models import Corner2
from copy import deepcopy
import random


class Command(BaseCommand):

    help = "Make all possible combinations of corner 2"

    """
        +----+----+----+----+
        | 5  | 6  | 7  | 8  |
        +----+----+----+----+
             | 14 | 15 | 16 |
             +----+----+----+
                  | 23 | 24 |
                  +----+----+
                       | 32 |
                       +----+
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.corner = 2
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

        # solve order: 15, 16, 8, 7, 6, 14, 24, 23, (22), 32, (31), 5, (13)
        self.loc7_exp_s3 = 0
        self.loc16_exp_s4 = 0
        self.loc23_exp_s1 = 0
        self.loc14_exp_s2 = 0
        self.loc8_exp_s3 = 0
        self.loc24_exp_s1 = 0
        self.loc7_exp_s2 = 0
        self.loc6_exp_s2 = 0
        self.loc5_exp_s2 = 0
        self.loc14_exp_s1 = 0
        self.loc22_exp_s1 = 0
        self.loc13_exp_s2 = 0
        self.loc23_exp_s2 = 0
        self.loc32_exp_s1 = 0
        self.loc31_exp_s1 = 0
        self.loc22_exp_s2 = 0
        self.loc31_exp_s2 = 0
        self.loc13_exp_s1 = 0

        self.count = 0
        self.count_print = 5000
        self.bulk = list()

    def add_arguments(self, parser):
        parser.add_argument('seed', type=int, help='Randomization seed')

    def _fill_unused(self, seed):
        self.stdout.write('[INFO] Seed: %s' % seed)
        self.unused = list()

        corner_claims = {1: [], 2: [], 3: [], 4: []}
        gen = GenerateBorder(seed)
        borders = gen.get_first_solution()
        for corner in (1, 2, 3, 4):
            sub = borders[(corner - 1) * 15:]
            bcb_nrs = sub[6:6+3]
            # print('bcb = %s' % repr(bcb_nrs))
            if corner == 1:
                d = list(Piece2x2.objects.filter(nr3=bcb_nrs[0], nr1=bcb_nrs[1], nr2=bcb_nrs[2])
                         .distinct('nr4').values_list('nr4', flat=True))
                # print('p2x2 count for c1.nr4: %s' % repr(d))
            elif corner == 2:
                d = list(Piece2x2.objects.filter(nr1=bcb_nrs[0], nr2=bcb_nrs[1], nr4=bcb_nrs[2])
                         .distinct('nr3').values_list('nr3', flat=True))
                # print('p2x2 count for c2.nr3: %s' % repr(d))
            elif corner == 3:
                d = list(Piece2x2.objects.filter(nr2=bcb_nrs[0], nr4=bcb_nrs[1], nr3=bcb_nrs[2])
                         .distinct('nr1').values_list('nr1', flat=True))
                # print('p2x2 count for c3.nr1: %s' % repr(d))
            else:
                d = list(Piece2x2.objects.filter(nr4=bcb_nrs[0], nr3=bcb_nrs[1], nr1=bcb_nrs[2])
                         .distinct('nr2').values_list('nr2', flat=True))
                # print('p2x2 count for c4.nr2: %s' % repr(d))
            corner_claims[corner].extend(d)
        # for

        borders = borders[(self.corner - 1) * 15:]
        self.unused.extend(borders[:15])
        del gen
        del borders

        # divide the corner claims for this seed
        done = False
        idx = 1
        while not done:
            done = True

            try:
                claim = corner_claims[idx].pop(0)
            except IndexError:
                # empty list
                pass
            else:
                # give this claim
                if idx == self.corner:
                    print('adding corner claim %s' % claim)
                    self.unused.append(claim)
                self.select_rest.remove(claim)

                # remove this claim from all other corner claims
                for corner in (1, 2, 3, 4):
                    try:
                        corner_claims[corner].remove(claim)
                    except ValueError:
                        pass
                # for
            idx += 1
            if idx > 4:
                idx = 1
        # while

        # select_rest are all non-border/corner pieces except the hints
        r = random.Random(seed)
        upper = len(self.select_rest)
        for lp in range(100000):
            idx = int(r.uniform(0, upper))
            nr = self.select_rest.pop(idx)
            self.select_rest.append(nr)
        # for

        uniq_nrs = frozenset(self.uniq_nrs[1] + self.uniq_nrs[2] + self.uniq_nrs[3] + self.uniq_nrs[4])

        for nr in self.uniq_nrs[self.corner]:
            if nr in self.select_rest:
                self.unused.append(nr)
        # for

        counts = {
            1: len(self.uniq_nrs[1]),
            2: len(self.uniq_nrs[2]),
            3: len(self.uniq_nrs[3]),
            4: len(self.uniq_nrs[4]),
        }

        idx = 1
        while len(self.select_rest):
            nr = self.select_rest.pop(0)
            if nr in uniq_nrs:
                continue

            # idx: 1, 2, 3, 4, (repeat)
            if idx == self.corner:
                self.unused.append(nr)

            counts[idx] += 1
            idx += 1
            if idx > 4:
                idx = 1

            # skip if full
            while counts[idx] >= 48:
                idx += 1
                if idx > 4:
                    idx = 1
            # while

        # while

    def _save(self, c2):
        self.count += 1
        self.bulk.append(deepcopy(c2))
        if len(self.bulk) >= 1000:
            if self.count >= self.count_print:
                print('count: %s --> 15=%s, 16=%s, 8=%s, 7=%s, 6=%s, 24=%s, 23=%s' % (
                    self.count, c2.loc15, c2.loc16, c2.loc8, c2.loc7, c2.loc6, c2.loc24, c2.loc23))
                self.count_print += 5000
            Corner2.objects.bulk_create(self.bulk)
            self.bulk = list()

    def _check(self, c2):

        used = [c2.nr1, c2.nr2, c2.nr3, c2.nr4, c2.nr5, c2.nr6, c2.nr7, c2.nr8, c2.nr9, c2.nr10, c2.nr11, c2.nr12,
                c2.nr13, c2.nr14, c2.nr15, c2.nr16, c2.nr17, c2.nr18, c2.nr19, c2.nr20, c2.nr21, c2.nr22, c2.nr23,
                c2.nr24, c2.nr25, c2.nr26, c2.nr27, c2.nr28, c2.nr29, c2.nr30, c2.nr31, c2.nr32, c2.nr33, c2.nr34,
                c2.nr35, c2.nr36, c2.nr37, c2.nr38, c2.nr39, c2.nr40]

        # check loc13
        chk13 = (Piece2x2
                 .objects
                 .filter(side1=self.loc13_exp_s1,
                         side2=self.loc13_exp_s2)
                 .exclude(nr1__in=used)
                 .exclude(nr2__in=used)
                 .exclude(nr3__in=used)
                 .exclude(nr4__in=used)
                 .first())
        if not chk13:
            return

        # check loc22
        chk22 = (Piece2x2
                 .objects
                 .filter(side1=self.loc22_exp_s1,
                         side2=self.loc22_exp_s2)
                 .exclude(nr1__in=used)
                 .exclude(nr2__in=used)
                 .exclude(nr3__in=used)
                 .exclude(nr4__in=used)
                 .first())
        if not chk22:
            return

        # check loc31
        chk31 = (Piece2x2
                 .objects
                 .filter(side1=self.loc31_exp_s1,
                         side2=self.loc31_exp_s2)
                 .exclude(nr1__in=used)
                 .exclude(nr2__in=used)
                 .exclude(nr3__in=used)
                 .exclude(nr4__in=used)
                 .first())
        if not chk31:
            return

        self._save(c2)

    def _find_nr5(self, c2):
        exp_s1 = self.twoside_border
        for p2x2 in (Piece2x2
                     .objects
                     .filter(is_border=True,
                             side1=exp_s1, side2=self.loc5_exp_s2,
                             nr1__in=self.unused, nr2__in=self.unused, nr3__in=self.unused, nr4__in=self.unused)
                     .exclude(side4=self.twoside_border)):
            c2.loc5 = p2x2.nr
            c2.side4 = p2x2.side4
            self.loc13_exp_s1 = self.twoside2reverse[p2x2.side3]

            c2.nr37 = p2x2.nr1
            c2.nr38 = p2x2.nr2
            c2.nr39 = p2x2.nr3
            c2.nr40 = p2x2.nr4

            self._check(c2)
        # for

    def _find_nr32(self, c2):
        exp_s2 = self.twoside_border
        for p2x2 in (Piece2x2
                     .objects
                     .filter(is_border=True,
                             side1=self.loc32_exp_s1, side2=exp_s2,
                             nr1__in=self.unused, nr2__in=self.unused, nr3__in=self.unused, nr4__in=self.unused)
                     .exclude(side3=self.twoside_border)):
            c2.loc32 = p2x2.nr
            c2.side3 = p2x2.side3
            self.loc31_exp_s2 = self.twoside2reverse[p2x2.side4]

            c2.nr33 = p2x2.nr1
            c2.nr34 = p2x2.nr2
            c2.nr35 = p2x2.nr3
            c2.nr36 = p2x2.nr4

            self.unused.remove(p2x2.nr1)
            self.unused.remove(p2x2.nr2)
            self.unused.remove(p2x2.nr3)
            self.unused.remove(p2x2.nr4)

            self._find_nr5(c2)

            self.unused.extend([p2x2.nr1, p2x2.nr2, p2x2.nr3, p2x2.nr4])
        # for

    def _find_nr23(self, c2):
        for p2x2 in (Piece2x2
                     .objects
                     .filter(is_border=False,
                             side1=self.loc23_exp_s1, side2=self.loc23_exp_s2,
                             nr1__in=self.unused, nr2__in=self.unused, nr3__in=self.unused, nr4__in=self.unused)):
            c2.loc23 = p2x2.nr

            self.loc22_exp_s2 = self.twoside2reverse[p2x2.side4]
            self.loc31_exp_s1 = self.twoside2reverse[p2x2.side3]

            c2.nr29 = p2x2.nr1
            c2.nr30 = p2x2.nr2
            c2.nr31 = p2x2.nr3
            c2.nr32 = p2x2.nr4

            self.unused.remove(p2x2.nr1)
            self.unused.remove(p2x2.nr2)
            self.unused.remove(p2x2.nr3)
            self.unused.remove(p2x2.nr4)

            # check loc22
            used = [c2.nr1, c2.nr2, c2.nr3, c2.nr4, c2.nr5, c2.nr6, c2.nr7, c2.nr8, c2.nr9, c2.nr10, c2.nr11, c2.nr12,
                    c2.nr13, c2.nr14, c2.nr15, c2.nr16, c2.nr17, c2.nr18, c2.nr19, c2.nr20, c2.nr21, c2.nr22, c2.nr23,
                    c2.nr24, c2.nr25, c2.nr26, c2.nr27, c2.nr28, c2.nr29, c2.nr30, c2.nr31, c2.nr32]
            chk22 = (Piece2x2
                     .objects
                     .filter(side1=self.loc22_exp_s1,
                             side2=self.loc22_exp_s2)
                     .exclude(nr1__in=used)
                     .exclude(nr2__in=used)
                     .exclude(nr3__in=used)
                     .exclude(nr4__in=used)
                     .first())
            if chk22:
                self._find_nr32(c2)

            self.unused.extend([p2x2.nr1, p2x2.nr2, p2x2.nr3, p2x2.nr4])
        # for

    def _find_nr24(self, c2):
        exp_s2 = self.twoside_border
        qset = (Piece2x2
                .objects
                .filter(is_border=True,
                        side1=self.loc24_exp_s1, side2=exp_s2,
                        nr1__in=self.unused, nr2__in=self.unused, nr3__in=self.unused, nr4__in=self.unused)
                .exclude(side3=self.twoside_border))
        # print('24 count: %s' % qset.count())
        for p2x2 in qset:
            c2.loc24 = p2x2.nr
            self.loc23_exp_s2 = self.twoside2reverse[p2x2.side4]
            self.loc32_exp_s1 = self.twoside2reverse[p2x2.side3]

            c2.nr25 = p2x2.nr1
            c2.nr26 = p2x2.nr2
            c2.nr27 = p2x2.nr3
            c2.nr28 = p2x2.nr4

            self.unused.remove(p2x2.nr1)
            self.unused.remove(p2x2.nr2)
            self.unused.remove(p2x2.nr3)
            self.unused.remove(p2x2.nr4)

            self._find_nr23(c2)

            self.unused.extend([p2x2.nr1, p2x2.nr2, p2x2.nr3, p2x2.nr4])
        # for

    def _find_nr14(self, c2):
        qset = (Piece2x2
                .objects
                .filter(is_border=False,
                        side1=self.loc14_exp_s1, side2=self.loc14_exp_s2,
                        nr1__in=self.unused, nr2__in=self.unused, nr3__in=self.unused, nr4__in=self.unused))
        # print('14 count: %s' % qset.count())
        for p2x2 in qset:
            c2.loc14 = p2x2.nr
            self.loc22_exp_s1 = self.twoside2reverse[p2x2.side3]
            self.loc13_exp_s2 = self.twoside2reverse[p2x2.side4]

            c2.nr21 = p2x2.nr1
            c2.nr22 = p2x2.nr2
            c2.nr23 = p2x2.nr3
            c2.nr24 = p2x2.nr4

            self.unused.remove(p2x2.nr1)
            self.unused.remove(p2x2.nr2)
            self.unused.remove(p2x2.nr3)
            self.unused.remove(p2x2.nr4)

            self._find_nr24(c2)

            self.unused.extend([p2x2.nr1, p2x2.nr2, p2x2.nr3, p2x2.nr4])
        # for

    def _find_nr6(self, c2):
        exp_s1 = self.twoside_border
        qset = (Piece2x2
                .objects
                .filter(is_border=True,
                        side1=exp_s1, side2=self.loc6_exp_s2,
                        nr1__in=self.unused, nr2__in=self.unused, nr3__in=self.unused, nr4__in=self.unused)
                .exclude(side4=self.twoside_border))
        # print('6 count: %s' % qset.count())
        for p2x2 in qset:
            c2.loc6 = p2x2.nr
            self.loc5_exp_s2 = self.twoside2reverse[p2x2.side4]
            self.loc14_exp_s1 = self.twoside2reverse[p2x2.side3]

            c2.nr17 = p2x2.nr1
            c2.nr18 = p2x2.nr2
            c2.nr19 = p2x2.nr3
            c2.nr20 = p2x2.nr4

            self.unused.remove(p2x2.nr1)
            self.unused.remove(p2x2.nr2)
            self.unused.remove(p2x2.nr3)
            self.unused.remove(p2x2.nr4)

            self._find_nr14(c2)

            self.unused.extend([p2x2.nr1, p2x2.nr2, p2x2.nr3, p2x2.nr4])
        # for

    def _find_nr7(self, c2):
        exp_s1 = self.twoside_border
        qset = (Piece2x2
                .objects
                .filter(is_border=True,
                        side1=exp_s1, side2=self.loc7_exp_s2, side3=self.loc7_exp_s3,
                        nr1__in=self.unused, nr2__in=self.unused, nr3__in=self.unused, nr4__in=self.unused)
                .exclude(side4=self.twoside_border))
        # print('7 count: %s' % qset.count())
        for p2x2 in qset:
            c2.loc7 = p2x2.nr
            self.loc6_exp_s2 = self.twoside2reverse[p2x2.side4]

            c2.nr13 = p2x2.nr1
            c2.nr14 = p2x2.nr2
            c2.nr15 = p2x2.nr3
            c2.nr16 = p2x2.nr4

            self.unused.remove(p2x2.nr1)
            self.unused.remove(p2x2.nr2)
            self.unused.remove(p2x2.nr3)
            self.unused.remove(p2x2.nr4)

            self._find_nr6(c2)

            self.unused.extend([p2x2.nr1, p2x2.nr2, p2x2.nr3, p2x2.nr4])
        # for

    def _find_nr8(self, c2):
        exp_s1 = exp_s2 = self.twoside_border
        qset = (Piece2x2
                .objects
                .filter(is_border=True,
                        side1=exp_s1, side2=exp_s2, side3=self.loc8_exp_s3,
                        nr1__in=self.unused, nr2__in=self.unused, nr3__in=self.unused, nr4__in=self.unused))
        # print('8 count: %s' % qset.count())
        for p2x2 in qset:
            c2.loc8 = p2x2.nr
            self.loc7_exp_s2 = self.twoside2reverse[p2x2.side4]

            c2.nr9 = p2x2.nr1
            c2.nr10 = p2x2.nr2
            c2.nr11 = p2x2.nr3
            c2.nr12 = p2x2.nr4

            self.unused.remove(p2x2.nr1)
            self.unused.remove(p2x2.nr2)
            self.unused.remove(p2x2.nr3)
            self.unused.remove(p2x2.nr4)

            self._find_nr7(c2)

            self.unused.extend([p2x2.nr1, p2x2.nr2, p2x2.nr3, p2x2.nr4])
        # for

    def _find_nr16(self, c2):
        exp_s2 = self.twoside_border
        qset = (Piece2x2
                .objects
                .filter(is_border=True,
                        side4=self.loc16_exp_s4, side2=exp_s2,
                        nr1__in=self.unused, nr2__in=self.unused, nr3__in=self.unused, nr4__in=self.unused)
                .exclude(side3=self.twoside_border)
                .exclude(side1=self.twoside_border))
        # print('16 count: %s' % qset.count())
        for p2x2 in qset:
            c2.loc16 = p2x2.nr
            self.loc8_exp_s3 = self.twoside2reverse[p2x2.side1]
            self.loc24_exp_s1 = self.twoside2reverse[p2x2.side3]

            c2.nr5 = p2x2.nr1
            c2.nr6 = p2x2.nr2
            c2.nr7 = p2x2.nr3
            c2.nr8 = p2x2.nr4

            self.unused.remove(p2x2.nr1)
            self.unused.remove(p2x2.nr2)
            self.unused.remove(p2x2.nr3)
            self.unused.remove(p2x2.nr4)

            self._find_nr8(c2)

            self.unused.extend([p2x2.nr1, p2x2.nr2, p2x2.nr3, p2x2.nr4])
        # for

    def _find_nr15(self, c2):
        qset = (Piece2x2
                .objects
                .filter(is_border=False,
                        has_hint=True,
                        nr2=255,
                        nr1__in=self.unused, nr3__in=self.unused, nr4__in=self.unused))
        # print('15 count: %s' % qset.count())
        for p2x2 in qset:
            c2.loc15 = p2x2.nr
            self.loc7_exp_s3 = self.twoside2reverse[p2x2.side1]
            self.loc16_exp_s4 = self.twoside2reverse[p2x2.side2]
            self.loc23_exp_s1 = self.twoside2reverse[p2x2.side3]
            self.loc14_exp_s2 = self.twoside2reverse[p2x2.side4]

            c2.nr1 = p2x2.nr1
            c2.nr2 = p2x2.nr2
            c2.nr3 = p2x2.nr3
            c2.nr4 = p2x2.nr4

            self.unused.remove(p2x2.nr1)
            # self.unused.remove(p2x2.nr2)
            self.unused.remove(p2x2.nr3)
            self.unused.remove(p2x2.nr4)

            self._find_nr16(c2)

            self.unused.extend([p2x2.nr1, p2x2.nr3, p2x2.nr4])
        # for

    def handle(self, *args, **options):

        seed = options['seed']
        self._fill_unused(seed)
        self.stdout.write('[INFO] Selected base pieces: %s' % repr(self.unused))

        Corner2.objects.filter(seed=seed).delete()

        c2 = Corner2(seed=seed)
        try:
            self._find_nr15(c2)
        except KeyboardInterrupt:
            pass
        else:
            if len(self.bulk):
                Corner2.objects.bulk_create(self.bulk)
                self.bulk = list()

            self.stdout.write('[INFO] Created %s Corner2' % self.count)

            count1 = Corner2.objects.filter(seed=seed).distinct('side4').count()
            count2 = Corner2.objects.filter(seed=seed).distinct('side3').count()
            self.stdout.write('[INFO] Distinct sides: %s, %s' % (count1, count2))

# end of file
