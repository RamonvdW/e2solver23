# -*- coding: utf-8 -*-

#  Copyright (c) 2024 Ramon van der Winkel.
#  All rights reserved.
#  Licensed under BSD-3-Clause-Clear. See LICENSE file for details.

from django.core.management.base import BaseCommand
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
        self.select_corners = (1, 2, 3, 4)
        self.select_hints = (208, 255, 249, 181)
        self.select_borders = list(range(5, 60+1))
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

    def _fill_unused(self, seed):
        self.stdout.write('[INFO] Seed: %s' % seed)

        r = random.Random(seed)
        upper = len(self.select_rest)
        for lp in range(100000):
            idx = int(r.uniform(0, upper))
            nr = self.select_rest.pop(idx)
            self.select_rest.append(nr)
        # for

        uniq_nrs = frozenset(self.uniq_nrs[1] + self.uniq_nrs[2] + self.uniq_nrs[3] + self.uniq_nrs[4])

        self.unused = list()
        self.unused.extend(self.uniq_nrs[self.corner])
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

        # reminder: all corners and all borders
        self.unused.extend(self.select_corners)
        self.unused.extend(self.select_borders)

    def add_arguments(self, parser):
        parser.add_argument('seed', type=int, help='Randomization seed')

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
        exp_s1 = self.twoside_border
        qset = (Piece2x2
                .objects
                .filter(is_border=True,
                        side1=exp_s1, side4=self.loc2_exp_s4, side3=self.loc2_exp_s3,
                        nr1__in=self.unused, nr2__in=self.unused, nr3__in=self.unused, nr4__in=self.unused)
                .exclude(side2=self.twoside_border))
        # print('2 count: %s' % qset.count())
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

            self.unused.remove(p2x2.nr1)
            self.unused.remove(p2x2.nr2)
            self.unused.remove(p2x2.nr3)
            self.unused.remove(p2x2.nr4)

            self._find_nr1(c1)

            self.unused.extend([p2x2.nr1, p2x2.nr2, p2x2.nr3, p2x2.nr4])
        # for

    def _find_nr10(self, c1):
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
        # self.stdout.write('[INFO] Selected base pieces: %s' % repr(self.unused))

        Corner1.objects.all().delete()

        c1 = Corner1()
        try:
            self._find_nr10(c1)
        except KeyboardInterrupt:
            pass
        else:
            if len(self.bulk):
                Corner1.objects.bulk_create(self.bulk)
                self.bulk = list()

            self.stdout.write('[INFO] Created %s Corner1' % self.count)

            count1 = Corner1.objects.distinct('side3').count()
            count2 = Corner1.objects.distinct('side2').count()
            self.stdout.write('[INFO] Distinct sides: %s, %s' % (count1, count2))

# end of file
