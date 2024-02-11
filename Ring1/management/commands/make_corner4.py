# -*- coding: utf-8 -*-

#  Copyright (c) 2024 Ramon van der Winkel.
#  All rights reserved.
#  Licensed under BSD-3-Clause-Clear. See LICENSE file for details.

from django.core.management.base import BaseCommand
from Pieces2x2.models import TwoSide, Piece2x2
from Ring1.models import Corner4
from copy import deepcopy
import random


class Command(BaseCommand):

    help = "Make all possible combinations of corner 4"

    """
        +----+
        | 33 |
        +----+----+
        | 41 | 42 |
        +----+----+----+
        | 49 | 50 | 51 |
        +----+----+----+----+
        | 57 | 58 | 59 | 60 |
        +----+----+----+----+
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.corner = 4
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

        # solve order: 50, 49, 57, 58, 59, 51, 41, 42, (43), 33, (34), 60, (52)
        self.loc42_exp_s3 = 0
        self.loc51_exp_s4 = 0
        self.loc58_exp_s1 = 0
        self.loc49_exp_s2 = 0
        self.loc41_exp_s3 = 0
        self.loc57_exp_s1 = 0
        self.loc58_exp_s4 = 0
        self.loc59_exp_s4 = 0
        self.loc51_exp_s3 = 0
        self.loc60_exp_s4 = 0
        self.loc42_exp_s4 = 0
        self.loc43_exp_s3 = 0
        self.loc34_exp_s4 = 0
        self.loc34_exp_s3 = 0
        self.loc43_exp_s4 = 0
        self.loc43_exp_s3 = 0
        self.loc52_exp_s4 = 0
        self.loc52_exp_s3 = 0

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

    def _save(self, c4):
        self.count += 1
        self.bulk.append(deepcopy(c4))
        if len(self.bulk) >= 1000:
            if self.count >= self.count_print:
                print('count: %s --> 50=%s, 49=%s, 57=%s, 58=%s, 59=%s, 51=%s, 41=%s' % (
                    self.count, c4.loc50, c4.loc49, c4.loc57, c4.loc58, c4.loc59, c4.loc51, c4.loc41))
                self.count_print += 5000
            Corner4.objects.bulk_create(self.bulk)
            self.bulk = list()

    def _check(self, c4):

        used = [c4.nr1, c4.nr2, c4.nr3, c4.nr4, c4.nr5, c4.nr6, c4.nr7, c4.nr8, c4.nr9, c4.nr10, c4.nr11, c4.nr12,
                c4.nr13, c4.nr14, c4.nr15, c4.nr16, c4.nr17, c4.nr18, c4.nr19, c4.nr20, c4.nr21, c4.nr22, c4.nr23,
                c4.nr24, c4.nr25, c4.nr26, c4.nr27, c4.nr28, c4.nr29, c4.nr30, c4.nr31, c4.nr32, c4.nr33, c4.nr34,
                c4.nr35, c4.nr36, c4.nr37, c4.nr38, c4.nr39, c4.nr40]

        # check loc43
        chk43 = (Piece2x2
                 .objects
                 .filter(side3=self.loc43_exp_s3,
                         side4=self.loc43_exp_s4)
                 .exclude(nr1__in=used)
                 .exclude(nr2__in=used)
                 .exclude(nr3__in=used)
                 .exclude(nr4__in=used)
                 .first())
        if not chk43:
            return

        # check loc34
        chk34 = (Piece2x2
                 .objects
                 .filter(side3=self.loc34_exp_s3,
                         side4=self.loc34_exp_s4)
                 .exclude(nr1__in=used)
                 .exclude(nr2__in=used)
                 .exclude(nr3__in=used)
                 .exclude(nr4__in=used)
                 .first())
        if not chk34:
            return

        # check loc52
        chk52 = (Piece2x2
                 .objects
                 .filter(side3=self.loc52_exp_s3,
                         side4=self.loc52_exp_s4)
                 .exclude(nr1__in=used)
                 .exclude(nr2__in=used)
                 .exclude(nr3__in=used)
                 .exclude(nr4__in=used)
                 .first())
        if not chk52:
            return

        self._save(c4)

    def _find_nr60(self, c4):
        # print('60')
        exp_s3 = self.twoside_border
        for p2x2 in (Piece2x2
                     .objects
                     .filter(is_border=True,
                             side3=exp_s3, side4=self.loc60_exp_s4,
                             nr1__in=self.unused, nr2__in=self.unused, nr3__in=self.unused, nr4__in=self.unused)
                     .exclude(side2=self.twoside_border)):
            c4.loc60 = p2x2.nr
            c4.side2 = p2x2.side2
            self.loc52_exp_s3 = self.twoside2reverse[p2x2.side1]

            c4.nr37 = p2x2.nr1
            c4.nr38 = p2x2.nr2
            c4.nr39 = p2x2.nr3
            c4.nr40 = p2x2.nr4

            self._check(c4)
        # for

    def _find_nr33(self, c4):
        # print('33')
        exp_s4 = self.twoside_border
        for p2x2 in (Piece2x2
                     .objects
                     .filter(is_border=True,
                             side3=self.loc33_exp_s3, side4=exp_s4,
                             nr1__in=self.unused, nr2__in=self.unused, nr3__in=self.unused, nr4__in=self.unused)
                     .exclude(side1=self.twoside_border)):
            c4.loc33 = p2x2.nr
            c4.side1 = p2x2.side1
            self.loc34_exp_s4 = self.twoside2reverse[p2x2.side2]

            c4.nr33 = p2x2.nr1
            c4.nr34 = p2x2.nr2
            c4.nr35 = p2x2.nr3
            c4.nr36 = p2x2.nr4

            self.unused.remove(p2x2.nr1)
            self.unused.remove(p2x2.nr2)
            self.unused.remove(p2x2.nr3)
            self.unused.remove(p2x2.nr4)

            self._find_nr60(c4)

            self.unused.extend([p2x2.nr1, p2x2.nr2, p2x2.nr3, p2x2.nr4])
        # for

    def _find_nr42(self, c4):
        # print('42')
        for p2x2 in (Piece2x2
                     .objects
                     .filter(is_border=False,
                             side4=self.loc42_exp_s4, side3=self.loc42_exp_s3,
                             nr1__in=self.unused, nr2__in=self.unused, nr3__in=self.unused, nr4__in=self.unused)):
            c4.loc42 = p2x2.nr
            self.loc34_exp_s3 = self.twoside2reverse[p2x2.side1]
            self.loc43_exp_s4 = self.twoside2reverse[p2x2.side2]

            c4.nr29 = p2x2.nr1
            c4.nr30 = p2x2.nr2
            c4.nr31 = p2x2.nr3
            c4.nr32 = p2x2.nr4

            self.unused.remove(p2x2.nr1)
            self.unused.remove(p2x2.nr2)
            self.unused.remove(p2x2.nr3)
            self.unused.remove(p2x2.nr4)

            self._find_nr33(c4)

            self.unused.extend([p2x2.nr1, p2x2.nr2, p2x2.nr3, p2x2.nr4])
        # for

    def _find_nr41(self, c4):
        exp_s4 = self.twoside_border
        qset = (Piece2x2
                .objects
                .filter(is_border=True,
                        side3=self.loc41_exp_s3, side4=exp_s4,
                        nr1__in=self.unused, nr2__in=self.unused, nr3__in=self.unused, nr4__in=self.unused)
                .exclude(side1=self.twoside_border))
        # print('41 count: %s' % qset.count())
        for p2x2 in qset:
            c4.loc41 = p2x2.nr
            self.loc42_exp_s4 = self.twoside2reverse[p2x2.side2]
            self.loc33_exp_s3 = self.twoside2reverse[p2x2.side1]

            c4.nr25 = p2x2.nr1
            c4.nr26 = p2x2.nr2
            c4.nr27 = p2x2.nr3
            c4.nr28 = p2x2.nr4

            self.unused.remove(p2x2.nr1)
            self.unused.remove(p2x2.nr2)
            self.unused.remove(p2x2.nr3)
            self.unused.remove(p2x2.nr4)

            self._find_nr42(c4)

            self.unused.extend([p2x2.nr1, p2x2.nr2, p2x2.nr3, p2x2.nr4])
        # for

    def _find_nr51(self, c4):
        qset = (Piece2x2
                .objects
                .filter(is_border=False,
                        side4=self.loc51_exp_s4, side3=self.loc51_exp_s3,
                        nr1__in=self.unused, nr2__in=self.unused, nr3__in=self.unused, nr4__in=self.unused))
        # print('54 count: %s' % qset.count())
        for p2x2 in qset:
            c4.loc51 = p2x2.nr
            self.loc43_exp_s3 = self.twoside2reverse[p2x2.side1]
            self.loc52_exp_s4 = self.twoside2reverse[p2x2.side2]

            c4.nr21 = p2x2.nr1
            c4.nr22 = p2x2.nr2
            c4.nr23 = p2x2.nr3
            c4.nr24 = p2x2.nr4

            self.unused.remove(p2x2.nr1)
            self.unused.remove(p2x2.nr2)
            self.unused.remove(p2x2.nr3)
            self.unused.remove(p2x2.nr4)

            self._find_nr41(c4)

            self.unused.extend([p2x2.nr1, p2x2.nr2, p2x2.nr3, p2x2.nr4])
        # for

    def _find_nr59(self, c4):
        exp_s3 = self.twoside_border
        qset = (Piece2x2
                .objects
                .filter(is_border=True,
                        side3=exp_s3, side4=self.loc59_exp_s4,
                        nr1__in=self.unused, nr2__in=self.unused, nr3__in=self.unused, nr4__in=self.unused)
                .exclude(side2=self.twoside_border))
        # print('59 count: %s' % qset.count())
        for p2x2 in qset:
            c4.loc59 = p2x2.nr
            self.loc51_exp_s3 = self.twoside2reverse[p2x2.side1]
            self.loc60_exp_s4 = self.twoside2reverse[p2x2.side2]

            c4.nr17 = p2x2.nr1
            c4.nr18 = p2x2.nr2
            c4.nr19 = p2x2.nr3
            c4.nr20 = p2x2.nr4

            self.unused.remove(p2x2.nr1)
            self.unused.remove(p2x2.nr2)
            self.unused.remove(p2x2.nr3)
            self.unused.remove(p2x2.nr4)

            self._find_nr51(c4)

            self.unused.extend([p2x2.nr1, p2x2.nr2, p2x2.nr3, p2x2.nr4])
        # for

    def _find_nr58(self, c4):
        exp_s3 = self.twoside_border
        qset = (Piece2x2
                .objects
                .filter(is_border=True,
                        side3=exp_s3, side1=self.loc58_exp_s1, side4=self.loc58_exp_s4,
                        nr1__in=self.unused, nr2__in=self.unused, nr3__in=self.unused, nr4__in=self.unused)
                .exclude(side2=self.twoside_border))
        # print('58 count: %s' % qset.count())
        for p2x2 in qset:
            c4.loc58 = p2x2.nr
            self.loc59_exp_s4 = self.twoside2reverse[p2x2.side2]

            c4.nr13 = p2x2.nr1
            c4.nr14 = p2x2.nr2
            c4.nr15 = p2x2.nr3
            c4.nr16 = p2x2.nr4

            self.unused.remove(p2x2.nr1)
            self.unused.remove(p2x2.nr2)
            self.unused.remove(p2x2.nr3)
            self.unused.remove(p2x2.nr4)

            self._find_nr59(c4)

            self.unused.extend([p2x2.nr1, p2x2.nr2, p2x2.nr3, p2x2.nr4])
        # for

    def _find_nr57(self, c4):
        exp_s3 = exp_s4 = self.twoside_border
        qset = (Piece2x2
                .objects
                .filter(is_border=True,
                        side3=exp_s3, side4=exp_s4, side1=self.loc57_exp_s1,
                        nr1__in=self.unused, nr2__in=self.unused, nr3__in=self.unused, nr4__in=self.unused))
        # print('57 count: %s' % qset.count())
        for p2x2 in qset:
            c4.loc57 = p2x2.nr
            self.loc58_exp_s4 = self.twoside2reverse[p2x2.side2]

            c4.nr9 = p2x2.nr1
            c4.nr10 = p2x2.nr2
            c4.nr11 = p2x2.nr3
            c4.nr12 = p2x2.nr4

            self.unused.remove(p2x2.nr1)
            self.unused.remove(p2x2.nr2)
            self.unused.remove(p2x2.nr3)
            self.unused.remove(p2x2.nr4)

            self._find_nr58(c4)

            self.unused.extend([p2x2.nr1, p2x2.nr2, p2x2.nr3, p2x2.nr4])
        # for

    def _find_nr49(self, c4):
        exp_s4 = self.twoside_border
        qset = (Piece2x2
                .objects
                .filter(is_border=True,
                        side2=self.loc49_exp_s2, side4=exp_s4,
                        nr1__in=self.unused, nr2__in=self.unused, nr3__in=self.unused, nr4__in=self.unused)
                .exclude(side3=self.twoside_border)
                .exclude(side1=self.twoside_border))
        # print('49 count: %s' % qset.count())
        for p2x2 in qset:
            c4.loc49 = p2x2.nr
            self.loc57_exp_s1 = self.twoside2reverse[p2x2.side3]
            self.loc41_exp_s3 = self.twoside2reverse[p2x2.side1]

            c4.nr5 = p2x2.nr1
            c4.nr6 = p2x2.nr2
            c4.nr7 = p2x2.nr3
            c4.nr8 = p2x2.nr4

            self.unused.remove(p2x2.nr1)
            self.unused.remove(p2x2.nr2)
            self.unused.remove(p2x2.nr3)
            self.unused.remove(p2x2.nr4)

            self._find_nr57(c4)

            self.unused.extend([p2x2.nr1, p2x2.nr2, p2x2.nr3, p2x2.nr4])
        # for

    def _find_nr50(self, c4):
        qset = (Piece2x2
                .objects
                .filter(is_border=False,
                        has_hint=True,
                        nr3=181,
                        nr1__in=self.unused, nr2__in=self.unused, nr4__in=self.unused))
        # print('50 count: %s' % qset.count())
        for p2x2 in qset:
            c4.loc50 = p2x2.nr
            self.loc42_exp_s3 = self.twoside2reverse[p2x2.side1]
            self.loc51_exp_s4 = self.twoside2reverse[p2x2.side2]
            self.loc58_exp_s1 = self.twoside2reverse[p2x2.side3]
            self.loc49_exp_s2 = self.twoside2reverse[p2x2.side4]

            c4.nr1 = p2x2.nr1
            c4.nr2 = p2x2.nr2
            c4.nr3 = p2x2.nr3
            c4.nr4 = p2x2.nr4

            self.unused.remove(p2x2.nr1)
            self.unused.remove(p2x2.nr2)
            # self.unused.remove(p2x2.nr3)
            self.unused.remove(p2x2.nr4)

            self._find_nr49(c4)

            self.unused.extend([p2x2.nr1, p2x2.nr2, p2x2.nr4])
        # for

    def handle(self, *args, **options):

        seed = options['seed']
        self._fill_unused(seed)
        # self.stdout.write('[INFO] Selected base pieces: %s' % repr(self.unused))

        Corner4.objects.all().delete()

        c4 = Corner4()
        try:
            self._find_nr50(c4)
        except KeyboardInterrupt:
            pass

        if len(self.bulk):
            Corner4.objects.bulk_create(self.bulk)
            self.bulk = list()

            self.stdout.write('[INFO] Created %s Corner4' % self.count)

            count1 = Corner4.objects.distinct('side1').count()
            count2 = Corner4.objects.distinct('side2').count()
            self.stdout.write('[INFO] Distinct sides: %s, %s' % (count1, count2))

# end of file
