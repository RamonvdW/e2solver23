# -*- coding: utf-8 -*-

#  Copyright (c) 2024 Ramon van der Winkel.
#  All rights reserved.
#  Licensed under BSD-3-Clause-Clear. See LICENSE file for details.

from BasePieces.hints import ALL_HINT_NRS
from Pieces2x2.helpers import calc_segment
from Pieces2x2.models import Piece2x2, TwoSide, TwoSideOptions
from Ring1.models import Ring1
from Ring2.models import Ring2


class CanSolveRing2(object):

    """ Additional checks of a candidate Ring1

        Verify the inner sides of the Ring1 to make sure we can make a Ring2 with the remaining pieces
    """

    def __init__(self):

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
        # 1..60 = borders + corners
        self.unused = list(range(1, 256+1))
        for nr in ALL_HINT_NRS:
            self.unused.remove(nr)
        # for

        self._link_sides = False

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

    def _make_used(self, p_nrs: tuple | list):
        for nr in p_nrs:
            self.unused.remove(nr)
        # for

    def _make_unused(self, p_nrs: tuple | list):
        self.unused.extend(p_nrs)

    def _reverse_sides(self, options):
        return [self.twoside2reverse[two_side] for two_side in options]

    def _load_ring1(self, ring1):
        ring2 = Ring2()
        # ring2.based_on_ring1 = ring1.nr

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
            setattr(ring2, loc_str, p2x2_nr)
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
        p2x2 = nr2p2x2[ring2.loc2]
        self.exp_loc10_s1 = self.twoside2reverse[p2x2.side3]

        p2x2 = nr2p2x2[ring2.loc3]
        self.exp_loc11_s1 = self.twoside2reverse[p2x2.side3]

        p2x2 = nr2p2x2[ring2.loc4]
        self.exp_loc12_s1 = self.twoside2reverse[p2x2.side3]

        p2x2 = nr2p2x2[ring2.loc5]
        self.exp_loc13_s1 = self.twoside2reverse[p2x2.side3]

        p2x2 = nr2p2x2[ring2.loc6]
        self.exp_loc14_s1 = self.twoside2reverse[p2x2.side3]

        p2x2 = nr2p2x2[ring2.loc7]
        self.exp_loc15_s1 = self.twoside2reverse[p2x2.side3]

        # side 4
        p2x2 = nr2p2x2[ring2.loc9]
        self.exp_loc10_s4 = self.twoside2reverse[p2x2.side2]

        p2x2 = nr2p2x2[ring2.loc17]
        self.exp_loc18_s4 = self.twoside2reverse[p2x2.side2]

        p2x2 = nr2p2x2[ring2.loc25]
        self.exp_loc26_s4 = self.twoside2reverse[p2x2.side2]

        p2x2 = nr2p2x2[ring2.loc33]
        self.exp_loc34_s4 = self.twoside2reverse[p2x2.side2]

        p2x2 = nr2p2x2[ring2.loc41]
        self.exp_loc42_s4 = self.twoside2reverse[p2x2.side2]

        p2x2 = nr2p2x2[ring2.loc49]
        self.exp_loc50_s4 = self.twoside2reverse[p2x2.side2]

        # side 2
        p2x2 = nr2p2x2[ring2.loc16]
        self.exp_loc15_s2 = self.twoside2reverse[p2x2.side4]

        p2x2 = nr2p2x2[ring2.loc24]
        self.exp_loc23_s2 = self.twoside2reverse[p2x2.side4]

        p2x2 = nr2p2x2[ring2.loc32]
        self.exp_loc31_s2 = self.twoside2reverse[p2x2.side4]

        p2x2 = nr2p2x2[ring2.loc40]
        self.exp_loc39_s2 = self.twoside2reverse[p2x2.side4]

        p2x2 = nr2p2x2[ring2.loc48]
        self.exp_loc47_s2 = self.twoside2reverse[p2x2.side4]

        p2x2 = nr2p2x2[ring2.loc56]
        self.exp_loc55_s2 = self.twoside2reverse[p2x2.side4]

        # side 3
        p2x2 = nr2p2x2[ring2.loc58]
        self.exp_loc50_s3 = self.twoside2reverse[p2x2.side1]

        p2x2 = nr2p2x2[ring2.loc59]
        self.exp_loc51_s3 = self.twoside2reverse[p2x2.side1]

        p2x2 = nr2p2x2[ring2.loc60]
        self.exp_loc52_s3 = self.twoside2reverse[p2x2.side1]

        p2x2 = nr2p2x2[ring2.loc61]
        self.exp_loc53_s3 = self.twoside2reverse[p2x2.side1]

        p2x2 = nr2p2x2[ring2.loc62]
        self.exp_loc54_s3 = self.twoside2reverse[p2x2.side1]

        p2x2 = nr2p2x2[ring2.loc63]
        self.exp_loc55_s3 = self.twoside2reverse[p2x2.side1]

    def _check_side4_loc10(self, exp_loc10_s3):
        qset = Piece2x2.objects.filter(has_hint=True,
                                       nr1=208,
                                       nr2__in=self.unused, nr3__in=self.unused, nr4__in=self.unused,
                                       side1=self.exp_loc10_s1, side3=exp_loc10_s3, side4=self.exp_loc10_s4)
        return qset.first() is not None

    def _find_side4_loc18(self, exp_loc18_s3):
        found = False
        qset = Piece2x2.objects.filter(has_hint=False,
                                       nr1__in=self.unused, nr2__in=self.unused,
                                       nr3__in=self.unused, nr4__in=self.unused,
                                       side3=exp_loc18_s3, side4=self.exp_loc18_s4)
        for p in qset:
            exp_loc10_s3 = self.twoside2reverse[p.side1]
            p_nrs = (p.nr1, p.nr2, p.nr3, p.nr4)
            self._make_used(p_nrs)
            found = self._check_side4_loc10(exp_loc10_s3)
            self._make_unused(p_nrs)
            if found:
                break
        # for
        return found

    def _find_side4_loc26(self, exp_loc26_s3):
        found = False
        qset = Piece2x2.objects.filter(has_hint=False,
                                       nr1__in=self.unused, nr2__in=self.unused,
                                       nr3__in=self.unused, nr4__in=self.unused,
                                       side3=exp_loc26_s3, side4=self.exp_loc26_s4)
        for p in qset:
            exp_loc18_s3 = self.twoside2reverse[p.side1]
            p_nrs = (p.nr1, p.nr2, p.nr3, p.nr4)
            self._make_used(p_nrs)
            found = self._find_side4_loc18(exp_loc18_s3)
            self._make_unused(p_nrs)
            if found:
                break
        # for
        return found

    def _find_side4_loc34(self, exp_loc34_s3):
        found = False
        qset = Piece2x2.objects.filter(has_hint=False,
                                       nr1__in=self.unused, nr2__in=self.unused,
                                       nr3__in=self.unused, nr4__in=self.unused,
                                       side3=exp_loc34_s3, side4=self.exp_loc34_s4)
        for p in qset:
            exp_loc26_s3 = self.twoside2reverse[p.side1]
            p_nrs = (p.nr1, p.nr2, p.nr3, p.nr4)
            self._make_used(p_nrs)
            found = self._find_side4_loc26(exp_loc26_s3)
            self._make_unused(p_nrs)
            if found:
                break
        # for
        return found

    def _find_side4_loc42(self, exp_loc42_s3):
        found = False
        qset = Piece2x2.objects.filter(has_hint=False,
                                       nr1__in=self.unused, nr2__in=self.unused,
                                       nr3__in=self.unused, nr4__in=self.unused,
                                       side3=exp_loc42_s3, side4=self.exp_loc42_s4)
        for p in qset:
            exp_loc34_s3 = self.twoside2reverse[p.side1]
            p_nrs = (p.nr1, p.nr2, p.nr3, p.nr4)
            self._make_used(p_nrs)
            found = self._find_side4_loc34(exp_loc34_s3)
            self._make_unused(p_nrs)
            if found:
                break
        # for
        return found

    def _find_side4_loc50(self):
        found = False
        qset = Piece2x2.objects.filter(has_hint=True,
                                       nr3=181,
                                       nr1__in=self.unused, nr2__in=self.unused, nr4__in=self.unused,
                                       side3=self.exp_loc50_s3, side4=self.exp_loc50_s4)
        for p in qset:
            exp_loc42_s3 = self.twoside2reverse[p.side1]
            p_nrs = (p.nr1, p.nr2, p.nr4)
            self._make_used(p_nrs)
            found = self._find_side4_loc42(exp_loc42_s3)
            self._make_unused(p_nrs)
            if found:
                break
        # for
        return found

    #####################################################################################

    def _find_side2_loc55(self, exp_loc55_s1):
        found = False
        qset = Piece2x2.objects.filter(has_hint=True,
                                       nr4=249,
                                       nr1__in=self.unused, nr2__in=self.unused, nr3__in=self.unused,
                                       side1=exp_loc55_s1, side2=self.exp_loc55_s2, side3=self.exp_loc55_s3)
        if not self._link_sides:
            return qset.first() is not None
        for p in qset:
            p_nrs = (p.nr1, p.nr2, p.nr3)
            self._make_used(p_nrs)
            found = self._find_side4_loc50()
            self._make_unused(p_nrs)
            if found:
                break
        # for
        return found

    def _find_side2_loc47(self, exp_loc47_s1):
        found = False
        qset = Piece2x2.objects.filter(has_hint=False,
                                       nr1__in=self.unused, nr2__in=self.unused,
                                       nr3__in=self.unused, nr4__in=self.unused,
                                       side1=exp_loc47_s1, side2=self.exp_loc47_s2)
        for p in qset:
            exp_loc55_s1 = self.twoside2reverse[p.side3]
            p_nrs = (p.nr1, p.nr2, p.nr3, p.nr4)
            self._make_used(p_nrs)
            found = self._find_side2_loc55(exp_loc55_s1)
            self._make_unused(p_nrs)
            if found:
                break
        # for
        return found

    def _find_side2_loc39(self, exp_loc39_s1):
        found = False
        qset = Piece2x2.objects.filter(has_hint=False,
                                       nr1__in=self.unused, nr2__in=self.unused,
                                       nr3__in=self.unused, nr4__in=self.unused,
                                       side1=exp_loc39_s1, side2=self.exp_loc39_s2)
        for p in qset:
            exp_loc47_s1 = self.twoside2reverse[p.side3]
            p_nrs = (p.nr1, p.nr2, p.nr3, p.nr4)
            self._make_used(p_nrs)
            found = self._find_side2_loc47(exp_loc47_s1)
            self._make_unused(p_nrs)
            if found:
                break
        # for
        return found

    def _find_side2_loc31(self, exp_loc31_s1):
        found = False
        qset = Piece2x2.objects.filter(has_hint=False,
                                       nr1__in=self.unused, nr2__in=self.unused,
                                       nr3__in=self.unused, nr4__in=self.unused,
                                       side1=exp_loc31_s1, side2=self.exp_loc31_s2)
        for p in qset:
            exp_loc39_s1 = self.twoside2reverse[p.side3]
            p_nrs = (p.nr1, p.nr2, p.nr3, p.nr4)
            self._make_used(p_nrs)
            found = self._find_side2_loc39(exp_loc39_s1)
            self._make_unused(p_nrs)
            if found:
                break
        # for
        return found

    def _find_side2_loc23(self, exp_loc23_s1):
        found = False
        qset = Piece2x2.objects.filter(has_hint=False,
                                       nr1__in=self.unused, nr2__in=self.unused,
                                       nr3__in=self.unused, nr4__in=self.unused,
                                       side1=exp_loc23_s1, side2=self.exp_loc23_s2)
        for p in qset:
            exp_loc31_s1 = self.twoside2reverse[p.side3]
            p_nrs = (p.nr1, p.nr2, p.nr3, p.nr4)
            self._make_used(p_nrs)
            found = self._find_side2_loc31(exp_loc31_s1)
            self._make_unused(p_nrs)
            if found:
                break
        # for
        return found

    def _find_side2_loc15(self):
        found = False
        qset = Piece2x2.objects.filter(has_hint=True,
                                       nr2=255,
                                       nr1__in=self.unused, nr3__in=self.unused, nr4__in=self.unused,
                                       side1=self.exp_loc15_s1, side2=self.exp_loc15_s2)
        for p in qset:
            exp_loc23_s1 = self.twoside2reverse[p.side3]
            p_nrs = (p.nr1, p.nr3, p.nr4)
            self._make_used(p_nrs)
            found = self._find_side2_loc23(exp_loc23_s1)
            self._make_unused(p_nrs)
            if found:
                break
        # for
        return found

    #####################################################################################

    def _check_side3_loc50(self, exp_loc50_s2):
        qset = Piece2x2.objects.filter(has_hint=True,
                                       nr3=181,
                                       nr1__in=self.unused, nr2__in=self.unused, nr4__in=self.unused,
                                       side2=exp_loc50_s2, side3=self.exp_loc50_s3, side4=self.exp_loc50_s4)
        return qset.first() is not None

    def _find_side3_loc51(self, exp_loc51_s2):
        found = False
        qset = Piece2x2.objects.filter(has_hint=False,
                                       nr1__in=self.unused, nr2__in=self.unused,
                                       nr3__in=self.unused, nr4__in=self.unused,
                                       side2=exp_loc51_s2, side3=self.exp_loc51_s3)
        for p in qset:
            exp_loc50_s2 = self.twoside2reverse[p.side4]
            p_nrs = (p.nr1, p.nr2, p.nr3, p.nr4)
            self._make_used(p_nrs)
            found = self._check_side3_loc50(exp_loc50_s2)
            self._make_unused(p_nrs)
            if found:
                break
        # for
        return found

    def _find_side3_loc52(self, exp_loc52_s2):
        found = False
        qset = Piece2x2.objects.filter(has_hint=False,
                                       nr1__in=self.unused, nr2__in=self.unused,
                                       nr3__in=self.unused, nr4__in=self.unused,
                                       side2=exp_loc52_s2, side3=self.exp_loc52_s3)
        for p in qset:
            exp_loc51_s2 = self.twoside2reverse[p.side4]
            p_nrs = (p.nr1, p.nr2, p.nr3, p.nr4)
            self._make_used(p_nrs)
            found = self._find_side3_loc51(exp_loc51_s2)
            self._make_unused(p_nrs)
            if found:
                break
        # for
        return found

    def _find_side3_loc53(self, exp_loc53_s2):
        found = False
        qset = Piece2x2.objects.filter(has_hint=False,
                                       nr1__in=self.unused, nr2__in=self.unused,
                                       nr3__in=self.unused, nr4__in=self.unused,
                                       side2=exp_loc53_s2, side3=self.exp_loc53_s3)
        for p in qset:
            exp_loc52_s2 = self.twoside2reverse[p.side4]
            p_nrs = (p.nr1, p.nr2, p.nr3, p.nr4)
            self._make_used(p_nrs)
            found = self._find_side3_loc52(exp_loc52_s2)
            self._make_unused(p_nrs)
            if found:
                break
        # for
        return found

    def _find_side3_loc54(self, exp_loc54_s2):
        found = False
        qset = Piece2x2.objects.filter(has_hint=False,
                                       nr1__in=self.unused, nr2__in=self.unused,
                                       nr3__in=self.unused, nr4__in=self.unused,
                                       side2=exp_loc54_s2, side3=self.exp_loc54_s3)
        for p in qset:
            exp_loc53_s2 = self.twoside2reverse[p.side4]
            p_nrs = (p.nr1, p.nr2, p.nr3, p.nr4)
            self._make_used(p_nrs)
            found = self._find_side3_loc53(exp_loc53_s2)
            self._make_unused(p_nrs)
            if found:
                break
        # for
        return found

    def _find_side3_loc55(self):
        found = False
        qset = Piece2x2.objects.filter(has_hint=True,
                                       nr4=249,
                                       nr1__in=self.unused, nr2__in=self.unused, nr3__in=self.unused,
                                       side2=self.exp_loc55_s2, side3=self.exp_loc55_s3)
        for p in qset:
            exp_loc54_s2 = self.twoside2reverse[p.side4]
            p_nrs = (p.nr1, p.nr2, p.nr3)
            self._make_used(p_nrs)
            found = self._find_side3_loc54(exp_loc54_s2)
            self._make_unused(p_nrs)
            if found:
                break
        # for
        return found

    #####################################################################################

    def _find_side1_loc15(self, exp_loc15_s4):
        found = False
        qset = Piece2x2.objects.filter(has_hint=True,
                                       nr2=255,
                                       nr1__in=self.unused, nr3__in=self.unused, nr4__in=self.unused,
                                       side1=self.exp_loc15_s1, side2=self.exp_loc15_s2, side4=exp_loc15_s4)
        if not self._link_sides:
            return qset.first() is not None
        for p in qset:
            p_nrs = (p.nr1, p.nr3, p.nr4)
            self._make_used(p_nrs)
            found = self._find_side3_loc55()
            self._make_unused(p_nrs)
            if found:
                break
        # for
        return found

    def _find_side1_loc14(self, exp_loc14_s4):
        found = False
        qset = Piece2x2.objects.filter(has_hint=False,
                                       nr1__in=self.unused, nr2__in=self.unused,
                                       nr3__in=self.unused, nr4__in=self.unused,
                                       side1=self.exp_loc14_s1, side4=exp_loc14_s4)
        for p in qset:
            exp_loc15_s4 = self.twoside2reverse[p.side2]
            p_nrs = (p.nr1, p.nr2, p.nr3, p.nr4)
            self._make_used(p_nrs)
            found = self._find_side1_loc15(exp_loc15_s4)
            self._make_unused(p_nrs)
            if found:
                break
        # for
        return found

    def _find_side1_loc13(self, exp_loc13_s4):
        found = False
        qset = Piece2x2.objects.filter(has_hint=False,
                                       nr1__in=self.unused, nr2__in=self.unused,
                                       nr3__in=self.unused, nr4__in=self.unused,
                                       side1=self.exp_loc13_s1, side4=exp_loc13_s4)
        for p in qset:
            exp_loc14_s4 = self.twoside2reverse[p.side2]
            p_nrs = (p.nr1, p.nr2, p.nr3, p.nr4)
            self._make_used(p_nrs)
            found = self._find_side1_loc14(exp_loc14_s4)
            self._make_unused(p_nrs)
            if found:
                break
        # for
        return found

    def _find_side1_loc12(self, exp_loc12_s4):
        found = False
        qset = Piece2x2.objects.filter(has_hint=False,
                                       nr1__in=self.unused, nr2__in=self.unused,
                                       nr3__in=self.unused, nr4__in=self.unused,
                                       side1=self.exp_loc12_s1, side4=exp_loc12_s4)
        for p in qset:
            exp_loc13_s4 = self.twoside2reverse[p.side2]
            p_nrs = (p.nr1, p.nr2, p.nr3, p.nr4)
            self._make_used(p_nrs)
            found = self._find_side1_loc13(exp_loc13_s4)
            self._make_unused(p_nrs)
            if found:
                break
        # for
        return found

    def _find_side1_loc11(self, exp_loc11_s4):
        found = False
        qset = Piece2x2.objects.filter(has_hint=False,
                                       nr1__in=self.unused, nr2__in=self.unused,
                                       nr3__in=self.unused, nr4__in=self.unused,
                                       side1=self.exp_loc11_s1, side4=exp_loc11_s4)
        for p in qset:
            exp_loc12_s4 = self.twoside2reverse[p.side2]
            p_nrs = (p.nr1, p.nr2, p.nr3, p.nr4)
            self._make_used(p_nrs)
            found = self._find_side1_loc12(exp_loc12_s4)
            self._make_unused(p_nrs)
            if found:
                break
        # for
        return found

    def _find_side1_loc10(self):
        found = False
        qset = Piece2x2.objects.filter(has_hint=True,
                                       nr1=208,
                                       nr2__in=self.unused, nr3__in=self.unused, nr4__in=self.unused,
                                       side1=self.exp_loc10_s1, side4=self.exp_loc10_s4)
        for p in qset:
            exp_loc11_s4 = self.twoside2reverse[p.side2]
            p_nrs = (p.nr2, p.nr3, p.nr4)
            self._make_used(p_nrs)
            found = self._find_side1_loc11(exp_loc11_s4)
            self._make_unused(p_nrs)
            if found:
                break
        # for
        return found

    def verify(self, ring1):
        self._load_ring1(ring1)

        self._link_sides = False
        found = self._find_side1_loc10()  # 10..15
        if found:
            found = self._find_side2_loc15()  # 15..55
            if found:
                found = self._find_side3_loc55()  # 55..50
                if found:
                    found = self._find_side4_loc50()  # 50..10

        if found:
            self._link_sides = True
            found = self._find_side1_loc10()  # 10..15 + 55..50
            if found:
                found = self._find_side2_loc15()  # 15..55 + 50..10

        return found

# end of file
