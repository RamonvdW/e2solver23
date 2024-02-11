# -*- coding: utf-8 -*-

#  Copyright (c) 2024 Ramon van der Winkel.
#  All rights reserved.
#  Licensed under BSD-3-Clause-Clear. See LICENSE file for details.

from django.core.management.base import BaseCommand
from Pieces2x2.models import TwoSide, Piece2x2
from Ring1.models import Corner3
import random


class Command(BaseCommand):

    help = "Make all possible combinations of corner3"

    """
                       +----+
                       | 40 |
                  +----+----+
                  | 47 | 48 |
             +----+----+----+
             | 54 | 55 | 56 |
        +----+----+----+----+
        | 61 | 62 | 63 | 64 |
        +----+----+----+----+
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.corner = 3
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

        # solve order: 55, 56, 64, 63, 62, 54, 47, 47, 40, 61
        self.loc47_exp_s3 = 0
        self.loc56_exp_s4 = 0
        self.loc63_exp_s1 = 0
        self.loc54_exp_s2 = 0
        self.loc48_exp_s3 = 0
        self.loc64_exp_s1 = 0
        self.loc63_exp_s2 = 0
        self.loc62_exp_s2 = 0
        self.loc54_exp_s3 = 0
        self.loc61_exp_s2 = 0
        self.loc40_exp_s3 = 0
        self.loc47_exp_s2 = 0

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

    def _save(self, c3):
        self.count += 1
        c3.pk = None
        self.bulk.append(c3)
        if len(self.bulk) >= 1000:
            if self.count >= self.count_print:
                print('count: %s --> 55=%s, 56=%s, 64=%s, 63=%s, 62=%s, 48=%s, 47=%s' % (
                    self.count, c3.loc55, c3.loc56, c3.loc64, c3.loc63, c3.loc62, c3.loc48, c3.loc47))
                self.count_print += 5000
            Corner3.objects.bulk_create(self.bulk)
            self.bulk = list()

    def _find_nr61(self, c3):
        exp_s3 = self.twoside_border
        for p2x2 in (Piece2x2
                     .objects
                     .filter(is_border=True,
                             side3=exp_s3, side2=self.loc61_exp_s2,
                             nr1__in=self.unused, nr2__in=self.unused, nr3__in=self.unused, nr4__in=self.unused)
                     .exclude(side4=self.twoside_border)):
            c3.loc61 = p2x2.nr
            c3.side4 = p2x2.side4

            c3.nr37 = p2x2.nr1
            c3.nr38 = p2x2.nr2
            c3.nr39 = p2x2.nr3
            c3.nr40 = p2x2.nr4

            self._save(c3)
        # for

    def _find_nr40(self, c3):
        exp_s2 = self.twoside_border
        for p2x2 in (Piece2x2
                     .objects
                     .filter(is_border=True,
                             side3=self.loc40_exp_s3, side2=exp_s2,
                             nr1__in=self.unused, nr2__in=self.unused, nr3__in=self.unused, nr4__in=self.unused)
                     .exclude(side1=self.twoside_border)):
            c3.loc40 = p2x2.nr
            c3.side1 = p2x2.side1

            c3.nr33 = p2x2.nr1
            c3.nr34 = p2x2.nr2
            c3.nr35 = p2x2.nr3
            c3.nr36 = p2x2.nr4

            self.unused.remove(p2x2.nr1)
            self.unused.remove(p2x2.nr2)
            self.unused.remove(p2x2.nr3)
            self.unused.remove(p2x2.nr4)

            self._find_nr61(c3)

            self.unused.extend([p2x2.nr1, p2x2.nr2, p2x2.nr3, p2x2.nr4])
        # for

    def _find_nr47(self, c3):
        for p2x2 in (Piece2x2
                     .objects
                     .filter(is_border=False,
                             side2=self.loc47_exp_s2, side3=self.loc47_exp_s3,
                             nr1__in=self.unused, nr2__in=self.unused, nr3__in=self.unused, nr4__in=self.unused)):
            c3.loc47 = p2x2.nr

            c3.nr29 = p2x2.nr1
            c3.nr30 = p2x2.nr2
            c3.nr31 = p2x2.nr3
            c3.nr32 = p2x2.nr4

            self.unused.remove(p2x2.nr1)
            self.unused.remove(p2x2.nr2)
            self.unused.remove(p2x2.nr3)
            self.unused.remove(p2x2.nr4)

            self._find_nr40(c3)

            self.unused.extend([p2x2.nr1, p2x2.nr2, p2x2.nr3, p2x2.nr4])
        # for

    def _find_nr48(self, c3):
        exp_s2 = self.twoside_border
        qset = (Piece2x2
                .objects
                .filter(is_border=True,
                        side3=self.loc48_exp_s3, side2=exp_s2,
                        nr1__in=self.unused, nr2__in=self.unused, nr3__in=self.unused, nr4__in=self.unused)
                .exclude(side1=self.twoside_border))
        # print('48 count: %s' % qset.count())
        for p2x2 in qset:
            c3.loc48 = p2x2.nr
            self.loc47_exp_s2 = self.twoside2reverse[p2x2.side4]
            self.loc40_exp_s3 = self.twoside2reverse[p2x2.side1]

            c3.nr25 = p2x2.nr1
            c3.nr26 = p2x2.nr2
            c3.nr27 = p2x2.nr3
            c3.nr28 = p2x2.nr4

            self.unused.remove(p2x2.nr1)
            self.unused.remove(p2x2.nr2)
            self.unused.remove(p2x2.nr3)
            self.unused.remove(p2x2.nr4)

            self._find_nr47(c3)

            self.unused.extend([p2x2.nr1, p2x2.nr2, p2x2.nr3, p2x2.nr4])
        # for

    def _find_nr54(self, c3):
        qset = (Piece2x2
                .objects
                .filter(is_border=False,
                        side2=self.loc54_exp_s2, side3=self.loc54_exp_s3,
                        nr1__in=self.unused, nr2__in=self.unused, nr3__in=self.unused, nr4__in=self.unused))
        # print('54 count: %s' % qset.count())
        for p2x2 in qset:
            c3.loc54 = p2x2.nr

            c3.nr21 = p2x2.nr1
            c3.nr22 = p2x2.nr2
            c3.nr23 = p2x2.nr3
            c3.nr24 = p2x2.nr4

            self.unused.remove(p2x2.nr1)
            self.unused.remove(p2x2.nr2)
            self.unused.remove(p2x2.nr3)
            self.unused.remove(p2x2.nr4)

            self._find_nr48(c3)

            self.unused.extend([p2x2.nr1, p2x2.nr2, p2x2.nr3, p2x2.nr4])
        # for

    def _find_nr62(self, c3):
        exp_s3 = self.twoside_border
        qset = (Piece2x2
                .objects
                .filter(is_border=True,
                        side3=exp_s3, side2=self.loc62_exp_s2,
                        nr1__in=self.unused, nr2__in=self.unused, nr3__in=self.unused, nr4__in=self.unused)
                .exclude(side4=self.twoside_border))
        # print('62 count: %s' % qset.count())
        for p2x2 in qset:
            c3.loc62 = p2x2.nr
            self.loc54_exp_s3 = self.twoside2reverse[p2x2.side1]
            self.loc61_exp_s2 = self.twoside2reverse[p2x2.side4]

            c3.nr17 = p2x2.nr1
            c3.nr18 = p2x2.nr2
            c3.nr19 = p2x2.nr3
            c3.nr20 = p2x2.nr4

            self.unused.remove(p2x2.nr1)
            self.unused.remove(p2x2.nr2)
            self.unused.remove(p2x2.nr3)
            self.unused.remove(p2x2.nr4)

            self._find_nr54(c3)

            self.unused.extend([p2x2.nr1, p2x2.nr2, p2x2.nr3, p2x2.nr4])
        # for

    def _find_nr63(self, c3):
        exp_s3 = self.twoside_border
        qset = (Piece2x2
                .objects
                .filter(is_border=True,
                        side3=exp_s3, side2=self.loc63_exp_s2, side1=self.loc63_exp_s1,
                        nr1__in=self.unused, nr2__in=self.unused, nr3__in=self.unused, nr4__in=self.unused)
                .exclude(side4=self.twoside_border))
        # print('63 count: %s' % qset.count())
        for p2x2 in qset:
            c3.loc63 = p2x2.nr
            self.loc62_exp_s2 = self.twoside2reverse[p2x2.side4]

            c3.nr13 = p2x2.nr1
            c3.nr14 = p2x2.nr2
            c3.nr15 = p2x2.nr3
            c3.nr16 = p2x2.nr4

            self.unused.remove(p2x2.nr1)
            self.unused.remove(p2x2.nr2)
            self.unused.remove(p2x2.nr3)
            self.unused.remove(p2x2.nr4)

            self._find_nr62(c3)

            self.unused.extend([p2x2.nr1, p2x2.nr2, p2x2.nr3, p2x2.nr4])
        # for

    def _find_nr64(self, c3):
        exp_s2 = exp_s3 = self.twoside_border
        qset = (Piece2x2
                .objects
                .filter(is_border=True,
                        side2=exp_s2, side3=exp_s3, side1=self.loc64_exp_s1,
                        nr1__in=self.unused, nr2__in=self.unused, nr3__in=self.unused, nr4__in=self.unused))
        # print('64 count: %s' % qset.count())
        for p2x2 in qset:
            c3.loc64 = p2x2.nr
            self.loc63_exp_s2 = self.twoside2reverse[p2x2.side4]

            c3.nr9 = p2x2.nr1
            c3.nr10 = p2x2.nr2
            c3.nr11 = p2x2.nr3
            c3.nr12 = p2x2.nr4

            self.unused.remove(p2x2.nr1)
            self.unused.remove(p2x2.nr2)
            self.unused.remove(p2x2.nr3)
            self.unused.remove(p2x2.nr4)

            self._find_nr63(c3)

            self.unused.extend([p2x2.nr1, p2x2.nr2, p2x2.nr3, p2x2.nr4])
        # for

    def _find_nr56(self, c3):
        exp_s2 = self.twoside_border
        qset = (Piece2x2
                .objects
                .filter(is_border=True,
                        side4=self.loc56_exp_s4, side2=exp_s2,
                        nr1__in=self.unused, nr2__in=self.unused, nr3__in=self.unused, nr4__in=self.unused))
        # print('56 count: %s' % qset.count())
        for p2x2 in qset:
            c3.loc56 = p2x2.nr
            self.loc64_exp_s1 = self.twoside2reverse[p2x2.side3]
            self.loc48_exp_s3 = self.twoside2reverse[p2x2.side1]

            c3.nr5 = p2x2.nr1
            c3.nr6 = p2x2.nr2
            c3.nr7 = p2x2.nr3
            c3.nr8 = p2x2.nr4

            self.unused.remove(p2x2.nr1)
            self.unused.remove(p2x2.nr2)
            self.unused.remove(p2x2.nr3)
            self.unused.remove(p2x2.nr4)

            self._find_nr64(c3)

            self.unused.extend([p2x2.nr1, p2x2.nr2, p2x2.nr3, p2x2.nr4])
        # for

    def _find_nr55(self, c3):
        qset = (Piece2x2
                .objects
                .filter(is_border=False,
                        has_hint=True,
                        nr4=249,
                        nr1__in=self.unused, nr2__in=self.unused, nr3__in=self.unused))
        # print('55 count: %s' % qset.count())
        for p2x2 in qset:
            c3.loc55 = p2x2.nr
            self.loc47_exp_s3 = self.twoside2reverse[p2x2.side1]
            self.loc56_exp_s4 = self.twoside2reverse[p2x2.side2]
            self.loc63_exp_s1 = self.twoside2reverse[p2x2.side3]
            self.loc54_exp_s2 = self.twoside2reverse[p2x2.side4]

            c3.nr1 = p2x2.nr1
            c3.nr2 = p2x2.nr2
            c3.nr3 = p2x2.nr3
            c3.nr4 = p2x2.nr4

            self.unused.remove(p2x2.nr1)
            self.unused.remove(p2x2.nr2)
            self.unused.remove(p2x2.nr3)
            # self.unused.remove(p2x2.nr4)

            self._find_nr56(c3)

            self.unused.extend([p2x2.nr1, p2x2.nr2, p2x2.nr3])
        # for

    def handle(self, *args, **options):

        seed = options['seed']
        self._fill_unused(seed)
        # self.stdout.write('[INFO] Selected base pieces: %s' % repr(self.unused))

        Corner3.objects.all().delete()

        c3 = Corner3()
        try:
            self._find_nr55(c3)
        except KeyboardInterrupt:
            pass

        if len(self.bulk):
            Corner3.objects.bulk_create(self.bulk)
            self.bulk = list()

        self.stdout.write('[INFO] Created %s Corner3' % self.count)

        count1 = Corner3.objects.distinct('side1').count()
        count2 = Corner3.objects.distinct('side4').count()
        self.stdout.write('[INFO] Distinct sides: %s, %s' % (count1, count2))

# end of file
