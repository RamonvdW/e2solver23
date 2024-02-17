# -*- coding: utf-8 -*-

#  Copyright (c) 2024 Ramon van der Winkel.
#  All rights reserved.
#  Licensed under BSD-3-Clause-Clear. See LICENSE file for details.

from django.core.management.base import BaseCommand
from BasePieces.border import GenerateBorder
from BasePieces.hints import ALL_HINT_NRS
from BasePieces.models import BasePiece
from Pieces2x2.models import Piece2x2, TwoSide
from Ring1.models import Ring1


class Command(BaseCommand):

    help = "Generate a Ring1"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        two2nr = dict()
        self.side2two = dict()     # [two side nr] = two_sides
        for two in TwoSide.objects.all():
            two2nr[two.two_sides] = two.nr
            self.side2two[two.nr] = two.two_sides
        # for
        self.twoside2reverse = dict()
        for two_sides, nr in two2nr.items():
            two_rev = two_sides[1] + two_sides[0]
            rev_nr = two2nr[two_rev]
            self.twoside2reverse[nr] = rev_nr
        # for

        self.nr2base = dict()
        for p1x1 in BasePiece.objects.all():
            self.nr2base[p1x1.nr] = p1x1
        # for

        self.ring1 = Ring1(
                        nr1=0, nr2=0, nr3=0, nr4=0, nr5=0, nr6=0, nr7=0, nr8=0, nr9=0, nr16=0, nr17=0, nr24=0, nr25=0,
                        nr32=0, nr33=0, nr40=0, nr41=0, nr48=0, nr49=0, nr56=0, nr57=0, nr58=0, nr59=0, nr60=0, nr61=0,
                        nr62=0, nr63=0, nr64=0, nr10=0, nr11=0, nr18=0, nr14=0, nr15=0, nr23=0, nr42=0, nr50=0, nr51=0,
                        nr47=0, nr54=0, nr55=0, nr36=0)

        # 1..60 = borders + corners
        self.unused = list(range(1, 256+1))
        for nr in ALL_HINT_NRS:
            self.unused.remove(nr)
        # for

        self.bcb1 = list()
        self.bcb2 = list()
        self.bcb3 = list()
        self.bcb4 = list()

        self.exp_loc2_s4 = 0
        self.exp_loc3_s4 = 0
        self.exp_loc6_s2 = 0
        self.exp_loc7_s2 = 0
        self.exp_loc9_s1 = 0
        self.exp_loc10_s4 = 0
        self.exp_loc15_s1 = 0
        self.exp_loc16_s1 = 0
        self.exp_loc17_s1 = 0
        self.exp_loc49_s3 = 0
        self.exp_loc56_s3 = 0
        self.exp_loc58_s4 = 0
        self.exp_loc63_s2 = 0

        self.count = 0
        self.count_print = 100
        self.bulk = list()

    def add_arguments(self, parser):
        parser.add_argument('seed', type=int, help='Randomization seed')

    def _save_ring1(self):
        self.ring1.pk = None
        self.ring1.save()
        self.stdout.write('[INFO] Saved Ring1 with pk=%s' % self.ring1.pk)

    def _check_loc10_c1(self):
        p = Piece2x2.objects.filter(has_hint=True,
                                    nr1=208,
                                    #nr2__in=self.unused, nr3__in=self.unused, nr4__in=self.unused,
                                    side1=self.exp_loc10_s1, side4=self.exp_loc10_s4).first()
        return p is not None

    def _check_loc15_c2(self):
        p = Piece2x2.objects.filter(has_hint=True,
                                    nr2=255,
                                    nr1__in=self.unused, nr3__in=self.unused, nr4__in=self.unused,
                                    side1=self.exp_loc15_s1, side2=self.exp_loc15_s2).first()
        return p is not None

    def _count(self):
        self.count += 1
        if self.count > self.count_print:
            print('count = %s' % self.count)
            self.count_print += 100

    def _find_loc56_c3(self):
        self._count()
        self._save_ring1()

    def _find_loc16_c2(self):
        b = self.bcb2[9:9+2]
        for p in Piece2x2.objects.filter(nr2=b[0], nr4=b[1],
                                         nr1__in=self.unused, nr3__in=self.unused,
                                         side1=self.exp_loc16_s1):
            self.ring1.nr16 = p.nr
            for nr in (p.nr1, p.nr2, p.nr3, p.nr4):
                self.unused.remove(nr)
            # for
            self.exp_loc15_s2 = self.twoside2reverse[p.side4]
            self.exp_loc24_s1 = self.twoside2reverse[p.side3]
            if self._check_loc15_c2() and self._check_loc10_c1():
                self._find_loc56_c3()
            self.unused.extend([p.nr1, p.nr2, p.nr3, p.nr4])
        # for

    def _find_loc7_c2(self):
        b = self.bcb2[4:4+2]
        for p in Piece2x2.objects.filter(nr1=b[0], nr2=b[1],
                                         nr3__in=self.unused, nr4__in=self.unused,
                                         side2=self.exp_loc7_s2):
            self.ring1.nr7 = p.nr
            self.exp_loc6_s2 = self.twoside2reverse[p.side4]
            self.exp_loc15_s1 = self.twoside2reverse[p.side3]
            for nr in (p.nr1, p.nr2, p.nr3, p.nr4):
                self.unused.remove(nr)
            # for
            self._find_loc16_c2()
            self.unused.extend([p.nr1, p.nr2, p.nr3, p.nr4])
        # for

    def _find_loc9_c1(self):
        b = self.bcb1[4:4+2]
        qset = Piece2x2.objects.filter(nr3=b[0], nr1=b[1],
                                       nr4__in=self.unused, nr2__in=self.unused,
                                       side1=self.exp_loc9_s1)
        for p in qset:
            self.ring1.nr9 = p.nr
            self.exp_loc10_s4 = self.twoside2reverse[p.side2]
            self.exp_loc17_s1 = self.twoside2reverse[p.side3]
            for nr in (p.nr1, p.nr2, p.nr3, p.nr4):
                self.unused.remove(nr)
            # for
            if self._check_loc10_c1():
                self._find_loc7_c2()
            self.unused.extend([p.nr1, p.nr2, p.nr3, p.nr4])
        # for

    def _find_loc2_c1(self):
        b = self.bcb1[9:9+2]
        qset = Piece2x2.objects.filter(nr1=b[0], nr2=b[1],
                                       nr3__in=self.unused, nr4__in=self.unused,
                                       side4=self.exp_loc2_s4)
        for p in qset:
            # print('loc2: %s' % p.nr)
            self.ring1.nr2 = p.nr
            self.exp_loc3_s4 = self.twoside2reverse[p.side2]
            self.exp_loc10_s1 = self.twoside2reverse[p.side3]
            for nr in (p.nr1, p.nr2, p.nr3, p.nr4):
                self.unused.remove(nr)
            # for
            self._find_loc9_c1()
            self.unused.extend([p.nr1, p.nr2, p.nr3, p.nr4])
        # for

    def _find_loc57_c4(self):
        c = self.bcb4[6:6+3]
        for p in Piece2x2.objects.filter(nr4=c[0], nr3=c[1], nr1=c[2],
                                         nr2__in=self.unused):
            self.ring1.nr57 = p.nr
            for nr in (p.nr1, p.nr2, p.nr3, p.nr4):
                self.unused.remove(nr)
            # for
            self.exp_loc49_s3 = self.twoside2reverse[p.side1]
            self.exp_loc58_s4 = self.twoside2reverse[p.side2]
            self._find_loc2_c1()
            self.unused.extend([p.nr1, p.nr2, p.nr3, p.nr4])
        # for

    def _find_loc64_c3(self):
        c = self.bcb3[6:6+3]
        for p in Piece2x2.objects.filter(nr2=c[0], nr4=c[1], nr3=c[2],
                                         nr1__in=self.unused):
            self.ring1.nr64 = p.nr
            for nr in (p.nr1, p.nr2, p.nr3, p.nr4):
                self.unused.remove(nr)
            # for
            self.exp_loc56_s3 = self.twoside2reverse[p.side1]
            self.exp_loc63_s2 = self.twoside2reverse[p.side3]
            self._find_loc57_c4()
            self.unused.extend([p.nr1, p.nr2, p.nr3, p.nr4])
        # for

    def _find_loc8_c2(self):
        c = self.bcb2[6:6+3]
        for p in Piece2x2.objects.filter(nr1=c[0], nr2=c[1], nr4=c[2],
                                         nr3__in=self.unused):
            self.ring1.nr8 = p.nr
            for nr in (p.nr1, p.nr2, p.nr3, p.nr4):
                self.unused.remove(nr)
            # for
            self.exp_loc7_s2 = self.twoside2reverse[p.side4]
            self.exp_loc16_s1 = self.twoside2reverse[p.side3]
            self._find_loc64_c3()
            self.unused.extend([p.nr1, p.nr2, p.nr3, p.nr4])
        # for

    def _find_loc1_c1(self):
        c = self.bcb1[6:6+3]
        qset = Piece2x2.objects.filter(nr3=c[0], nr1=c[1], nr2=c[2])
        for p in qset:
            self.ring1.nr1 = p.nr
            self.exp_loc2_s4 = self.twoside2reverse[p.side2]
            self.exp_loc9_s1 = self.twoside2reverse[p.side3]
            for nr in (p.nr1, p.nr2, p.nr3, p.nr4):
                self.unused.remove(nr)
            # for
            self._find_loc8_c2()
            self.unused.extend([p.nr1, p.nr2, p.nr3, p.nr4])
        # for

    def handle(self, *args, **options):

        seed = options['seed']
        self.ring1.seed = seed

        Ring1.objects.all().delete()

        gen = GenerateBorder(seed)
        sol = gen.get_first_solution()

        self.bcb1 = sol[:15]
        self.bcb2 = sol[15:30]
        self.bcb3 = sol[30:45]
        self.bcb4 = sol[45:]

        try:
            self._find_loc1_c1()
        except KeyboardInterrupt:
            pass
        else:
            print('[INFO] Counted: %s' % self.count)


# end of file
