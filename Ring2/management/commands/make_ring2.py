# -*- coding: utf-8 -*-

#  Copyright (c) 2024 Ramon van der Winkel.
#  All rights reserved.
#  Licensed under BSD-3-Clause-Clear. See LICENSE file for details.

from django.core.management.base import BaseCommand
from BasePieces.hints import ALL_HINT_NRS
from BasePieces.models import BasePiece
from Pieces2x2.models import Piece2x2, TwoSide
from Ring1.models import Ring1
from Ring2.models import Ring2


class Command(BaseCommand):

    help = "Generate a Ring2, starting with a Ring1"

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

        self.ring2 = Ring2()

        # 1..60 = borders + corners
        self.unused = list(range(1, 256+1))
        for nr in ALL_HINT_NRS:
            self.unused.remove(nr)
        # for

        self.used = []

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
        parser.add_argument('ring1_nr', type=int, help='Ring1 to load')
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

    def _load_ring1(self, nr):
        self.stdout.write('[INFO] Loading Ring1 %s' % nr)

        try:
            ring1 = Ring1.objects.get(nr=nr)
        except Ring1.DoesNotExist:
            self.stdout.write('[ERROR] Could not locate Ring1')
            return

        self.ring2.based_on_ring1 = ring1.nr

        p2x2_nrs = list()
        for loc in (1, 2, 3, 4, 5, 6, 7, 8,
                    9, 16,
                    17, 24,
                    25, 32,
                    33, 40,
                    41, 48,
                    49, 56,
                    57, 58, 59, 60, 61, 62, 63, 64):
            nr_str = 'nr%s' % loc
            p2x2_nr = getattr(ring1, nr_str)
            p2x2_nrs.append(p2x2_nr)

            loc_str = 'loc%s' % loc
            setattr(self.ring2, loc_str, p2x2_nr)
        # for

        # load all p2x2's
        nr2p2x2 = dict()
        for p2x2 in Piece2x2.objects.filter(nr__in=p2x2_nrs):
            # set the p2x2 pieces as used
            nr2p2x2[p2x2.nr] = p2x2
            nrs = [p2x2.nr1, p2x2.nr2, p2x2.nr3, p2x2.nr4]
            self._make_used(nrs)
        # for

        # side 1
        p2x2 = nr2p2x2[self.ring2.loc2]
        self.exp_loc10_s1 = self.twoside2reverse[p2x2.side3]

        p2x2 = nr2p2x2[self.ring2.loc3]
        self.exp_loc11_s1 = self.twoside2reverse[p2x2.side3]

        p2x2 = nr2p2x2[self.ring2.loc4]
        self.exp_loc12_s1 = self.twoside2reverse[p2x2.side3]

        p2x2 = nr2p2x2[self.ring2.loc5]
        self.exp_loc13_s1 = self.twoside2reverse[p2x2.side3]

        p2x2 = nr2p2x2[self.ring2.loc6]
        self.exp_loc14_s1 = self.twoside2reverse[p2x2.side3]

        p2x2 = nr2p2x2[self.ring2.loc7]
        self.exp_loc15_s1 = self.twoside2reverse[p2x2.side3]

        # side 4
        p2x2 = nr2p2x2[self.ring2.loc9]
        self.exp_loc10_s4 = self.twoside2reverse[p2x2.side2]

        p2x2 = nr2p2x2[self.ring2.loc17]
        self.exp_loc18_s4 = self.twoside2reverse[p2x2.side2]

        p2x2 = nr2p2x2[self.ring2.loc25]
        self.exp_loc26_s4 = self.twoside2reverse[p2x2.side2]

        p2x2 = nr2p2x2[self.ring2.loc33]
        self.exp_loc34_s4 = self.twoside2reverse[p2x2.side2]

        p2x2 = nr2p2x2[self.ring2.loc41]
        self.exp_loc42_s4 = self.twoside2reverse[p2x2.side2]

        p2x2 = nr2p2x2[self.ring2.loc49]
        self.exp_loc50_s4 = self.twoside2reverse[p2x2.side2]

        # side 2
        p2x2 = nr2p2x2[self.ring2.loc16]
        self.exp_loc15_s2 = self.twoside2reverse[p2x2.side4]

        p2x2 = nr2p2x2[self.ring2.loc24]
        self.exp_loc23_s2 = self.twoside2reverse[p2x2.side4]

        p2x2 = nr2p2x2[self.ring2.loc32]
        self.exp_loc31_s2 = self.twoside2reverse[p2x2.side4]

        p2x2 = nr2p2x2[self.ring2.loc40]
        self.exp_loc39_s2 = self.twoside2reverse[p2x2.side4]

        p2x2 = nr2p2x2[self.ring2.loc48]
        self.exp_loc47_s2 = self.twoside2reverse[p2x2.side4]

        p2x2 = nr2p2x2[self.ring2.loc56]
        self.exp_loc55_s2 = self.twoside2reverse[p2x2.side4]

        # side 3
        p2x2 = nr2p2x2[self.ring2.loc58]
        self.exp_loc50_s3 = self.twoside2reverse[p2x2.side1]

        p2x2 = nr2p2x2[self.ring2.loc59]
        self.exp_loc51_s3 = self.twoside2reverse[p2x2.side1]

        p2x2 = nr2p2x2[self.ring2.loc60]
        self.exp_loc52_s3 = self.twoside2reverse[p2x2.side1]

        p2x2 = nr2p2x2[self.ring2.loc61]
        self.exp_loc53_s3 = self.twoside2reverse[p2x2.side1]

        p2x2 = nr2p2x2[self.ring2.loc62]
        self.exp_loc54_s3 = self.twoside2reverse[p2x2.side1]

        p2x2 = nr2p2x2[self.ring2.loc63]
        self.exp_loc55_s3 = self.twoside2reverse[p2x2.side1]

    def _save_ring2(self):
        self.ring2.pk = None
        self.ring2.save()
        self.stdout.write('[INFO] Saved Ring2 with pk=%s' % self.ring2.pk)

    def _check_loc46(self):
        p = Piece2x2.objects.filter(has_hint=False,
                                    nr1__in=self.unused, nr2__in=self.unused,
                                    nr3__in=self.unused, nr4__in=self.unused,
                                    side2=self.exp_loc46_s2, side3=self.exp_loc46_s3).first()
        return p is not None

    def _check_loc43(self):
        p = Piece2x2.objects.filter(has_hint=False,
                                    nr1__in=self.unused, nr2__in=self.unused,
                                    nr3__in=self.unused, nr4__in=self.unused,
                                    side3=self.exp_loc43_s3, side4=self.exp_loc43_s4).first()
        return p is not None

    def _check_loc22(self):
        p = Piece2x2.objects.filter(has_hint=False,
                                    nr1__in=self.unused, nr2__in=self.unused,
                                    nr3__in=self.unused, nr4__in=self.unused,
                                    side1=self.exp_loc22_s1, side2=self.exp_loc22_s2).first()
        return p is not None

    def _check_loc19(self):
        p = Piece2x2.objects.filter(has_hint=False,
                                    nr1__in=self.unused, nr2__in=self.unused,
                                    nr3__in=self.unused, nr4__in=self.unused,
                                    side1=self.exp_loc19_s1, side4=self.exp_loc19_s4).first()
        return p is not None

    def _find_loc42(self):
        qset = Piece2x2.objects.filter(has_hint=False,
                                       nr1__in=self.unused, nr2__in=self.unused,
                                       nr3__in=self.unused, nr4__in=self.unused,
                                       side3=self.exp_loc42_s3, side4=self.exp_loc42_s4)
        for p in qset:
            self.ring2.loc42 = p.nr
            self.exp_loc34_s3 = self.twoside2reverse[p.side1]
            self.exp_loc43_s4 = self.twoside2reverse[p.side2]
            p_nrs = (p.nr1, p.nr2, p.nr3)
            self._make_used(p_nrs)
            if self._check_loc43() and self._check_loc46() and self._check_loc22() and self._check_loc19():
                self._save_ring2()
            self._make_unused(p_nrs)
        # for

    def _find_loc51(self):
        qset = Piece2x2.objects.filter(has_hint=False,
                                       nr1__in=self.unused, nr2__in=self.unused,
                                       nr3__in=self.unused, nr4__in=self.unused,
                                       side3=self.exp_loc51_s3, side4=self.exp_loc51_s4)
        for p in qset:
            self.ring2.loc51 = p.nr
            self.exp_loc43_s3 = self.twoside2reverse[p.side1]
            self.exp_loc52_s4 = self.twoside2reverse[p.side2]
            p_nrs = (p.nr1, p.nr2, p.nr3)
            self._make_used(p_nrs)
            self._find_loc42()
            self._make_unused(p_nrs)
        # for

    def _find_loc50(self):
        qset = Piece2x2.objects.filter(has_hint=True,
                                       nr3=181,
                                       nr1__in=self.unused, nr2__in=self.unused, nr4__in=self.unused,
                                       side3=self.exp_loc50_s3, side4=self.exp_loc50_s4)
        for p in qset:
            self.ring2.loc50 = p.nr
            self.exp_loc42_s3 = self.twoside2reverse[p.side1]
            self.exp_loc51_s4 = self.twoside2reverse[p.side2]
            p_nrs = (p.nr1, p.nr2, p.nr4)
            self._make_used(p_nrs)
            self._find_loc51()
            self._make_unused(p_nrs)
        # for

    def _find_loc54(self):
        qset = Piece2x2.objects.filter(has_hint=False,
                                       nr1__in=self.unused, nr2__in=self.unused,
                                       nr3__in=self.unused, nr4__in=self.unused,
                                       side2=self.exp_loc54_s2, side3=self.exp_loc54_s3)
        for p in qset:
            self.ring2.loc54 = p.nr
            self.exp_loc53_s2 = self.twoside2reverse[p.side4]
            self.exp_loc46_s3 = self.twoside2reverse[p.side1]
            p_nrs = (p.nr1, p.nr2, p.nr3)
            self._make_used(p_nrs)
            if self._check_loc46() and self._check_loc22() and self._check_loc19():
                self._find_loc50()
            self._make_unused(p_nrs)
        # for

    def _find_loc47(self):
        qset = Piece2x2.objects.filter(has_hint=False,
                                       nr1__in=self.unused, nr2__in=self.unused,
                                       nr3__in=self.unused, nr4__in=self.unused,
                                       side2=self.exp_loc47_s2, side3=self.exp_loc47_s3)
        for p in qset:
            self.ring2.loc47 = p.nr
            self.exp_loc46_s2 = self.twoside2reverse[p.side4]
            self.exp_loc39_s3 = self.twoside2reverse[p.side1]
            p_nrs = (p.nr1, p.nr2, p.nr3)
            self._make_used(p_nrs)
            self._find_loc54()
            self._make_unused(p_nrs)
        # for

    def _find_loc55(self):
        qset = Piece2x2.objects.filter(has_hint=True,
                                       nr4=249,
                                       nr1__in=self.unused, nr2__in=self.unused, nr3__in=self.unused,
                                       side2=self.exp_loc55_s2, side3=self.exp_loc55_s3)
        for p in qset:
            self.ring2.loc55 = p.nr
            self.exp_loc47_s3 = self.twoside2reverse[p.side1]
            self.exp_loc54_s2 = self.twoside2reverse[p.side4]
            p_nrs = (p.nr1, p.nr2, p.nr3)
            self._make_used(p_nrs)
            self._find_loc47()
            self._make_unused(p_nrs)
        # for

    def _find_loc23(self):
        qset = Piece2x2.objects.filter(has_hint=False,
                                       nr1__in=self.unused, nr2__in=self.unused,
                                       nr3__in=self.unused, nr4__in=self.unused,
                                       side1=self.exp_loc23_s1, side2=self.exp_loc23_s2)
        for p in qset:
            self.ring2.loc23 = p.nr
            self.exp_loc22_s2 = self.twoside2reverse[p.side4]
            self.exp_loc31_s1 = self.twoside2reverse[p.side3]
            p_nrs = (p.nr1, p.nr2, p.nr3)
            self._make_used(p_nrs)
            if self._check_loc22() and self._check_loc19():
                self._find_loc55()
            self._make_unused(p_nrs)
        # for

    def _find_loc14(self):
        qset = Piece2x2.objects.filter(has_hint=False,
                                       nr1__in=self.unused, nr2__in=self.unused,
                                       nr3__in=self.unused, nr4__in=self.unused,
                                       side1=self.exp_loc14_s1, side2=self.exp_loc14_s2)
        for p in qset:
            self.ring2.loc14 = p.nr
            self.exp_loc22_s1 = self.twoside2reverse[p.side3]
            self.exp_loc13_s2 = self.twoside2reverse[p.side4]
            p_nrs = (p.nr1, p.nr2, p.nr3)
            self._make_used(p_nrs)
            self._find_loc23()
            self._make_unused(p_nrs)
        # for

    def _find_loc15(self):
        qset = Piece2x2.objects.filter(has_hint=True,
                                       nr2=255,
                                       nr1__in=self.unused, nr3__in=self.unused, nr4__in=self.unused,
                                       side1=self.exp_loc15_s1, side2=self.exp_loc15_s2)
        for p in qset:
            self.ring2.loc15 = p.nr
            self.exp_loc14_s2 = self.twoside2reverse[p.side4]
            self.exp_loc23_s1 = self.twoside2reverse[p.side3]
            p_nrs = (p.nr1, p.nr3, p.nr4)
            self._make_used(p_nrs)
            self._find_loc14()
            self._make_unused(p_nrs)
        # for

    def _find_loc11(self):
        qset = Piece2x2.objects.filter(has_hint=False,
                                       nr1__in=self.unused, nr2__in=self.unused,
                                       nr3__in=self.unused, nr4__in=self.unused,
                                       side1=self.exp_loc11_s1, side4=self.exp_loc11_s4)
        for p in qset:
            self.ring2.loc11 = p.nr
            self.exp_loc19_s1 = self.twoside2reverse[p.side3]
            self.exp_loc12_s4 = self.twoside2reverse[p.side2]
            p_nrs = (p.nr1, p.nr2, p.nr3)
            self._make_used(p_nrs)
            if self._check_loc19():
                self._find_loc15()
            self._make_unused(p_nrs)
        # for

    def _find_loc18(self):
        qset = Piece2x2.objects.filter(has_hint=False,
                                       nr1__in=self.unused, nr2__in=self.unused,
                                       nr3__in=self.unused, nr4__in=self.unused,
                                       side1=self.exp_loc18_s1, side4=self.exp_loc18_s4)
        for p in qset:
            self.ring2.loc18 = p.nr
            self.exp_loc26_s1 = self.twoside2reverse[p.side3]
            self.exp_loc19_s4 = self.twoside2reverse[p.side2]
            p_nrs = (p.nr1, p.nr2, p.nr3)
            self._make_used(p_nrs)
            self._find_loc11()
            self._make_unused(p_nrs)
        # for

    def _find_loc10(self):
        qset = Piece2x2.objects.filter(has_hint=True,
                                       nr1=208,
                                       nr2__in=self.unused, nr3__in=self.unused, nr4__in=self.unused,
                                       side1=self.exp_loc10_s1, side4=self.exp_loc10_s4)
        for p in qset:
            self.ring2.loc10 = p.nr
            self.exp_loc11_s4 = self.twoside2reverse[p.side2]
            self.exp_loc18_s1 = self.twoside2reverse[p.side3]
            p_nrs = (p.nr2, p.nr3, p.nr4)
            self._make_used(p_nrs)
            self._find_loc18()
            self._make_unused(p_nrs)
        # for

    def _find_best(self):
        # if self.ring2.loc50 > 0:
        #     return 23
        # if self.ring2.loc55 > 0:
        #     return 22
        # if self.ring2.loc15 > 0:
        #     return 21
        # if self.ring2.loc10 > 0:
        #     return 20

        if self.ring2.loc42 > 0:
            return 12
        if self.ring2.loc51 > 0:
            return 11
        if self.ring2.loc50 > 0:
            return 10

        if self.ring2.loc54 > 0:
            return 9
        if self.ring2.loc47 > 0:
            return 8
        if self.ring2.loc55 > 0:
            return 7

        if self.ring2.loc23 > 0:
            return 6
        if self.ring2.loc14 > 0:
            return 5
        if self.ring2.loc15 > 0:
            return 4

        if self.ring2.loc11 > 0:
            return 3
        if self.ring2.loc18 > 0:
            return 2
        if self.ring2.loc10 > 0:
            return 1
        return 0

    def handle(self, *args, **options):

        if options['clean']:
            self.stdout.write('[WARNING] Deleting all Ring2')
            Ring2.objects.all().delete()
            return

        ring1_nr = options['ring1_nr']
        self._load_ring1(ring1_nr)

        #print('[DEBUG] count unused=%s' % len(frozenset(self.unused)))

        try:
            self._find_loc10()
        except KeyboardInterrupt:
            pass
        else:
            # print('[DEBUG] unused=%s' % len(frozenset(self.unused)))
            best = self._find_best()
            print('[INFO] Counted: %s; Best: %s' % (self.count, best))

# end of file
