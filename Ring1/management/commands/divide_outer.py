# -*- coding: utf-8 -*-

#  Copyright (c) 2024 Ramon van der Winkel.
#  All rights reserved.
#  Licensed under BSD-3-Clause-Clear. See LICENSE file for details.

from django.core.management.base import BaseCommand
from BasePieces.border import GenerateBorder
from BasePieces.models import BasePiece
from Pieces2x2.models import Piece2x2, TwoSide


class Command(BaseCommand):

    help = "Generate solutions for the outer border ring"

    def add_arguments(self, parser):
        parser.add_argument('seed', type=int, help='Randomization seed')

    @staticmethod
    def _needs_c4():
        c4s = list()
        zs = {1: [], 2: [], 3: [], 4: []}

        twoside_border = TwoSide.objects.get(two_sides='XX').nr

        two2nr = dict()
        side2two = dict()     # [two side nr] = two_sides
        for two in TwoSide.objects.all():
            two2nr[two.two_sides] = two.nr
            side2two[two.nr] = two.two_sides
        # for

        twoside2reverse = dict()
        for two_sides, nr in two2nr.items():
            two_rev = two_sides[1] + two_sides[0]
            rev_nr = two2nr[two_rev]
            twoside2reverse[nr] = rev_nr
        # for

        nr2base = dict()
        for p1x1 in BasePiece.objects.all():
            nr2base[p1x1.nr] = p1x1
        # for

        unused = list(range(1, 256+1))
        unused.remove(139)
        unused.remove(181)
        unused.remove(208)
        unused.remove(249)
        unused.remove(255)

        # loc 50
        qset = (Piece2x2
                .objects
                .filter(is_border=False,
                        has_hint=True,
                        nr3=181,
                        nr1__in=unused, nr2__in=unused, nr4__in=unused))
        loc50_sides4 = list(qset.distinct('side4').values_list('side4', flat=True))
        loc50_sides3 = list(qset.distinct('side3').values_list('side3', flat=True))

        todo = len(loc50_sides3)
        for loc50_side3 in loc50_sides3:
            print('todo: %s' % todo)
            todo -= 1
            loc58_exp_s1 = twoside2reverse[loc50_side3]

            for loc50_side4 in loc50_sides4:
                loc49_exp_s2 = twoside2reverse[loc50_side4]

                # loc 49
                exp_s4 = twoside_border
                qset = (Piece2x2
                        .objects
                        .filter(is_border=True,
                                side2=loc49_exp_s2, side4=exp_s4,
                                nr1__in=unused, nr2__in=unused, nr3__in=unused, nr4__in=unused)
                        .exclude(side3=twoside_border)
                        .exclude(side1=twoside_border))
                for p2x2b in qset:
                    # loc49 = p2x2b.nr

                    loc57_exp_s1 = twoside2reverse[p2x2b.side3]

                    unused.remove(p2x2b.nr1)
                    unused.remove(p2x2b.nr2)
                    unused.remove(p2x2b.nr3)
                    unused.remove(p2x2b.nr4)

                    exp_s3 = exp_s4 = twoside_border
                    qset = (Piece2x2
                            .objects
                            .filter(is_border=True,
                                    side3=exp_s3, side4=exp_s4, side1=loc57_exp_s1,
                                    nr1__in=unused, nr2__in=unused, nr3__in=unused, nr4__in=unused))
                    for p2x2c in qset:
                        # loc57 = p2x2c.nr
                        loc58_exp_s4 = twoside2reverse[p2x2c.side2]

                        c_nr = p2x2c.nr3
                        c4s.append(c_nr)

                        p1x1 = nr2base[p2x2c.nr2]
                        bb = p1x1.get_side(3, p2x2c.rot2) + p1x1.get_side(4, p2x2c.rot2)

                        unused.remove(p2x2c.nr1)
                        unused.remove(p2x2c.nr2)
                        unused.remove(p2x2c.nr3)
                        unused.remove(p2x2c.nr4)

                        exp_s3 = twoside_border
                        qset = (Piece2x2
                                .objects
                                .filter(is_border=True,
                                        side3=exp_s3, side1=loc58_exp_s1, side4=loc58_exp_s4,
                                        nr1__in=unused, nr2__in=unused, nr3__in=unused, nr4__in=unused)
                                .exclude(side2=twoside_border))

                        if qset.first():
                            zs[c_nr].append(bb)

                        unused.extend([p2x2c.nr1, p2x2c.nr2, p2x2c.nr3, p2x2c.nr4])
                    # for

                    unused.extend([p2x2b.nr1, p2x2b.nr2, p2x2b.nr3, p2x2b.nr4])
                # for

            # for side4
        # for side1

        c4s = list(set(c4s))
        c4s.sort()
        print('c4s: %s' % repr(c4s))

        for c in c4s:
            print('corner 4, c=%s' % c)
            bbs = list(set(zs[c]))
            bbs.sort()
            print('  zs: %s' % repr(bbs))
        # for

    @staticmethod
    def _needs_c3():
        c3s = list()
        zs = {1: [], 2: [], 3: [], 4: []}

        twoside_border = TwoSide.objects.get(two_sides='XX').nr

        two2nr = dict()
        side2two = dict()     # [two side nr] = two_sides
        for two in TwoSide.objects.all():
            two2nr[two.two_sides] = two.nr
            side2two[two.nr] = two.two_sides
        # for

        twoside2reverse = dict()
        for two_sides, nr in two2nr.items():
            two_rev = two_sides[1] + two_sides[0]
            rev_nr = two2nr[two_rev]
            twoside2reverse[nr] = rev_nr
        # for

        nr2base = dict()
        for p1x1 in BasePiece.objects.all():
            nr2base[p1x1.nr] = p1x1
        # for

        unused = list(range(1, 256+1))
        unused.remove(139)
        unused.remove(181)
        unused.remove(208)
        unused.remove(249)
        unused.remove(255)

        # loc 55
        qset = (Piece2x2
                .objects
                .filter(is_border=False,
                        has_hint=True,
                        nr4=249,
                        nr1__in=unused, nr2__in=unused, nr3__in=unused))
        loc55_sides2 = list(qset.distinct('side2').values_list('side2', flat=True))
        loc55_sides3 = list(qset.distinct('side3').values_list('side3', flat=True))

        todo = len(loc55_sides3)
        for loc55_side3 in loc55_sides3:
            print('todo: %s' % todo)
            todo -= 1
            loc63_exp_s1 = twoside2reverse[loc55_side3]

            for loc55_side2 in loc55_sides2:
                loc56_exp_s4 = twoside2reverse[loc55_side2]

                # loc 56
                exp_s2 = twoside_border
                qset = (Piece2x2
                        .objects
                        .filter(is_border=True,
                                side4=loc56_exp_s4, side2=exp_s2,
                                nr1__in=unused, nr2__in=unused, nr3__in=unused, nr4__in=unused)
                        .exclude(side3=twoside_border)
                        .exclude(side1=twoside_border))
                for p2x2b in qset:
                    # loc56 = p2x2b.nr

                    loc64_exp_s1 = twoside2reverse[p2x2b.side3]

                    unused.remove(p2x2b.nr1)
                    unused.remove(p2x2b.nr2)
                    unused.remove(p2x2b.nr3)
                    unused.remove(p2x2b.nr4)

                    exp_s2 = exp_s3 = twoside_border
                    qset = (Piece2x2
                            .objects
                            .filter(is_border=True,
                                    side2=exp_s2, side3=exp_s3, side1=loc64_exp_s1,
                                    nr1__in=unused, nr2__in=unused, nr3__in=unused, nr4__in=unused))
                    for p2x2c in qset:
                        # loc64 = p2x2c.nr
                        loc63_exp_s2 = twoside2reverse[p2x2c.side4]

                        c_nr = p2x2c.nr4
                        c3s.append(c_nr)

                        p1x1 = nr2base[p2x2c.nr1]
                        bb = p1x1.get_side(2, p2x2c.rot1) + p1x1.get_side(3, p2x2c.rot1)

                        unused.remove(p2x2c.nr1)
                        unused.remove(p2x2c.nr2)
                        unused.remove(p2x2c.nr3)
                        unused.remove(p2x2c.nr4)

                        exp_s3 = twoside_border
                        qset = (Piece2x2
                                .objects
                                .filter(is_border=True,
                                        side3=exp_s3, side1=loc63_exp_s1, side2=loc63_exp_s2,
                                        nr1__in=unused, nr2__in=unused, nr3__in=unused, nr4__in=unused)
                                .exclude(side2=twoside_border))

                        if qset.first():
                            zs[c_nr].append(bb)

                        unused.extend([p2x2c.nr1, p2x2c.nr2, p2x2c.nr3, p2x2c.nr4])
                    # for

                    unused.extend([p2x2b.nr1, p2x2b.nr2, p2x2b.nr3, p2x2b.nr4])
                # for

            # for side4
        # for side1

        c3s = list(set(c3s))
        c3s.sort()
        print('c3s: %s' % repr(c3s))

        for c in c3s:
            print('corner 3, c=%s' % c)
            bbs = list(set(zs[c]))
            bbs.sort()
            print('  zs: %s' % repr(bbs))
        # for

    @staticmethod
    def _needs_c2():
        c2s = list()
        zs = {1: [], 2: [], 3: [], 4: []}

        twoside_border = TwoSide.objects.get(two_sides='XX').nr

        two2nr = dict()
        side2two = dict()     # [two side nr] = two_sides
        for two in TwoSide.objects.all():
            two2nr[two.two_sides] = two.nr
            side2two[two.nr] = two.two_sides
        # for

        twoside2reverse = dict()
        for two_sides, nr in two2nr.items():
            two_rev = two_sides[1] + two_sides[0]
            rev_nr = two2nr[two_rev]
            twoside2reverse[nr] = rev_nr
        # for

        nr2base = dict()
        for p1x1 in BasePiece.objects.all():
            nr2base[p1x1.nr] = p1x1
        # for

        unused = list(range(1, 256+1))
        unused.remove(139)
        unused.remove(181)
        unused.remove(208)
        unused.remove(249)
        unused.remove(255)

        # loc 15
        qset = (Piece2x2
                .objects
                .filter(is_border=False,
                        has_hint=True,
                        nr2=255,
                        nr1__in=unused, nr3__in=unused, nr4__in=unused))
        loc15_sides2 = list(qset.distinct('side2').values_list('side2', flat=True))
        loc15_sides1 = list(qset.distinct('side4').values_list('side4', flat=True))

        todo = len(loc15_sides1)
        for loc15_side1 in loc15_sides1:
            print('todo: %s' % todo)
            todo -= 1
            loc7_exp_s3 = twoside2reverse[loc15_side1]

            for loc15_side2 in loc15_sides2:
                loc16_exp_s4 = twoside2reverse[loc15_side2]

                # loc 16
                exp_s2 = twoside_border
                qset = (Piece2x2
                        .objects
                        .filter(is_border=True,
                                side4=loc16_exp_s4, side2=exp_s2,
                                nr1__in=unused, nr2__in=unused, nr3__in=unused, nr4__in=unused)
                        .exclude(side3=twoside_border)
                        .exclude(side1=twoside_border))
                for p2x2b in qset:
                    # loc16 = p2x2b.nr

                    loc8_exp_s3 = twoside2reverse[p2x2b.side1]

                    unused.remove(p2x2b.nr1)
                    unused.remove(p2x2b.nr2)
                    unused.remove(p2x2b.nr3)
                    unused.remove(p2x2b.nr4)

                    exp_s1 = exp_s2 = twoside_border
                    qset = (Piece2x2
                            .objects
                            .filter(is_border=True,
                                    side1=exp_s1, side2=exp_s2, side3=loc8_exp_s3,
                                    nr1__in=unused, nr2__in=unused, nr3__in=unused, nr4__in=unused))
                    for p2x2c in qset:
                        # loc8 = p2x2c.nr
                        loc7_exp_s2 = twoside2reverse[p2x2c.side4]

                        c_nr = p2x2c.nr2
                        c2s.append(c_nr)

                        p1x1 = nr2base[p2x2c.nr3]
                        bb = p1x1.get_side(1, p2x2c.rot3) + p1x1.get_side(2, p2x2c.rot3)

                        unused.remove(p2x2c.nr1)
                        unused.remove(p2x2c.nr2)
                        unused.remove(p2x2c.nr3)
                        unused.remove(p2x2c.nr4)

                        exp_s1 = twoside_border
                        qset = (Piece2x2
                                .objects
                                .filter(is_border=True,
                                        side1=exp_s1, side2=loc7_exp_s2, side3=loc7_exp_s3,
                                        nr1__in=unused, nr2__in=unused, nr3__in=unused, nr4__in=unused)
                                .exclude(side2=twoside_border))

                        if qset.first():
                            zs[c_nr].append(bb)

                        unused.extend([p2x2c.nr1, p2x2c.nr2, p2x2c.nr3, p2x2c.nr4])
                    # for

                    unused.extend([p2x2b.nr1, p2x2b.nr2, p2x2b.nr3, p2x2b.nr4])
                # for

            # for side4
        # for side1

        c2s = list(set(c2s))
        c2s.sort()
        print('c1s: %s' % repr(c2s))

        for c in c2s:
            print('corner2, c=%s' % c)
            bbs = list(set(zs[c]))
            bbs.sort()
            print('  zs: %s' % repr(bbs))
        # for

    @staticmethod
    def _needs_c1():
        c1s = list()
        zs = {1: [], 2: [], 3: [], 4: []}

        twoside_border = TwoSide.objects.get(two_sides='XX').nr

        two2nr = dict()
        side2two = dict()     # [two side nr] = two_sides
        for two in TwoSide.objects.all():
            two2nr[two.two_sides] = two.nr
            side2two[two.nr] = two.two_sides
        # for

        twoside2reverse = dict()
        for two_sides, nr in two2nr.items():
            two_rev = two_sides[1] + two_sides[0]
            rev_nr = two2nr[two_rev]
            twoside2reverse[nr] = rev_nr
        # for

        nr2base = dict()
        for p1x1 in BasePiece.objects.all():
            nr2base[p1x1.nr] = p1x1
        # for

        unused = list(range(1, 256+1))
        unused.remove(139)
        unused.remove(181)
        unused.remove(208)
        unused.remove(249)
        unused.remove(255)

        # loc 10
        qset = (Piece2x2
                .objects
                .filter(is_border=False,
                        has_hint=True,
                        nr1=208,
                        nr2__in=unused, nr3__in=unused, nr4__in=unused))
        loc10_sides4 = list(qset.distinct('side4').values_list('side4', flat=True))
        loc10_sides1 = list(qset.distinct('side1').values_list('side1', flat=True))

        todo = len(loc10_sides1)
        for loc10_side1 in loc10_sides1:
            print('todo: %s' % todo)
            todo -= 1
            loc2_exp_s3 = twoside2reverse[loc10_side1]

            for loc10_side4 in loc10_sides4:
                loc9_exp_s2 = twoside2reverse[loc10_side4]

                # loc 9
                exp_s4 = twoside_border
                qset = (Piece2x2
                        .objects
                        .filter(is_border=True,
                                side2=loc9_exp_s2, side4=exp_s4,
                                nr1__in=unused, nr2__in=unused, nr3__in=unused, nr4__in=unused)
                        .exclude(side3=twoside_border)
                        .exclude(side1=twoside_border))
                for p2x2b in qset:
                    # loc9 = p2x2b.nr

                    loc1_exp_s3 = twoside2reverse[p2x2b.side1]

                    unused.remove(p2x2b.nr1)
                    unused.remove(p2x2b.nr2)
                    unused.remove(p2x2b.nr3)
                    unused.remove(p2x2b.nr4)

                    exp_s1 = exp_s4 = twoside_border
                    qset = (Piece2x2
                            .objects
                            .filter(is_border=True,
                                    side1=exp_s1, side4=exp_s4, side3=loc1_exp_s3,
                                    nr1__in=unused, nr2__in=unused, nr3__in=unused, nr4__in=unused))
                    for p2x2c in qset:
                        # loc1 = p2x2c.nr
                        loc2_exp_s4 = twoside2reverse[p2x2c.side2]

                        c_nr = p2x2c.nr1
                        c1s.append(c_nr)

                        p1x1 = nr2base[p2x2c.nr4]
                        bb = p1x1.get_side(4, p2x2c.rot4) + p1x1.get_side(1, p2x2c.rot4)

                        unused.remove(p2x2c.nr1)
                        unused.remove(p2x2c.nr2)
                        unused.remove(p2x2c.nr3)
                        unused.remove(p2x2c.nr4)

                        exp_s1 = twoside_border
                        qset = (Piece2x2
                                .objects
                                .filter(is_border=True,
                                        side1=exp_s1, side4=loc2_exp_s4, side3=loc2_exp_s3,
                                        nr1__in=unused, nr2__in=unused, nr3__in=unused, nr4__in=unused)
                                .exclude(side2=twoside_border))

                        if qset.first():
                            zs[c_nr].append(bb)

                        unused.extend([p2x2c.nr1, p2x2c.nr2, p2x2c.nr3, p2x2c.nr4])
                    # for

                    unused.extend([p2x2b.nr1, p2x2b.nr2, p2x2b.nr3, p2x2b.nr4])
                # for

            # for side4
        # for side1

        c1s = list(set(c1s))
        c1s.sort()
        print('c1s: %s' % repr(c1s))

        for c in c1s:
            print('corner 1, c=%s' % c)
            bbs = list(set(zs[c]))
            bbs.sort()
            print('  zs: %s' % repr(bbs))
        # for

    def handle(self, *args, **options):
        #self._needs_c1()
        #self._needs_c2()
        #self._needs_c3()
        self._needs_c4()
        return

        seed = options['seed']
        gen = GenerateBorder(seed)
        for sol in gen.iter_solutions():
            #print('solution: %s' % repr(sol))
            print('c1.nr4=%s' % repr(list(Piece2x2.objects.filter(nr3=sol[6], nr1=sol[7], nr2=sol[8]).distinct('nr4').values_list('nr4', flat=True))))


# end of file
