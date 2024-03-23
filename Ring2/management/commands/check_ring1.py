# -*- coding: utf-8 -*-

#  Copyright (c) 2024 Ramon van der Winkel.
#  All rights reserved.
#  Licensed under BSD-3-Clause-Clear. See LICENSE file for details.

from django.core.management.base import BaseCommand
from BasePieces.hints import ALL_HINT_NRS
from BasePieces.models import BasePiece
from Pieces2x2.helpers import calc_segment
from Pieces2x2.models import Piece2x2, TwoSide, TwoSideOptions
from Ring1.models import Ring1
from Ring2.models import Ring2
from WorkQueue.models import ProcessorUsedPieces
from WorkQueue.operations import used_note_add
import time


class Command(BaseCommand):

    help = "Check the inner side of a Ring1 (learning)"

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

        # 1..60 = borders + corners
        self.unused = list(range(1, 256+1))
        for nr in ALL_HINT_NRS:
            self.unused.remove(nr)
        # for

        self.used = []
        self.link_sides = False

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

        self.prev_tick = time.monotonic()

    def add_arguments(self, parser):
        # parser.add_argument('ring1_nr', type=int, help='Ring1 to load')
        parser.add_argument('processor', type=int, help='Processor to use')
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

    def _reverse_sides(self, options):
        return [self.twoside2reverse[two_side] for two_side in options]

    def _load_ring1(self, nr, processor):
        self.stdout.write('[INFO] Loading Ring1 %s' % nr)

        try:
            ring1 = Ring1.objects.get(nr=nr)
        except Ring1.DoesNotExist:
            self.stdout.write('[ERROR] Could not locate Ring1')
            return

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

        # get the segment limitations for the inner sides and free-start location
        qset = TwoSideOptions.objects.filter(processor=processor)

        seg = calc_segment(50, 1)
        options = list(qset.filter(segment=seg).values_list('two_side', flat=True))
        self.exp_loc50_sides1 = options

        seg = calc_segment(51, 1)
        options = list(qset.filter(segment=seg).values_list('two_side', flat=True))
        self.exp_loc51_sides1 = options

        seg = calc_segment(51, 4)
        options = list(qset.filter(segment=seg).values_list('two_side', flat=True))
        self.exp_loc51_sides4 = self._reverse_sides(options)

        seg = calc_segment(52, 1)
        options = list(qset.filter(segment=seg).values_list('two_side', flat=True))
        self.exp_loc52_sides1 = options

        seg = calc_segment(52, 4)
        options = list(qset.filter(segment=seg).values_list('two_side', flat=True))
        self.exp_loc52_sides4 = self._reverse_sides(options)

        seg = calc_segment(53, 1)
        options = list(qset.filter(segment=seg).values_list('two_side', flat=True))
        self.exp_loc53_sides1 = options

        seg = calc_segment(53, 4)
        options = list(qset.filter(segment=seg).values_list('two_side', flat=True))
        self.exp_loc53_sides4 = self._reverse_sides(options)

        seg = calc_segment(54, 1)
        options = list(qset.filter(segment=seg).values_list('two_side', flat=True))
        self.exp_loc54_sides1 = options

        seg = calc_segment(54, 4)
        options = list(qset.filter(segment=seg).values_list('two_side', flat=True))
        self.exp_loc54_sides4 = self._reverse_sides(options)

        seg = calc_segment(55, 1)
        options = list(qset.filter(segment=seg).values_list('two_side', flat=True))
        self.exp_loc55_sides1 = options

        seg = calc_segment(10, 2)
        options = list(qset.filter(segment=seg).values_list('two_side', flat=True))
        self.exp_loc10_sides2 = options

        seg = calc_segment(18, 1)
        options = list(qset.filter(segment=seg).values_list('two_side', flat=True))
        self.exp_loc18_sides1 = options

        seg = calc_segment(18, 2)
        options = list(qset.filter(segment=seg).values_list('two_side', flat=True))
        self.exp_loc18_sides2 = options

        seg = calc_segment(26, 1)
        options = list(qset.filter(segment=seg).values_list('two_side', flat=True))
        self.exp_loc26_sides1 = options

        seg = calc_segment(26, 2)
        options = list(qset.filter(segment=seg).values_list('two_side', flat=True))
        self.exp_loc26_sides2 = options

        seg = calc_segment(34, 1)
        options = list(qset.filter(segment=seg).values_list('two_side', flat=True))
        self.exp_loc34_sides1 = options

        seg = calc_segment(34, 2)
        options = list(qset.filter(segment=seg).values_list('two_side', flat=True))
        self.exp_loc34_sides2 = options

        seg = calc_segment(42, 1)
        options = list(qset.filter(segment=seg).values_list('two_side', flat=True))
        self.exp_loc42_sides1 = options

        seg = calc_segment(42, 2)
        options = list(qset.filter(segment=seg).values_list('two_side', flat=True))
        self.exp_loc42_sides2 = options

        seg = calc_segment(50, 2)
        options = list(qset.filter(segment=seg).values_list('two_side', flat=True))
        self.exp_loc50_sides2 = options

        seg = calc_segment(10, 3)
        options = list(qset.filter(segment=seg).values_list('two_side', flat=True))
        self.exp_loc10_sides3 = self._reverse_sides(options)

        seg = calc_segment(11, 2)
        options = list(qset.filter(segment=seg).values_list('two_side', flat=True))
        self.exp_loc11_sides2 = options

        seg = calc_segment(11, 3)
        options = list(qset.filter(segment=seg).values_list('two_side', flat=True))
        self.exp_loc11_sides3 = self._reverse_sides(options)

        seg = calc_segment(12, 2)
        options = list(qset.filter(segment=seg).values_list('two_side', flat=True))
        self.exp_loc12_sides2 = options

        seg = calc_segment(12, 3)
        options = list(qset.filter(segment=seg).values_list('two_side', flat=True))
        self.exp_loc12_sides3 = self._reverse_sides(options)

        seg = calc_segment(13, 2)
        options = list(qset.filter(segment=seg).values_list('two_side', flat=True))
        self.exp_loc13_sides2 = options

        seg = calc_segment(13, 3)
        options = list(qset.filter(segment=seg).values_list('two_side', flat=True))
        self.exp_loc13_sides3 = self._reverse_sides(options)

        seg = calc_segment(14, 2)
        options = list(qset.filter(segment=seg).values_list('two_side', flat=True))
        self.exp_loc14_sides2 = options

        seg = calc_segment(14, 3)
        options = list(qset.filter(segment=seg).values_list('two_side', flat=True))
        self.exp_loc14_sides3 = self._reverse_sides(options)

        seg = calc_segment(15, 3)
        options = list(qset.filter(segment=seg).values_list('two_side', flat=True))
        self.exp_loc15_sides3 = self._reverse_sides(options)

        seg = calc_segment(15, 4)
        options = list(qset.filter(segment=seg).values_list('two_side', flat=True))
        self.exp_loc15_sides4 = self._reverse_sides(options)

        seg = calc_segment(23, 3)
        options = list(qset.filter(segment=seg).values_list('two_side', flat=True))
        self.exp_loc23_sides3 = self._reverse_sides(options)

        seg = calc_segment(23, 4)
        options = list(qset.filter(segment=seg).values_list('two_side', flat=True))
        self.exp_loc23_sides4 = self._reverse_sides(options)

        seg = calc_segment(31, 3)
        options = list(qset.filter(segment=seg).values_list('two_side', flat=True))
        self.exp_loc31_sides3 = self._reverse_sides(options)

        seg = calc_segment(31, 4)
        options = list(qset.filter(segment=seg).values_list('two_side', flat=True))
        self.exp_loc31_sides4 = self._reverse_sides(options)

        seg = calc_segment(39, 3)
        options = list(qset.filter(segment=seg).values_list('two_side', flat=True))
        self.exp_loc39_sides3 = self._reverse_sides(options)

        seg = calc_segment(39, 4)
        options = list(qset.filter(segment=seg).values_list('two_side', flat=True))
        self.exp_loc39_sides4 = self._reverse_sides(options)

        seg = calc_segment(47, 3)
        options = list(qset.filter(segment=seg).values_list('two_side', flat=True))
        self.exp_loc47_sides3 = self._reverse_sides(options)

        seg = calc_segment(47, 4)
        options = list(qset.filter(segment=seg).values_list('two_side', flat=True))
        self.exp_loc47_sides4 = self._reverse_sides(options)

        seg = calc_segment(55, 4)
        options = list(qset.filter(segment=seg).values_list('two_side', flat=True))
        self.exp_loc55_sides4 = self._reverse_sides(options)

    def _check_side4_loc10(self, exp_loc10_s3):
        qset = Piece2x2.objects.filter(has_hint=True,
                                       nr1=208,
                                       nr2__in=self.unused, nr3__in=self.unused, nr4__in=self.unused,
                                       side1=self.exp_loc10_s1, side3=exp_loc10_s3, side4=self.exp_loc10_s4,
                                       side2__in=self.exp_loc10_sides2,)
        return qset.first() is not None

    def _find_side4_loc18(self, exp_loc18_s3):
        found = False
        qset = Piece2x2.objects.filter(has_hint=False,
                                       nr1__in=self.unused, nr2__in=self.unused,
                                       nr3__in=self.unused, nr4__in=self.unused,
                                       side3=exp_loc18_s3, side4=self.exp_loc18_s4,
                                       side1__in=self.exp_loc18_sides1,
                                       side2__in=self.exp_loc18_sides2)
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
                                       side3=exp_loc26_s3, side4=self.exp_loc26_s4,
                                       side1__in=self.exp_loc26_sides1,
                                       side2__in=self.exp_loc26_sides2)
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
                                       side3=exp_loc34_s3, side4=self.exp_loc34_s4,
                                       side1__in=self.exp_loc34_sides1,
                                       side2__in=self.exp_loc34_sides2)
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
                                       side3=exp_loc42_s3, side4=self.exp_loc42_s4,
                                       side1__in=self.exp_loc42_sides1,
                                       side2__in=self.exp_loc42_sides2)
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
                                       side3=self.exp_loc50_s3, side4=self.exp_loc50_s4,
                                       side1__in=self.exp_loc50_sides1, side2__in=self.exp_loc50_sides2)
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
                                       side1=exp_loc55_s1, side2=self.exp_loc55_s2, side3=self.exp_loc55_s3,
                                       side4__in=self.exp_loc55_sides4)
        if not self.link_sides:
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
                                       side1=exp_loc47_s1, side2=self.exp_loc47_s2,
                                       side3__in=self.exp_loc47_sides3,
                                       side4__in=self.exp_loc47_sides4)
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
                                       side1=exp_loc39_s1, side2=self.exp_loc39_s2,
                                       side3__in=self.exp_loc39_sides3,
                                       side4__in=self.exp_loc39_sides4)
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
                                       side1=exp_loc31_s1, side2=self.exp_loc31_s2,
                                       side3__in=self.exp_loc31_sides3,
                                       side4__in=self.exp_loc31_sides4)
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
                                       side1=exp_loc23_s1, side2=self.exp_loc23_s2,
                                       side3__in=self.exp_loc23_sides3,
                                       side4__in=self.exp_loc23_sides4)
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
                                       side1=self.exp_loc15_s1, side2=self.exp_loc15_s2,
                                       side3__in=self.exp_loc15_sides3, side4__in=self.exp_loc15_sides4)
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
                                       side2=exp_loc50_s2, side3=self.exp_loc50_s3, side4=self.exp_loc50_s4,
                                       side1__in=self.exp_loc50_sides1)
        return qset.first() is not None

    def _find_side3_loc51(self, exp_loc51_s2):
        found = False
        qset = Piece2x2.objects.filter(has_hint=False,
                                       nr1__in=self.unused, nr2__in=self.unused,
                                       nr3__in=self.unused, nr4__in=self.unused,
                                       side2=exp_loc51_s2, side3=self.exp_loc51_s3,
                                       side4__in=self.exp_loc51_sides4,
                                       side1__in=self.exp_loc51_sides1)
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
                                       side2=exp_loc52_s2, side3=self.exp_loc52_s3,
                                       side4__in=self.exp_loc52_sides4,
                                       side1__in=self.exp_loc52_sides1)
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
                                       side2=exp_loc53_s2, side3=self.exp_loc53_s3,
                                       side4__in=self.exp_loc53_sides4,
                                       side1__in=self.exp_loc53_sides1)
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
                                       side2=exp_loc54_s2, side3=self.exp_loc54_s3,
                                       side4__in=self.exp_loc54_sides4,
                                       side1__in=self.exp_loc54_sides1)
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
                                       side2=self.exp_loc55_s2, side3=self.exp_loc55_s3,
                                       side1__in=self.exp_loc55_sides1, side4__in=self.exp_loc55_sides4)
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
                                       side1=self.exp_loc15_s1, side2=self.exp_loc15_s2,
                                       side3__in=self.exp_loc15_sides3, side4=exp_loc15_s4)
        if not self.link_sides:
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
                                       side1=self.exp_loc14_s1, side4=exp_loc14_s4,
                                       side2__in=self.exp_loc14_sides2,
                                       side3__in=self.exp_loc14_sides3)
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
                                       side1=self.exp_loc13_s1, side4=exp_loc13_s4,
                                       side2__in=self.exp_loc13_sides2,
                                       side3__in=self.exp_loc13_sides3)
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
                                       side1=self.exp_loc12_s1, side4=exp_loc12_s4,
                                       side2__in=self.exp_loc12_sides2,
                                       side3__in=self.exp_loc12_sides3)
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
                                       side1=self.exp_loc11_s1, side4=exp_loc11_s4,
                                       side2__in=self.exp_loc11_sides2,
                                       side3__in=self.exp_loc11_sides3)
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
                                       side1=self.exp_loc10_s1, side4=self.exp_loc10_s4,
                                       side2__in=self.exp_loc10_sides2, side3__in=self.exp_loc10_sides3)
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

    def _verify_ring1(self):
        self.link_sides = False
        self.stdout.write('[INFO] Checking side 1')
        found = self._find_side1_loc10()  # 10..15
        if found:
            self.stdout.write('[INFO] Checking side 2')
            found = self._find_side2_loc15()  # 15..55
            if found:
                self.stdout.write('[INFO] Checking side 3')
                found = self._find_side3_loc55()  # 55..50
                if found:
                    self.stdout.write('[INFO] Checking side 4')
                    found = self._find_side4_loc50()  # 50..10

        if found:
            self.link_sides = True
            self.stdout.write('[INFO] Checking side 1 + 3')
            found = self._find_side1_loc10()  # 10..15 + 55..50
            if found:
                self.stdout.write('[INFO] Checking side 2 + 4')
                found = self._find_side2_loc15()  # 15..55 + 50..10

        return found

    def handle(self, *args, **options):

        processor_nr = options['processor']
        try:
            processor = ProcessorUsedPieces.objects.get(processor=processor_nr)
        except ProcessorUsedPieces.DoesNotExist:
            self.stderr.write('[ERROR] Could not find processor %s' % processor_nr)
            return

        self._load_ring1(processor.from_ring1, processor_nr)

        try:
            found = self._verify_ring1()
            if not found:
                self.stdout.write('[ERROR] No solution!')
                used_note_add(processor_nr, "Failed check_ring1")
                processor.reached_dead_end = True
                processor.save(update_fields=['reached_dead_end'])
        except KeyboardInterrupt:
            pass

# end of file
