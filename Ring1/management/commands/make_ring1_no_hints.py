# -*- coding: utf-8 -*-

#  Copyright (c) 2024 Ramon van der Winkel.
#  All rights reserved.
#  Licensed under BSD-3-Clause-Clear. See LICENSE file for details.

from django.core.management.base import BaseCommand
from BasePieces.border import GenerateBorder
from BasePieces.hints import CENTER_NR
from BasePieces.models import BasePiece
from Pieces2x2.models import Piece2x2, TwoSide, TwoSideOptions
from Ring1.models import Ring1


class Command(BaseCommand):

    help = "Generate a Ring1 without considering the 4 outer hints"

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
        self.unused.remove(CENTER_NR)

        self.used = list()

        self.bcb1 = list()
        self.bcb2 = list()
        self.bcb3 = list()
        self.bcb4 = list()

        self.count = 0
        self.count_print = 100
        self.bulk = list()

    def add_arguments(self, parser):
        parser.add_argument('seed', type=int, help='Randomization seed')

    def _make_used(self, p_nrs: tuple | list):
        for nr in p_nrs:
            self.unused.remove(nr)
        # for
        self.used.extend(p_nrs)

    def _make_unused(self, p_nrs: tuple | list):
        for nr in p_nrs:
            self.used.remove(nr)
        # for
        self.unused.extend(p_nrs)

    def _save_ring1(self):
        self.ring1.pk = None
        self.ring1.save()
        self.stdout.write('[INFO] Saved Ring1 with pk=%s' % self.ring1.pk)

    def _count(self):
        self.count += 1
        if self.count > self.count_print:
            print('count = %s' % self.count)
            self.count_print += 100

    def _check_loc55(self):
        qset = Piece2x2.objects.filter(nr1__in=self.unused, nr2__in=self.unused,
                                       nr3__in=self.unused, nr4__in=self.unused,
                                       side2=self.exp_loc55_s2, side3=self.exp_loc55_s3)
        return qset.first() is not None

    def _check_loc50(self):
        qset = Piece2x2.objects.filter(nr1__in=self.unused, nr2__in=self.unused,
                                       nr3__in=self.unused, nr4__in=self.unused,
                                       side4=self.exp_loc50_s4, side3=self.exp_loc50_s3)
        return qset.first() is not None

    def _check_loc15(self):
        qset = Piece2x2.objects.filter(nr1__in=self.unused, nr2__in=self.unused,
                                       nr3__in=self.unused, nr4__in=self.unused,
                                       side1=self.exp_loc15_s1, side2=self.exp_loc15_s2)
        return qset.first() is not None

    def _check_loc10(self):
        qset = Piece2x2.objects.filter(nr1__in=self.unused, nr2__in=self.unused,
                                       nr3__in=self.unused, nr4__in=self.unused,
                                       side1=self.exp_loc10_s1, side4=self.exp_loc10_s4)
        return qset.first() is not None

    def _find_loc55(self):
        qset = Piece2x2.objects.filter(nr1__in=self.unused, nr2__in=self.unused,
                                       nr3__in=self.unused, nr4__in=self.unused,
                                       side2=self.exp_loc55_s2, side3=self.exp_loc55_s3)
        for p in qset:
            self.ring1.nr55 = p.nr
            p_nrs = (p.nr1, p.nr2, p.nr3, p.nr4)
            self._make_used(p_nrs)
            self._save_ring1()
            self._make_unused(p_nrs)
        # for

    def _find_loc50(self):
        qset = Piece2x2.objects.filter(nr1__in=self.unused, nr2__in=self.unused,
                                       nr3__in=self.unused, nr4__in=self.unused,
                                       side4=self.exp_loc50_s4, side3=self.exp_loc50_s3)
        for p in qset:
            self.ring1.nr50 = p.nr
            p_nrs = (p.nr1, p.nr2, p.nr3, p.nr4)
            self._make_used(p_nrs)
            self._find_loc55()
            self._make_unused(p_nrs)
        # for

    def _find_loc15(self):
        qset = Piece2x2.objects.filter(nr1__in=self.unused, nr2__in=self.unused,
                                       nr3__in=self.unused, nr4__in=self.unused,
                                       side1=self.exp_loc15_s1, side2=self.exp_loc15_s2)
        for p in qset:
            self.ring1.nr15 = p.nr
            p_nrs = (p.nr1, p.nr2, p.nr3, p.nr4)
            self._make_used(p_nrs)
            self._find_loc50()
            self._make_unused(p_nrs)
        # for

    def _find_loc10(self):
        qset = Piece2x2.objects.filter(nr1__in=self.unused, nr2__in=self.unused,
                                       nr3__in=self.unused, nr4__in=self.unused,
                                       side1=self.exp_loc10_s1, side4=self.exp_loc10_s4)
        for p in qset:
            self.ring1.nr10 = p.nr
            p_nrs = (p.nr1, p.nr2, p.nr3, p.nr4)
            self._make_used(p_nrs)
            self._find_loc15()
            self._make_unused(p_nrs)
        # for

    def _find_loc25_c1(self):
        b = self.bcb1[0:0+2]
        qset = Piece2x2.objects.filter(nr3=b[0], nr1=b[1],
                                       nr4__in=self.unused, nr2__in=self.unused,
                                       side1=self.exp_loc25_s1, side3=self.exp_loc25_s3)
        for p in qset:
            self.ring1.nr25 = p.nr
            p_nrs = (p.nr1, p.nr2, p.nr3, p.nr4)
            self._make_used(p_nrs)
            self._find_loc10()
            self._make_unused(p_nrs)
        # for

    def _find_loc33_c4(self):
        b = self.bcb4[13:13+2]
        qset = Piece2x2.objects.filter(nr3=b[0], nr1=b[1],
                                       nr4__in=self.unused, nr2__in=self.unused,
                                       side3=self.exp_loc33_s3)
        for p in qset:
            self.ring1.nr33 = p.nr
            self.exp_loc25_s3 = self.twoside2reverse[p.side1]
            p_nrs = (p.nr1, p.nr2, p.nr3, p.nr4)
            self._make_used(p_nrs)
            self._find_loc25_c1()
            self._make_unused(p_nrs)
        # for

    def _find_loc60_c4(self):
        b = self.bcb4[0:0+2]
        for p in Piece2x2.objects.filter(nr4=b[0], nr3=b[1],
                                         nr1__in=self.unused, nr2__in=self.unused,
                                         side4=self.exp_loc60_s4, side2=self.exp_loc60_s2):
            self.ring1.nr60 = p.nr
            p_nrs = (p.nr1, p.nr2, p.nr3, p.nr4)
            self._make_used(p_nrs)
            self._find_loc33_c4()
            self._make_unused(p_nrs)
        # for

    def _find_loc61_c3(self):
        b = self.bcb3[13:13+2]
        for p in Piece2x2.objects.filter(nr4=b[0], nr3=b[1],
                                         nr1__in=self.unused, nr2__in=self.unused,
                                         side2=self.exp_loc61_s2):
            self.ring1.nr61 = p.nr
            self.exp_loc60_s2 = self.twoside2reverse[p.side4]
            p_nrs = (p.nr1, p.nr2, p.nr3, p.nr4)
            self._make_used(p_nrs)
            self._find_loc60_c4()
            self._make_unused(p_nrs)
        # for

    def _find_loc40_c3(self):
        b = self.bcb3[0:0+2]
        for p in Piece2x2.objects.filter(nr2=b[0], nr4=b[1],
                                         nr1__in=self.unused, nr3__in=self.unused,
                                         side3=self.exp_loc40_s3, side1=self.exp_loc40_s1):
            self.ring1.nr40 = p.nr
            p_nrs = (p.nr1, p.nr2, p.nr3, p.nr4)
            self._make_used(p_nrs)
            self._find_loc61_c3()
            self._make_unused(p_nrs)
        # for

    def _find_loc32_c2(self):
        b = self.bcb2[13:13+2]
        for p in Piece2x2.objects.filter(nr2=b[0], nr4=b[1],
                                         nr1__in=self.unused, nr3__in=self.unused,
                                         side1=self.exp_loc32_s1):
            self.ring1.nr32 = p.nr
            self.exp_loc40_s1 = self.twoside2reverse[p.side3]
            p_nrs = (p.nr1, p.nr2, p.nr3, p.nr4)
            self._make_used(p_nrs)
            self._find_loc40_c3()
            self._make_unused(p_nrs)
        # for

    def _find_loc5_c2(self):
        b = self.bcb2[0:0+2]
        for p in Piece2x2.objects.filter(nr1=b[0], nr2=b[1],
                                         nr3__in=self.unused, nr4__in=self.unused,
                                         side2=self.exp_loc5_s2, side4=self.exp_loc5_s4):
            self.ring1.nr5 = p.nr
            p_nrs = (p.nr1, p.nr2, p.nr3, p.nr4)
            self._make_used(p_nrs)
            self._find_loc32_c2()
            self._make_unused(p_nrs)
        # for

    def _find_loc4_c1(self):
        b = self.bcb1[13:13+2]
        qset = Piece2x2.objects.filter(nr1=b[0], nr2=b[1],
                                       nr3__in=self.unused, nr4__in=self.unused,
                                       side4=self.exp_loc4_s4)
        for p in qset:
            self.ring1.nr4 = p.nr
            self.exp_loc5_s4 = self.twoside2reverse[p.side2]
            p_nrs = (p.nr1, p.nr2, p.nr3, p.nr4)
            self._make_used(p_nrs)
            self._find_loc5_c2()
            self._make_unused(p_nrs)
        # for

    def _find_loc41_c4(self):
        b = self.bcb4[11:11+2]
        qset = Piece2x2.objects.filter(nr3=b[0], nr1=b[1],
                                       nr4__in=self.unused, nr2__in=self.unused,
                                       side3=self.exp_loc41_s3)
        for p in qset:
            self.ring1.nr41 = p.nr
            self.exp_loc33_s3 = self.twoside2reverse[p.side1]
            p_nrs = (p.nr1, p.nr2, p.nr3, p.nr4)
            self._make_used(p_nrs)
            self._find_loc4_c1()
            self._make_unused(p_nrs)
        # for

    def _find_loc59_c4(self):
        b = self.bcb4[2:2+2]
        for p in Piece2x2.objects.filter(nr4=b[0], nr3=b[1],
                                         nr1__in=self.unused, nr2__in=self.unused,
                                         side4=self.exp_loc59_s4):
            self.ring1.nr59 = p.nr
            self.exp_loc60_s4 = self.twoside2reverse[p.side2]
            p_nrs = (p.nr1, p.nr2, p.nr3, p.nr4)
            self._make_used(p_nrs)
            self._find_loc41_c4()
            self._make_unused(p_nrs)
        # for

    def _find_loc62_c3(self):
        b = self.bcb3[11:11+2]
        for p in Piece2x2.objects.filter(nr4=b[0], nr3=b[1],
                                         nr1__in=self.unused, nr2__in=self.unused,
                                         side2=self.exp_loc62_s2):
            self.ring1.nr62 = p.nr
            self.exp_loc61_s2 = self.twoside2reverse[p.side4]
            p_nrs = (p.nr1, p.nr2, p.nr3, p.nr4)
            self._make_used(p_nrs)
            self._find_loc59_c4()
            self._make_unused(p_nrs)
        # for

    def _find_loc48_c3(self):
        b = self.bcb3[2:2+2]
        for p in Piece2x2.objects.filter(nr2=b[0], nr4=b[1],
                                         nr1__in=self.unused, nr3__in=self.unused,
                                         side3=self.exp_loc48_s3):
            self.ring1.nr48 = p.nr
            self.exp_loc40_s3 = self.twoside2reverse[p.side1]
            p_nrs = (p.nr1, p.nr2, p.nr3, p.nr4)
            self._make_used(p_nrs)
            self._find_loc62_c3()
            self._make_unused(p_nrs)
        # for

    def _find_loc24_c2(self):
        b = self.bcb2[11:11+2]
        for p in Piece2x2.objects.filter(nr2=b[0], nr4=b[1],
                                         nr1__in=self.unused, nr3__in=self.unused,
                                         side1=self.exp_loc24_s1):
            self.ring1.nr24 = p.nr
            self.exp_loc32_s1 = self.twoside2reverse[p.side3]
            p_nrs = (p.nr1, p.nr2, p.nr3, p.nr4)
            self._make_used(p_nrs)
            self._find_loc48_c3()
            self._make_unused(p_nrs)
        # for

    def _find_loc6_c2(self):
        b = self.bcb2[2:2+2]
        for p in Piece2x2.objects.filter(nr1=b[0], nr2=b[1],
                                         nr3__in=self.unused, nr4__in=self.unused,
                                         side2=self.exp_loc6_s2):
            self.ring1.nr6 = p.nr
            self.exp_loc5_s2 = self.twoside2reverse[p.side4]
            p_nrs = (p.nr1, p.nr2, p.nr3, p.nr4)
            self._make_used(p_nrs)
            self._find_loc24_c2()
            self._make_unused(p_nrs)
        # for

    def _find_loc3_c1(self):
        b = self.bcb1[11:11+2]
        qset = Piece2x2.objects.filter(nr1=b[0], nr2=b[1],
                                       nr3__in=self.unused, nr4__in=self.unused,
                                       side4=self.exp_loc3_s4)
        for p in qset:
            self.ring1.nr3 = p.nr
            self.exp_loc4_s4 = self.twoside2reverse[p.side2]
            p_nrs = (p.nr1, p.nr2, p.nr3, p.nr4)
            self._make_used(p_nrs)
            self._find_loc6_c2()
            self._make_unused(p_nrs)
        # for

    def _find_loc17_c1(self):
        b = self.bcb1[2:2+2]
        qset = Piece2x2.objects.filter(nr3=b[0], nr1=b[1],
                                       nr4__in=self.unused, nr2__in=self.unused,
                                       side1=self.exp_loc17_s1)
        for p in qset:
            self.ring1.nr17 = p.nr
            self.exp_loc25_s1 = self.twoside2reverse[p.side3]
            p_nrs = (p.nr1, p.nr2, p.nr3, p.nr4)
            self._make_used(p_nrs)
            self._find_loc3_c1()
            self._make_unused(p_nrs)
        # for

    def _find_loc49_c4(self):
        b = self.bcb4[9:9+2]
        qset = Piece2x2.objects.filter(nr3=b[0], nr1=b[1],
                                       nr4__in=self.unused, nr2__in=self.unused,
                                       side3=self.exp_loc49_s3)
        for p in qset:
            self.ring1.nr49 = p.nr
            self.exp_loc41_s3 = self.twoside2reverse[p.side1]
            self.exp_loc50_s4 = self.twoside2reverse[p.side2]
            p_nrs = (p.nr1, p.nr2, p.nr3, p.nr4)
            self._make_used(p_nrs)
            if self._check_loc50():
                self._find_loc17_c1()
            self._make_unused(p_nrs)
        # for

    def _find_loc58_c4(self):
        b = self.bcb4[4:4+2]
        for p in Piece2x2.objects.filter(nr4=b[0], nr3=b[1],
                                         nr1__in=self.unused, nr2__in=self.unused,
                                         side4=self.exp_loc58_s4):
            self.ring1.nr58 = p.nr
            self.exp_loc59_s4 = self.twoside2reverse[p.side2]
            self.exp_loc50_s3 = self.twoside2reverse[p.side1]
            p_nrs = (p.nr1, p.nr2, p.nr3, p.nr4)
            self._make_used(p_nrs)
            self._find_loc49_c4()
            self._make_unused(p_nrs)
        # for

    def _find_loc63_c3(self):
        b = self.bcb3[9:9+2]
        for p in Piece2x2.objects.filter(nr4=b[0], nr3=b[1],
                                         nr1__in=self.unused, nr2__in=self.unused,
                                         side2=self.exp_loc63_s2):
            self.ring1.nr63 = p.nr
            self.exp_loc62_s2 = self.twoside2reverse[p.side4]
            self.exp_loc55_s3 = self.twoside2reverse[p.side1]
            p_nrs = (p.nr1, p.nr2, p.nr3, p.nr4)
            self._make_used(p_nrs)
            if self._check_loc55():
                self._find_loc58_c4()
            self._make_unused(p_nrs)
        # for

    def _find_loc56_c3(self):
        b = self.bcb3[4:4+2]
        for p in Piece2x2.objects.filter(nr2=b[0], nr4=b[1],
                                         nr1__in=self.unused, nr3__in=self.unused,
                                         side3=self.exp_loc56_s3):
            self.ring1.nr56 = p.nr
            self.exp_loc55_s2 = self.twoside2reverse[p.side4]
            self.exp_loc48_s3 = self.twoside2reverse[p.side1]
            p_nrs = (p.nr1, p.nr2, p.nr3, p.nr4)
            self._make_used(p_nrs)
            self._find_loc63_c3()
            self._make_unused(p_nrs)
        # for

    def _find_loc16_c2(self):
        b = self.bcb2[9:9+2]
        for p in Piece2x2.objects.filter(nr2=b[0], nr4=b[1],
                                         nr1__in=self.unused, nr3__in=self.unused,
                                         side1=self.exp_loc16_s1):
            self.ring1.nr16 = p.nr
            self.exp_loc15_s2 = self.twoside2reverse[p.side4]
            self.exp_loc24_s1 = self.twoside2reverse[p.side3]
            p_nrs = (p.nr1, p.nr2, p.nr3, p.nr4)
            self._make_used(p_nrs)
            if self._check_loc15():
                self._find_loc56_c3()
            self._make_unused(p_nrs)
        # for

    def _find_loc7_c2(self):
        b = self.bcb2[4:4+2]
        for p in Piece2x2.objects.filter(nr1=b[0], nr2=b[1],
                                         nr3__in=self.unused, nr4__in=self.unused,
                                         side2=self.exp_loc7_s2):
            self.ring1.nr7 = p.nr
            self.exp_loc6_s2 = self.twoside2reverse[p.side4]
            self.exp_loc15_s1 = self.twoside2reverse[p.side3]
            p_nrs = (p.nr1, p.nr2, p.nr3, p.nr4)
            self._make_used(p_nrs)
            self._find_loc16_c2()
            self._make_unused(p_nrs)
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
            p_nrs = (p.nr1, p.nr2, p.nr3, p.nr4)
            self._make_used(p_nrs)
            if self._check_loc10():
                self._find_loc7_c2()
            self._make_unused(p_nrs)
        # for

    def _find_loc2_c1(self):
        b = self.bcb1[9:9+2]
        qset = Piece2x2.objects.filter(nr1=b[0], nr2=b[1],
                                       nr3__in=self.unused, nr4__in=self.unused,
                                       side4=self.exp_loc2_s4)
        for p in qset:
            self.ring1.nr2 = p.nr
            self.exp_loc3_s4 = self.twoside2reverse[p.side2]
            self.exp_loc10_s1 = self.twoside2reverse[p.side3]
            p_nrs = (p.nr1, p.nr2, p.nr3, p.nr4)
            self._make_used(p_nrs)
            self._find_loc9_c1()
            self._make_unused(p_nrs)
        # for

    def _find_loc57_c4(self):
        c = self.bcb4[6:6+3]
        for p in Piece2x2.objects.filter(nr4=c[0], nr3=c[1], nr1=c[2],
                                         nr2__in=self.unused):
            self.ring1.nr57 = p.nr
            self.exp_loc49_s3 = self.twoside2reverse[p.side1]
            self.exp_loc58_s4 = self.twoside2reverse[p.side2]
            p_nrs = (p.nr1, p.nr2, p.nr3, p.nr4)
            self._make_used(p_nrs)
            self._find_loc2_c1()
            self._make_unused(p_nrs)
        # for

    def _find_loc64_c3(self):
        c = self.bcb3[6:6+3]
        for p in Piece2x2.objects.filter(nr2=c[0], nr4=c[1], nr3=c[2],
                                         nr1__in=self.unused):
            self.ring1.nr64 = p.nr
            self.exp_loc56_s3 = self.twoside2reverse[p.side1]
            self.exp_loc63_s2 = self.twoside2reverse[p.side4]
            p_nrs = (p.nr1, p.nr2, p.nr3, p.nr4)
            self._make_used(p_nrs)
            self._find_loc57_c4()
            self._make_unused(p_nrs)
        # for

    def _find_loc8_c2(self):
        c = self.bcb2[6:6+3]
        for p in Piece2x2.objects.filter(nr1=c[0], nr2=c[1], nr4=c[2],
                                         nr3__in=self.unused):
            self.ring1.nr8 = p.nr
            self.exp_loc7_s2 = self.twoside2reverse[p.side4]
            self.exp_loc16_s1 = self.twoside2reverse[p.side3]
            p_nrs = (p.nr1, p.nr2, p.nr3, p.nr4)
            self._make_used(p_nrs)
            self._find_loc64_c3()
            self._make_unused(p_nrs)
        # for

    def _find_loc1_c1(self):
        c = self.bcb1[6:6+3]
        qset = Piece2x2.objects.filter(nr3=c[0], nr1=c[1], nr2=c[2])
        for p in qset:
            self.ring1.nr1 = p.nr
            self.exp_loc2_s4 = self.twoside2reverse[p.side2]
            self.exp_loc9_s1 = self.twoside2reverse[p.side3]
            p_nrs = (p.nr1, p.nr2, p.nr3, p.nr4)
            self._make_used(p_nrs)
            self._find_loc8_c2()
            self._make_unused(p_nrs)
        # for

    def handle(self, *args, **options):

        seed = options['seed']
        self.ring1.seed = seed

        #Ring1.objects.all().delete()

        # print('generate border')
        gen = GenerateBorder(seed)
        sol = gen.get_first_solution()
        print('[INFO] Outer ring = %s' % repr(sol))

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
