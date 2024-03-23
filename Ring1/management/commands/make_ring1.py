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
from Ring1.can_solve_ring2 import CanSolveRing2


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
                        nr47=0, nr54=0, nr55=0)

        # 1..60 = borders + corners
        self.unused = list(range(1, 256+1))
        for nr in ALL_HINT_NRS:
            self.unused.remove(nr)
        # for

        self.used = []

        self.bcb1 = []
        self.bcb2 = []
        self.bcb3 = []
        self.bcb4 = []

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
        self.bulk = []

        # hint 1
        qset = Piece2x2.objects.filter(nr1=208)
        loc10_s1_set = qset.distinct('side1').values_list('side1', flat=True)
        loc10_s4_set = qset.distinct('side4').values_list('side4', flat=True)
        self.exp_loc2_s3_set = [self.twoside2reverse[side] for side in loc10_s1_set]
        self.exp_loc9_s2_set = [self.twoside2reverse[side] for side in loc10_s4_set]

        # hint 2
        qset = Piece2x2.objects.filter(nr2=255)
        loc15_s1_set = qset.distinct('side1').values_list('side1', flat=True)
        loc15_s2_set = qset.distinct('side2').values_list('side2', flat=True)
        self.exp_loc7_s3_set = [self.twoside2reverse[side] for side in loc15_s1_set]
        self.exp_loc16_s4_set = [self.twoside2reverse[side] for side in loc15_s2_set]

        # hint 3
        qset = Piece2x2.objects.filter(nr4=249)
        loc55_s2_set = qset.distinct('side2').values_list('side2', flat=True)
        loc55_s3_set = qset.distinct('side3').values_list('side3', flat=True)
        self.exp_loc56_s4_set = [self.twoside2reverse[side] for side in loc55_s2_set]
        self.exp_loc63_s1_set = [self.twoside2reverse[side] for side in loc55_s3_set]

        # hint 4
        qset = Piece2x2.objects.filter(nr3=181)
        loc50_s3_set = qset.distinct('side3').values_list('side3', flat=True)
        loc50_s4_set = qset.distinct('side4').values_list('side4', flat=True)
        self.exp_loc58_s1_set = [self.twoside2reverse[side] for side in loc50_s3_set]
        self.exp_loc49_s2_set = [self.twoside2reverse[side] for side in loc50_s4_set]

    def add_arguments(self, parser):
        parser.add_argument('seed', type=int, help='Randomization seed')
        parser.add_argument('--clean', action='store_true')

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

    def _check_loc10_c1(self):
        p = Piece2x2.objects.filter(has_hint=True,
                                    nr1=208,
                                    nr2__in=self.unused, nr3__in=self.unused, nr4__in=self.unused,
                                    side1=self.exp_loc10_s1, side4=self.exp_loc10_s4).first()
        return p is not None

    def _check_loc11_c1(self):
        p = Piece2x2.objects.filter(has_hint=False,
                                    nr1__in=self.unused, nr2__in=self.unused, nr3__in=self.unused, nr4__in=self.unused,
                                    side1=self.exp_loc11_s1, side4=self.exp_loc11_s4).first()
        return p is not None

    def _check_loc18_c1(self):
        p = Piece2x2.objects.filter(has_hint=False,
                                    nr1__in=self.unused, nr2__in=self.unused, nr3__in=self.unused, nr4__in=self.unused,
                                    side1=self.exp_loc18_s1, side4=self.exp_loc18_s4).first()
        return p is not None

    def _check_loc14_c2(self):
        p = Piece2x2.objects.filter(has_hint=False,
                                    nr1__in=self.unused, nr2__in=self.unused, nr3__in=self.unused, nr4__in=self.unused,
                                    side1=self.exp_loc14_s1, side2=self.exp_loc14_s2).first()
        return p is not None

    def _check_loc15_c2(self):
        p = Piece2x2.objects.filter(has_hint=True,
                                    nr2=255,
                                    nr1__in=self.unused, nr3__in=self.unused, nr4__in=self.unused,
                                    side1=self.exp_loc15_s1, side2=self.exp_loc15_s2).first()
        return p is not None

    def _check_loc23_c2(self):
        p = Piece2x2.objects.filter(has_hint=False,
                                    nr1__in=self.unused, nr2__in=self.unused, nr3__in=self.unused, nr4__in=self.unused,
                                    side1=self.exp_loc23_s1, side2=self.exp_loc23_s2).first()
        return p is not None

    def _check_loc47_c3(self):
        p = Piece2x2.objects.filter(has_hint=False,
                                    nr1__in=self.unused, nr2__in=self.unused, nr3__in=self.unused, nr4__in=self.unused,
                                    side2=self.exp_loc47_s2, side3=self.exp_loc47_s3).first()
        return p is not None

    def _check_loc54_c3(self):
        p = Piece2x2.objects.filter(has_hint=False,
                                    nr1__in=self.unused, nr2__in=self.unused, nr3__in=self.unused, nr4__in=self.unused,
                                    side2=self.exp_loc54_s2, side3=self.exp_loc54_s3).first()
        return p is not None

    def _check_loc55_c3(self):
        p = Piece2x2.objects.filter(has_hint=True,
                                    nr4=249,
                                    nr1__in=self.unused, nr2__in=self.unused, nr3__in=self.unused,
                                    side2=self.exp_loc55_s2, side3=self.exp_loc55_s3).first()
        return p is not None

    def _check_loc42_c4(self):
        p = Piece2x2.objects.filter(has_hint=False,
                                    nr1__in=self.unused, nr2__in=self.unused, nr3__in=self.unused, nr4__in=self.unused,
                                    side3=self.exp_loc42_s3, side4=self.exp_loc42_s4).first()
        return p is not None

    def _check_loc50_c4(self):
        p = Piece2x2.objects.filter(has_hint=True,
                                    nr3=181,
                                    nr1__in=self.unused, nr2__in=self.unused, nr4__in=self.unused,
                                    side3=self.exp_loc50_s3, side4=self.exp_loc50_s4).first()
        return p is not None

    def _check_loc51_c4(self):
        p = Piece2x2.objects.filter(has_hint=False,
                                    nr1__in=self.unused, nr2__in=self.unused, nr3__in=self.unused, nr4__in=self.unused,
                                    side3=self.exp_loc51_s3, side4=self.exp_loc51_s4).first()
        return p is not None

    def _count(self):
        self.count += 1
        if self.count > self.count_print:
            print('count = %s' % self.count)
            self.count_print += 100

    def _find_loc55(self):
        found = False
        qset = Piece2x2.objects.filter(has_hint=True,
                                       nr4=249,
                                       nr1__in=self.unused, nr2__in=self.unused, nr3__in=self.unused,
                                       side2=self.exp_loc55_s2, side3=self.exp_loc55_s3)
        for p in qset:
            # self.ring1.nr55 = p.nr
            self.exp_loc47_s3 = self.twoside2reverse[p.side1]
            self.exp_loc54_s2 = self.twoside2reverse[p.side4]
            p_nrs = (p.nr1, p.nr2, p.nr3)
            self._make_used(p_nrs)
            if self._check_loc47_c3() and self._check_loc54_c3():
                if self._check_loc42_c4() and self._check_loc51_c4():   # re-check
                    if self._check_loc14_c2() and self._check_loc23_c2():   # re-check
                        if self._check_loc11_c1() and self._check_loc18_c1():   # re-check
                            solve = CanSolveRing2()
                            if solve.verify(self.ring1):
                                self._save_ring1()
                                found = True
                            else:
                                self.stdout.write('No inner ring solution')
            self._make_unused(p_nrs)
            if found:
                break
        # for
        return found

    def _find_loc50(self):
        found = False
        qset = Piece2x2.objects.filter(has_hint=True,
                                       nr3=181,
                                       nr1__in=self.unused, nr2__in=self.unused, nr4__in=self.unused,
                                       side3=self.exp_loc50_s3, side4=self.exp_loc50_s4)
        for p in qset:
            # self.ring1.nr50 = p.nr
            self.exp_loc42_s3 = self.twoside2reverse[p.side1]
            self.exp_loc51_s4 = self.twoside2reverse[p.side2]
            p_nrs = (p.nr1, p.nr2, p.nr4)
            self._make_used(p_nrs)
            if self._check_loc42_c4() and self._check_loc51_c4():
                if self._check_loc14_c2() and self._check_loc23_c2():       # re-check
                    if self._check_loc11_c1() and self._check_loc18_c1():   # re-check
                        found = self._find_loc55()
            self._make_unused(p_nrs)
            if found:
                break
        # for
        return found

    def _find_loc15(self):
        found = False
        qset = Piece2x2.objects.filter(has_hint=True,
                                       nr2=255,
                                       nr1__in=self.unused, nr3__in=self.unused, nr4__in=self.unused,
                                       side1=self.exp_loc15_s1, side2=self.exp_loc15_s2)
        for p in qset:
            # self.ring1.nr15 = p.nr
            self.exp_loc14_s2 = self.twoside2reverse[p.side4]
            self.exp_loc23_s1 = self.twoside2reverse[p.side3]
            p_nrs = (p.nr1, p.nr3, p.nr4)
            self._make_used(p_nrs)
            if self._check_loc14_c2() and self._check_loc23_c2():
                if self._check_loc11_c1() and self._check_loc18_c1():       # re-check
                    found = self._find_loc50()
            self._make_unused(p_nrs)
            if found:
                break
        # for
        return found

    def _find_loc10(self):
        found = False
        qset = Piece2x2.objects.filter(has_hint=True,
                                       nr1=208,
                                       nr2__in=self.unused, nr3__in=self.unused, nr4__in=self.unused,
                                       side1=self.exp_loc10_s1, side4=self.exp_loc10_s4)
        for p in qset:
            # self.ring1.nr10 = p.nr
            self.exp_loc11_s4 = self.twoside2reverse[p.side2]
            self.exp_loc18_s1 = self.twoside2reverse[p.side3]
            p_nrs = (p.nr2, p.nr3, p.nr4)
            self._make_used(p_nrs)
            if self._check_loc11_c1() and self._check_loc18_c1():
                found = self._find_loc15()
            self._make_unused(p_nrs)
            if found:
                break
        # for
        return found

    def _find_loc41_c4(self):
        b = self.bcb4[11:11+2]
        qset = Piece2x2.objects.filter(nr3=b[0], nr1=b[1],
                                       nr2__in=self.unused, nr4__in=self.unused,
                                       side1=self.exp_loc41_s1, side3=self.exp_loc41_s3)
        for p in qset:
            self.ring1.nr41 = p.nr
            self.exp_loc42_s4 = self.twoside2reverse[p.side2]
            p_nrs = (p.nr1, p.nr2, p.nr3, p.nr4)
            self._make_used(p_nrs)
            self._find_loc10()
            self._make_unused(p_nrs)
        # for

    def _find_loc33_c4(self):
        b = self.bcb4[13:13+2]
        qset = Piece2x2.objects.filter(nr3=b[0], nr1=b[1],
                                       nr2__in=self.unused, nr4__in=self.unused,
                                       side1=self.exp_loc33_s1)
        for p in qset:
            self.ring1.nr33 = p.nr
            self.exp_loc41_s1 = self.twoside2reverse[p.side3]
            p_nrs = (p.nr1, p.nr2, p.nr3, p.nr4)
            self._make_used(p_nrs)
            self._find_loc41_c4()
            self._make_unused(p_nrs)
        # for

    def _find_loc25_c1(self):
        b = self.bcb1[0:0+2]
        qset = Piece2x2.objects.filter(nr3=b[0], nr1=b[1],
                                       nr2__in=self.unused, nr4__in=self.unused,
                                       side1=self.exp_loc25_s1)
        for p in qset:
            self.ring1.nr25 = p.nr
            self.exp_loc33_s1 = self.twoside2reverse[p.side3]
            p_nrs = (p.nr1, p.nr2, p.nr3, p.nr4)
            self._make_used(p_nrs)
            self._find_loc33_c4()
            self._make_unused(p_nrs)
        # for

    def _find_loc17_c1(self):
        b = self.bcb1[2:2+2]
        qset = Piece2x2.objects.filter(nr3=b[0], nr1=b[1],
                                       nr2__in=self.unused, nr4__in=self.unused,
                                       side1=self.exp_loc17_s1)
        for p in qset:
            self.ring1.nr17 = p.nr
            self.exp_loc18_s4 = self.twoside2reverse[p.side2]
            self.exp_loc25_s1 = self.twoside2reverse[p.side3]
            p_nrs = (p.nr1, p.nr2, p.nr3, p.nr4)
            self._make_used(p_nrs)
            self._find_loc25_c1()
            self._make_unused(p_nrs)
        # for

    def _find_loc62_c3(self):
        b = self.bcb3[11:11+2]
        qset = Piece2x2.objects.filter(nr4=b[0], nr3=b[1],
                                       nr2__in=self.unused, nr1__in=self.unused,
                                       side4=self.exp_loc62_s4, side2=self.exp_loc62_s2)
        for p in qset:
            self.ring1.nr62 = p.nr
            self.exp_loc54_s3 = self.twoside2reverse[p.side1]
            p_nrs = (p.nr1, p.nr2, p.nr3, p.nr4)
            self._make_used(p_nrs)
            self._find_loc17_c1()
            self._make_unused(p_nrs)
        # for

    def _find_loc61_c3(self):
        b = self.bcb3[13:13+2]
        qset = Piece2x2.objects.filter(nr4=b[0], nr3=b[1],
                                       nr2__in=self.unused, nr1__in=self.unused,
                                       side4=self.exp_loc61_s4)
        for p in qset:
            self.ring1.nr61 = p.nr
            self.exp_loc62_s4 = self.twoside2reverse[p.side2]
            p_nrs = (p.nr1, p.nr2, p.nr3, p.nr4)
            self._make_used(p_nrs)
            self._find_loc62_c3()
            self._make_unused(p_nrs)
        # for

    def _find_loc60_c4(self):
        b = self.bcb4[0:0+2]
        qset = Piece2x2.objects.filter(nr4=b[0], nr3=b[1],
                                       nr2__in=self.unused, nr1__in=self.unused,
                                       side4=self.exp_loc60_s4)
        for p in qset:
            self.ring1.nr60 = p.nr
            self.exp_loc61_s4 = self.twoside2reverse[p.side2]
            p_nrs = (p.nr1, p.nr2, p.nr3, p.nr4)
            self._make_used(p_nrs)
            self._find_loc61_c3()
            self._make_unused(p_nrs)
        # for

    def _find_loc59_c4(self):
        b = self.bcb4[2:2+2]
        qset = Piece2x2.objects.filter(nr4=b[0], nr3=b[1],
                                       nr2__in=self.unused, nr1__in=self.unused,
                                       side4=self.exp_loc59_s4)
        for p in qset:
            self.ring1.nr59 = p.nr
            self.exp_loc51_s3 = self.twoside2reverse[p.side1]
            self.exp_loc60_s4 = self.twoside2reverse[p.side2]
            p_nrs = (p.nr1, p.nr2, p.nr3, p.nr4)
            self._make_used(p_nrs)
            self._find_loc60_c4()
            self._make_unused(p_nrs)
        # for

    def _find_loc48_c3(self):
        b = self.bcb3[2:2+2]
        qset = Piece2x2.objects.filter(nr2=b[0], nr4=b[1],
                                       nr1__in=self.unused, nr3__in=self.unused,
                                       side1=self.exp_loc48_s1, side3=self.exp_loc48_s3)
        for p in qset:
            self.ring1.nr48 = p.nr
            self.exp_loc47_s2 = self.twoside2reverse[p.side4]
            p_nrs = (p.nr1, p.nr2, p.nr3, p.nr4)
            self._make_used(p_nrs)
            self._find_loc59_c4()
            self._make_unused(p_nrs)
        # for

    def _find_loc40_c3(self):
        b = self.bcb3[0:0+2]
        qset = Piece2x2.objects.filter(nr2=b[0], nr4=b[1],
                                       nr1__in=self.unused, nr3__in=self.unused,
                                       side1=self.exp_loc40_s1)
        for p in qset:
            self.ring1.nr40 = p.nr
            self.exp_loc48_s1 = self.twoside2reverse[p.side3]
            p_nrs = (p.nr1, p.nr2, p.nr3, p.nr4)
            self._make_used(p_nrs)
            self._find_loc48_c3()
            self._make_unused(p_nrs)
        # for

    def _find_loc32_c2(self):
        b = self.bcb2[13:13+2]
        qset = Piece2x2.objects.filter(nr2=b[0], nr4=b[1],
                                       nr1__in=self.unused, nr3__in=self.unused,
                                       side1=self.exp_loc32_s1)
        for p in qset:
            self.ring1.nr32 = p.nr
            self.exp_loc40_s1 = self.twoside2reverse[p.side3]
            p_nrs = (p.nr1, p.nr2, p.nr3, p.nr4)
            self._make_used(p_nrs)
            self._find_loc40_c3()
            self._make_unused(p_nrs)
        # for

    def _find_loc24_c2(self):
        b = self.bcb2[11:11+2]
        qset = Piece2x2.objects.filter(nr2=b[0], nr4=b[1],
                                       nr1__in=self.unused, nr3__in=self.unused,
                                       side1=self.exp_loc24_s1)
        for p in qset:
            self.ring1.nr24 = p.nr
            self.exp_loc23_s2 = self.twoside2reverse[p.side4]
            self.exp_loc32_s1 = self.twoside2reverse[p.side3]
            p_nrs = (p.nr1, p.nr2, p.nr3, p.nr4)
            self._make_used(p_nrs)
            self._find_loc32_c2()
            self._make_unused(p_nrs)
        # for

    def _find_loc6_c2(self):
        b = self.bcb2[2:2+2]
        qset = Piece2x2.objects.filter(nr1=b[0], nr2=b[1],
                                       nr3__in=self.unused, nr4__in=self.unused,
                                       side2=self.exp_loc6_s2, side4=self.exp_loc6_s4)
        for p in qset:
            self.ring1.nr6 = p.nr
            self.exp_loc14_s1 = self.twoside2reverse[p.side3]
            p_nrs = (p.nr1, p.nr2, p.nr3, p.nr4)
            self._make_used(p_nrs)
            self._find_loc24_c2()
            self._make_unused(p_nrs)
        # for

    def _find_loc5_c2(self):
        b = self.bcb2[0:0+2]
        qset = Piece2x2.objects.filter(nr1=b[0], nr2=b[1],
                                       nr3__in=self.unused, nr4__in=self.unused,
                                       side4=self.exp_loc5_s4)
        for p in qset:
            self.ring1.nr5 = p.nr
            self.exp_loc6_s4 = self.twoside2reverse[p.side2]
            p_nrs = (p.nr1, p.nr2, p.nr3, p.nr4)
            self._make_used(p_nrs)
            self._find_loc6_c2()
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

    def _find_loc3_c1(self):
        b = self.bcb1[11:11+2]
        qset = Piece2x2.objects.filter(nr1=b[0], nr2=b[1],
                                       nr3__in=self.unused, nr4__in=self.unused,
                                       side4=self.exp_loc3_s4)
        for p in qset:
            self.ring1.nr3 = p.nr
            self.exp_loc4_s4 = self.twoside2reverse[p.side2]
            self.exp_loc11_s1 = self.twoside2reverse[p.side3]
            p_nrs = (p.nr1, p.nr2, p.nr3, p.nr4)
            self._make_used(p_nrs)
            self._find_loc4_c1()
            self._make_unused(p_nrs)
        # for

    def _find_loc49_c4(self):
        b = self.bcb4[9:9+2]
        qset = Piece2x2.objects.filter(nr3=b[0], nr1=b[1],
                                       nr2__in=self.unused, nr4__in=self.unused,
                                       side3=self.exp_loc49_s3, side2__in=self.exp_loc49_s2_set)
        for p in qset:
            self.ring1.nr49 = p.nr
            self.exp_loc41_s3 = self.twoside2reverse[p.side1]
            self.exp_loc50_s4 = self.twoside2reverse[p.side2]
            p_nrs = (p.nr1, p.nr2, p.nr3, p.nr4)
            self._make_used(p_nrs)
            if self._check_loc50_c4():
                self._find_loc3_c1()
            self._make_unused(p_nrs)
        # for

    def _find_loc58_c4(self):
        b = self.bcb4[4:4+2]
        for p in Piece2x2.objects.filter(nr4=b[0], nr3=b[1],
                                         nr1__in=self.unused, nr2__in=self.unused,
                                         side1__in=self.exp_loc58_s1_set, side4=self.exp_loc58_s4):
            self.ring1.nr58 = p.nr
            self.exp_loc50_s3 = self.twoside2reverse[p.side1]
            self.exp_loc59_s4 = self.twoside2reverse[p.side2]
            p_nrs = (p.nr1, p.nr2, p.nr3, p.nr4)
            self._make_used(p_nrs)
            self._find_loc49_c4()
            self._make_unused(p_nrs)
        # for

    def _find_loc63_c3(self):
        b = self.bcb3[9:9+2]
        for p in Piece2x2.objects.filter(nr4=b[0], nr3=b[1],
                                         nr1__in=self.unused, nr2__in=self.unused,
                                         side1__in=self.exp_loc63_s1_set, side2=self.exp_loc63_s2):
            self.ring1.nr63 = p.nr
            self.exp_loc62_s2 = self.twoside2reverse[p.side4]
            self.exp_loc55_s3 = self.twoside2reverse[p.side1]
            p_nrs = (p.nr1, p.nr2, p.nr3, p.nr4)
            self._make_used(p_nrs)
            if self._check_loc55_c3() and self._check_loc15_c2() and self._check_loc10_c1():
                self._find_loc58_c4()
            self._make_unused(p_nrs)
        # for

    def _find_loc56_c3(self):
        b = self.bcb3[4:4+2]
        for p in Piece2x2.objects.filter(nr2=b[0], nr4=b[1],
                                         nr1__in=self.unused, nr3__in=self.unused,
                                         side3=self.exp_loc56_s3, side4__in=self.exp_loc56_s4_set):
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
                                         side1=self.exp_loc16_s1, side4__in=self.exp_loc16_s4_set):
            self.ring1.nr16 = p.nr
            self.exp_loc15_s2 = self.twoside2reverse[p.side4]
            self.exp_loc24_s1 = self.twoside2reverse[p.side3]
            p_nrs = (p.nr1, p.nr2, p.nr3, p.nr4)
            self._make_used(p_nrs)
            if self._check_loc15_c2() and self._check_loc10_c1():
                self._find_loc56_c3()
            self._make_unused(p_nrs)
        # for

    def _find_loc7_c2(self):
        b = self.bcb2[4:4+2]
        for p in Piece2x2.objects.filter(nr1=b[0], nr2=b[1],
                                         nr3__in=self.unused, nr4__in=self.unused,
                                         side2=self.exp_loc7_s2, side3__in=self.exp_loc7_s3_set):
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
                                       nr2__in=self.unused, nr4__in=self.unused,
                                       side1=self.exp_loc9_s1, side2__in=self.exp_loc9_s2_set)
        for p in qset:
            self.ring1.nr9 = p.nr
            self.exp_loc10_s4 = self.twoside2reverse[p.side2]
            self.exp_loc17_s1 = self.twoside2reverse[p.side3]
            p_nrs = (p.nr1, p.nr2, p.nr3, p.nr4)
            self._make_used(p_nrs)
            if self._check_loc10_c1():
                self._find_loc7_c2()
            self._make_unused(p_nrs)
        # for

    def _find_loc2_c1(self):
        b = self.bcb1[9:9+2]
        qset = Piece2x2.objects.filter(nr1=b[0], nr2=b[1],
                                       nr3__in=self.unused, nr4__in=self.unused,
                                       side4=self.exp_loc2_s4, side3__in=self.exp_loc2_s3_set)
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

    def _find_best(self):
        if self.ring1.nr50 > 0:
            return 23
        if self.ring1.nr55 > 0:
            return 22
        if self.ring1.nr15 > 0:
            return 21
        if self.ring1.nr10 > 0:
            return 20

        if self.ring1.nr49 > 0:
            return 12
        if self.ring1.nr58 > 0:
            return 11

        if self.ring1.nr63 > 0:
            return 10
        if self.ring1.nr56 > 0:
            return 9

        if self.ring1.nr16 > 0:
            return 8
        if self.ring1.nr7 > 0:
            return 7

        if self.ring1.nr9 > 0:
            return 6
        if self.ring1.nr2 > 0:
            return 5

        if self.ring1.nr57 > 0:
            return 4
        if self.ring1.nr64 > 0:
            return 3
        if self.ring1.nr8 > 0:
            return 2
        if self.ring1.nr1 > 0:
            return 1
        return 0

    def handle(self, *args, **options):

        # seg = 178
        # two_sides = TwoSideOptions.objects.filter(processor=1, segment=seg).values_list('two_side', flat=True)
        # bb = list(TwoSide.objects.filter(nr__in=two_sides).values_list('two_sides', flat=True))
        # print('seg%s_set = %s' % (seg, repr(bb)))
        # return

        seed = options['seed']
        self.ring1.seed = seed

        if options['clean']:
            self.stdout.write('[WARNING] Deleting all Ring1')
            Ring1.objects.all().delete()
            return

        # print('generate border')
        gen = GenerateBorder(seed)
        sol = gen.get_first_solution()
        print('[INFO] Outer ring = %s' % repr(sol))

        self.bcb1 = sol[:15]
        self.bcb2 = sol[15:30]
        self.bcb3 = sol[30:45]
        self.bcb4 = sol[45:]
        # print('bcb1: %s' % repr(self.bcb1))
        # print('bcb2: %s' % repr(self.bcb2))
        # print('bcb3: %s' % repr(self.bcb3))
        # print('bcb4: %s' % repr(self.bcb4))

        # for bcb in (self.bcb1, self.bcb2, self.bcb3, self.bcb4):
        #     bcb = bcb[:8] + bcb[7:]     # dupe corner
        #     while len(bcb) > 0:
        #         bb = bcb[:2]
        #         bcb = bcb[2:]
        #         qset = Piece2x2.objects.filter(nr1=bb[0], nr2=bb[1])
        #         print(bb,
        #               qset.count(),
        #               qset.distinct('nr3').count(),
        #               qset.distinct('nr4').count())
        #     # while
        # # for

        # print('[DEBUG] unused=%s' % len(frozenset(self.unused)))

        try:
            self._find_loc1_c1()
        except KeyboardInterrupt:
            pass
        else:
            # print('[DEBUG] unused=%s' % len(frozenset(self.unused)))
            best = self._find_best()
            print('[INFO] Counted: %s; Best: %s' % (self.count, best))

# end of file
