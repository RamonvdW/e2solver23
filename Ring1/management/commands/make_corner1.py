# -*- coding: utf-8 -*-

#  Copyright (c) 2024 Ramon van der Winkel.
#  All rights reserved.
#  Licensed under BSD-3-Clause-Clear. See LICENSE file for details.

from django.core.management.base import BaseCommand
from Pieces2x2.models import TwoSide, Piece2x2
from Ring1.models import Corner1


class Command(BaseCommand):

    help = "Make all possible combinations of corner1"

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

        self.unused = list(range(1, 256+1))
        self.unused.remove(139)      # needed for loc 36
        self.unused.remove(208)      # needed for loc 10
        self.unused.remove(255)      # needed for loc 15
        self.unused.remove(181)      # needed for loc 50
        self.unused.remove(249)      # needed for loc 55

        # solve order: 10, 9, 1, 2, 3, 11, 17, 18, 25, 4
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

        self.count = 0
        self.count_print = 100000

    def _find_nr4(self, c1):
        exp_s1 = self.twoside_border
        for p2x2 in (Piece2x2
                     .objects
                     .filter(is_border=True,
                             side1=exp_s1, side4=self.loc4_exp_s4,
                             nr1__in=self.unused, nr2__in=self.unused, nr3__in=self.unused, nr4__in=self.unused)
                     .exclude(side2=self.twoside_border)):
            c1.loc4 = p2x2.nr

            c1.nr37 = p2x2.nr1
            c1.nr38 = p2x2.nr2
            c1.nr39 = p2x2.nr3
            c1.nr40 = p2x2.nr4

            self.count += 1
            if self.count > self.count_print:
                print('count: %s --> 10=%s, 9=%s, 1=%s, 2=%s, 3=%s, 17=%s, 18=%s' % (
                        self.count, c1.loc10, c1.loc9, c1.loc1, c1.loc2, c1.loc3, c1.loc17, c1.loc18))
                self.count_print += 100_000

                # c1.pk = None
                # c1.save()
                # print('saved Corner1; pk=%s' % c1.pk)
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

            c1.nr29 = p2x2.nr1
            c1.nr30 = p2x2.nr2
            c1.nr31 = p2x2.nr3
            c1.nr32 = p2x2.nr4

            self.unused.remove(p2x2.nr1)
            self.unused.remove(p2x2.nr2)
            self.unused.remove(p2x2.nr3)
            self.unused.remove(p2x2.nr4)

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
        print('17 count: %s' % qset.count())
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
        print('11 count: %s' % qset.count())
        for p2x2 in qset:
            c1.loc11 = p2x2.nr

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
        print('3 count: %s' % qset.count())
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
        print('2 count: %s' % qset.count())
        for p2x2 in qset:
            c1.loc2 = p2x2.nr
            self.loc3_exp_s4 = self.twoside2reverse[p2x2.side2]
            self.nr10_exp_s1 = self.twoside2reverse[p2x2.side3]

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
        print('1 count: %s' % qset.count())
        for p2x2 in qset:
            c1.loc1 = p2x2.nr
            self.loc2_exp_s4 = self.twoside2reverse[p2x2.side2]
            self.nr9_exp_s1 = self.twoside2reverse[p2x2.side4]

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
                        nr1__in=self.unused, nr2__in=self.unused, nr3__in=self.unused, nr4__in=self.unused))
        print('9 count: %s' % qset.count())
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
        print('10 count: %s' % qset.count())
        for p2x2 in qset:
            c1.loc10 = p2x2.nr
            self.loc2_exp_s3 = self.twoside2reverse[p2x2.side1]
            self.loc11_exp_s4 = self.twoside2reverse[p2x2.side2]
            self.loc18_exp_s1 = self.twoside2reverse[p2x2.side3]
            self.loc9_exp_s2 = self.twoside2reverse[p2x2.side4]

            c1.nr1 = 208
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
        c1 = Corner1()
        try:
            self._find_nr10(c1)
        except KeyboardInterrupt:
            pass

# end of file
