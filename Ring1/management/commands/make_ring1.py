# -*- coding: utf-8 -*-

#  Copyright (c) 2024 Ramon van der Winkel.
#  All rights reserved.
#  Licensed under BSD-3-Clause-Clear. See LICENSE file for details.

from django.core.management.base import BaseCommand
from BasePieces.border import GenerateBorder
from BasePieces.hints import ALL_HINT_NRS
from BasePieces.models import BasePiece
from Pieces2x2.models import Piece2x2, TwoSide, TwoSideOptions
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

        self.used = list()

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

        # hint 1
        seg10_set = ['VB', 'VU', 'VR', 'VG', 'VC', 'VF', 'VN', 'VO', 'VT', 'VH', 'VS', 'VP', 'VD', 'VJ', 'VK', 'VL', 'VV']
        seg10_inv_set = [bb[::-1] for bb in seg10_set]
        self.exp_loc2_s3_set = list(TwoSide.objects.filter(two_sides__in=seg10_inv_set).values_list('nr', flat=True))

        seg138_set = ['SB', 'SU', 'SJ', 'SK', 'SS', 'SD', 'SL', 'SF', 'SR', 'SN', 'SG', 'SC', 'SO', 'ST', 'SH', 'SP', 'SV']
        self.exp_loc9_s2_set = list(TwoSide.objects.filter(two_sides__in=seg138_set).values_list('nr', flat=True))

        # hint 2
        seg15_set = ['CV', 'LV', 'UV', 'FV', 'JV', 'HV', 'NV', 'RV', 'DV', 'GV', 'TV', 'KV', 'VV']
        seg15_inv_set = [bb[::-1] for bb in seg15_set]
        self.exp_loc7_s3_set = list(TwoSide.objects.filter(two_sides__in=seg15_inv_set).values_list('nr', flat=True))

        seg144_set = ['TB', 'TK', 'TS', 'TD', 'TN', 'TF', 'TC', 'TG', 'TJ', 'TT', 'TP', 'TR', 'TU', 'TV', 'TO', 'TH']
        seg144_inv_set = [bb[::-1] for bb in seg144_set]
        self.exp_loc16_s4_set = list(TwoSide.objects.filter(two_sides__in=seg144_inv_set).values_list('nr', flat=True))

        # hint 3
        seg184_set = ['VU', 'JU', 'SU', 'GU', 'CU', 'HU', 'NU', 'LU', 'BU', 'DU', 'FU', 'RU', 'TU', 'PU', 'KU', 'OU']
        seg184_inv_set = [bb[::-1] for bb in seg184_set]
        self.exp_loc56_s4_set = list(TwoSide.objects.filter(two_sides__in=seg184_inv_set).values_list('nr', flat=True))

        seg63_set = ['UO', 'GO', 'RO', 'PO', 'LO', 'HO', 'JO', 'KO', 'BO', 'VO', 'FO', 'OO', 'SO', 'DO', 'NO', 'TO', 'CO']
        self.exp_loc63_s1_set = list(TwoSide.objects.filter(two_sides__in=seg63_set).values_list('nr', flat=True))

        # hint 4
        seg58_set = ['UB', 'UR', 'UN', 'UK', 'UT', 'UV', 'UO', 'UH', 'US', 'UC', 'UF', 'UD', 'UU', 'UJ', 'UP', 'UL']
        self.exp_loc58_s1_set = list(TwoSide.objects.filter(two_sides__in=seg58_set).values_list('nr', flat=True))

        seg178_set = ['CK', 'LK', 'UK', 'FK', 'NK', 'TK', 'DK', 'KK', 'SK', 'OK', 'BK', 'JK', 'RK', 'HK', 'GK', 'VK']
        self.exp_loc49_s2_set = list(TwoSide.objects.filter(two_sides__in=seg178_set).values_list('nr', flat=True))

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

    def _add_hints_and_save(self):
        p = Piece2x2.objects.filter(has_hint=True,
                                    nr1=208,
                                    nr2__in=self.unused, nr3__in=self.unused, nr4__in=self.unused,
                                    side1=self.exp_loc10_s1, side4=self.exp_loc10_s4).first()
        self.ring1.nr10 = p.nr

        p = Piece2x2.objects.filter(has_hint=True,
                                    nr2=255,
                                    nr1__in=self.unused, nr3__in=self.unused, nr4__in=self.unused,
                                    side1=self.exp_loc15_s1, side2=self.exp_loc15_s2).first()
        self.ring1.nr15 = p.nr

        self._save_ring1()

        self.ring1.nr10 = 0
        self.ring1.nr15 = 0

    def _check_loc10_c1(self):
        p = Piece2x2.objects.filter(has_hint=True,
                                    nr1=208,
                                    #nr2__in=self.unused, nr3__in=self.unused, nr4__in=self.unused,
                                    side1=self.exp_loc10_s1, side4=self.exp_loc10_s4).first()
        return p is not None

    def _check_loc15_c2(self):
        p = Piece2x2.objects.filter(has_hint=True,
                                    nr2=255,
                                    #nr1__in=self.unused, nr3__in=self.unused, nr4__in=self.unused,
                                    side1=self.exp_loc15_s1, side2=self.exp_loc15_s2).first()
        return p is not None

    def _check_loc55_c3(self):
        p = Piece2x2.objects.filter(has_hint=True,
                                    nr4=249,
                                    #nr1__in=self.unused, nr2__in=self.unused, nr3__in=self.unused,
                                    side2=self.exp_loc55_s2, side3=self.exp_loc55_s3).first()
        return p is not None

    def _count(self):
        self.count += 1
        if self.count > self.count_print:
            print('count = %s' % self.count)
            self.count_print += 100

    def _find_loc63_c3(self):
        #self._count()
        #self._save_ring1()
        self._add_hints_and_save()
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
                self._add_hints_and_save()
                #self._find_loc63_c3()
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
                                         side1=self.exp_loc16_s1):
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
            # print('loc2: %s' % p.nr)
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
            self.exp_loc63_s2 = self.twoside2reverse[p.side3]
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

        # seg = 178
        # two_sides = TwoSideOptions.objects.filter(processor=1, segment=seg).values_list('two_side', flat=True)
        # bb = list(TwoSide.objects.filter(nr__in=two_sides).values_list('two_sides', flat=True))
        # print('seg%s_set = %s' % (seg, repr(bb)))
        # return

        seed = options['seed']
        self.ring1.seed = seed

        Ring1.objects.all().delete()

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
