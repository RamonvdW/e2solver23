# -*- coding: utf-8 -*-

#  Copyright (c) 2024 Ramon van der Winkel.
#  All rights reserved.
#  Licensed under BSD-3-Clause-Clear. See LICENSE file for details.

from django.core.management.base import BaseCommand
from Pieces2x2.models import Piece2x2, TwoSide


class Command(BaseCommand):

    help = "Calculate the possible 7-border pieces in each corner, considering the hints"

    """
        Method:
            +---------+        +---------+
            | c     b |        | b     b |    c = corner (base piece 1..4)
            |   2x2   | side # |   2x2   |    b = border (base piece 5..60)
            | b     x |        | x     x |    h = hint (base piece 181,208,249,255)
            +---------+        +---------+    x = don't care
               side #             side #
            +---------+        +---------+
            | b     x |        | H     x |
            |   2x2   | side # |   2x2   |
            | b     x |        | x     x |
            +---------+        +---------+ 
    
            with   2x2 count
            c=1     339
            c=2     386
            c=3     276
            c=4     290
            h=208  5414   (corner 1)
            h=255  4847   (corner 2)
            h=249  5405   (corner 3)
            h=181  4613   (corner 4)  
    
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        two2nr = dict()
        side2two = dict()     # [two side nr] = two_sides
        for two in TwoSide.objects.all():
            two2nr[two.two_sides] = two.nr
            side2two[two.nr] = two.two_sides
        # for
        self.twoside2reverse = dict()
        for two_sides, nr in two2nr.items():
            two_rev = two_sides[1] + two_sides[0]
            rev_nr = two2nr[two_rev]
            self.twoside2reverse[nr] = rev_nr
        # for

        self.bbbcbbb = []
        self._print = -1

    def add_arguments(self, parser):
        parser.add_argument('corner', type=int, help='Corner to work on')

    def _add_bbbcbbb(self, bbbcbbb):
        if len(frozenset(bbbcbbb)) != len(bbbcbbb):
            raise ValueError('Invalid: %s' % repr(bbbcbbb))

        if bbbcbbb not in self.bbbcbbb:
            self.bbbcbbb.append(bbbcbbb)

            count = len(self.bbbcbbb)
            if count > self._print:
                print(count)
                self._print += 1000

    def _needs_c1(self):
        # solve order: 1, 2, 9, 10
        p10_s1_set = Piece2x2.objects.filter(nr1=208).values_list('side1', flat=True)
        p10_s4_set = Piece2x2.objects.filter(nr1=208).values_list('side4', flat=True)
        p2_exp_s3_set = [self.twoside2reverse[side] for side in p10_s1_set]
        p9_exp_s2_set = [self.twoside2reverse[side] for side in p10_s4_set]

        for p1 in Piece2x2.objects.filter(nr1__in=(1, 2, 3, 4)):
            p2_exp_s4 = self.twoside2reverse[p1.side2]
            p9_exp_s1 = self.twoside2reverse[p1.side3]
            used1 = [p1.nr1, p1.nr2, p1.nr3, p1.nr4]

            for p2 in (Piece2x2
                       .objects
                       .filter(side4=p2_exp_s4,
                               side3__in=p2_exp_s3_set)
                       .exclude(nr1__in=used1)
                       .exclude(nr2__in=used1)
                       .exclude(nr3__in=used1)
                       .exclude(nr4__in=used1)):

                used2 = used1[:]
                used2.extend([p2.nr1, p2.nr2, p2.nr3, p2.nr4])

                for p9 in (Piece2x2
                           .objects
                           .filter(side1=p9_exp_s1,
                                   side2__in=p9_exp_s2_set)
                           .exclude(nr1__in=used2)
                           .exclude(nr2__in=used2)
                           .exclude(nr3__in=used2)
                           .exclude(nr4__in=used2)):

                    bbbcbbb = (p9.nr3, p9.nr1, p1.nr3, p1.nr1, p1.nr2, p2.nr1, p2.nr2)
                    self._add_bbbcbbb(bbbcbbb)
                # for
            # for
        # for

    def _needs_c2(self):
        # solve order: 8, 7, 16, 15
        p15_s1_set = Piece2x2.objects.filter(nr2=255).values_list('side1', flat=True)
        p15_s2_set = Piece2x2.objects.filter(nr2=255).values_list('side2', flat=True)
        p7_exp_s3_set = [self.twoside2reverse[side] for side in p15_s1_set]
        p16_exp_s4_set = [self.twoside2reverse[side] for side in p15_s2_set]

        for p8 in Piece2x2.objects.filter(nr2__in=(1, 2, 3, 4)):
            p7_exp_s2 = self.twoside2reverse[p8.side4]
            p16_exp_s1 = self.twoside2reverse[p8.side3]
            used1 = [p8.nr1, p8.nr2, p8.nr3, p8.nr4]

            for p7 in (Piece2x2
                       .objects
                       .filter(side2=p7_exp_s2,
                               side3__in=p7_exp_s3_set)
                       .exclude(nr1__in=used1)
                       .exclude(nr2__in=used1)
                       .exclude(nr3__in=used1)
                       .exclude(nr4__in=used1)):

                used2 = used1[:]
                used2.extend([p7.nr1, p7.nr2, p7.nr3, p7.nr4])

                for p16 in (Piece2x2
                            .objects
                            .filter(side1=p16_exp_s1,
                                    side4__in=p16_exp_s4_set)
                            .exclude(nr1__in=used2)
                            .exclude(nr2__in=used2)
                            .exclude(nr3__in=used2)
                            .exclude(nr4__in=used2)):

                    bbbcbbb = (p7.nr1, p7.nr2, p8.nr1, p8.nr2, p8.nr4, p16.nr2, p16.nr4)
                    self._add_bbbcbbb(bbbcbbb)
                # for
            # for
        # for

    def _needs_c3(self):
        # solve order: 64, 63, 56, 55
        p55_s2_set = Piece2x2.objects.filter(nr4=249).values_list('side2', flat=True)
        p55_s3_set = Piece2x2.objects.filter(nr4=249).values_list('side3', flat=True)
        p56_exp_s4_set = [self.twoside2reverse[side] for side in p55_s2_set]
        p63_exp_s1_set = [self.twoside2reverse[side] for side in p55_s3_set]

        for p64 in Piece2x2.objects.filter(nr4__in=(1, 2, 3, 4)):
            p63_exp_s2 = self.twoside2reverse[p64.side4]
            p56_exp_s3 = self.twoside2reverse[p64.side1]
            used1 = [p64.nr1, p64.nr2, p64.nr3, p64.nr4]

            for p63 in (Piece2x2
                        .objects
                        .filter(side2=p63_exp_s2,
                                side1__in=p63_exp_s1_set)
                        .exclude(nr1__in=used1)
                        .exclude(nr2__in=used1)
                        .exclude(nr3__in=used1)
                        .exclude(nr4__in=used1)):

                used2 = used1[:]
                used2.extend([p63.nr1, p63.nr2, p63.nr3, p63.nr4])

                for p56 in (Piece2x2
                            .objects
                            .filter(side3=p56_exp_s3,
                                    side4__in=p56_exp_s4_set)
                            .exclude(nr1__in=used2)
                            .exclude(nr2__in=used2)
                            .exclude(nr3__in=used2)
                            .exclude(nr4__in=used2)):

                    bbbcbbb = (p56.nr2, p56.nr4, p64.nr2, p64.nr4, p64.nr3, p63.nr4, p63.nr3)
                    self._add_bbbcbbb(bbbcbbb)
                # for
            # for
        # for

    def _needs_c4(self):
        # solve order: 57, 58, 49, 50
        p50_s3_set = Piece2x2.objects.filter(nr3=181).values_list('side3', flat=True)
        p50_s4_set = Piece2x2.objects.filter(nr3=181).values_list('side4', flat=True)
        p58_exp_s1_set = [self.twoside2reverse[side] for side in p50_s3_set]
        p49_exp_s2_set = [self.twoside2reverse[side] for side in p50_s4_set]

        for p57 in Piece2x2.objects.filter(nr3__in=(1, 2, 3, 4)):
            p58_exp_s4 = self.twoside2reverse[p57.side2]
            p49_exp_s3 = self.twoside2reverse[p57.side1]
            used1 = [p57.nr1, p57.nr2, p57.nr3, p57.nr4]

            for p58 in (Piece2x2
                        .objects
                        .filter(side4=p58_exp_s4,
                                side1__in=p58_exp_s1_set)
                        .exclude(nr1__in=used1)
                        .exclude(nr2__in=used1)
                        .exclude(nr3__in=used1)
                        .exclude(nr4__in=used1)):

                used2 = used1[:]
                used2.extend([p58.nr1, p58.nr2, p58.nr3, p58.nr4])

                for p49 in (Piece2x2
                            .objects
                            .filter(side3=p49_exp_s3,
                                    side2__in=p49_exp_s2_set)
                            .exclude(nr1__in=used2)
                            .exclude(nr2__in=used2)
                            .exclude(nr3__in=used2)
                            .exclude(nr4__in=used2)):

                    bbbcbbb = (p58.nr4, p58.nr3, p57.nr4, p57.nr3, p57.nr1, p49.nr3, p49.nr1)
                    self._add_bbbcbbb(bbbcbbb)
                # for
            # for
        # for

    def handle(self, *args, **options):
        corner = options['corner']

        if corner == 1:
            self._needs_c1()
        elif corner == 2:
            self._needs_c2()
        elif corner == 3:
            self._needs_c3()
        elif corner == 4:
            self._needs_c4()

        print('[INFO] %s bbcbb for corner %s' % (len(self.bbbcbbb), corner))
        print('bbbcbbb%s = [' % corner)
        for bbbcbbb in self.bbbcbbb:
            print('    %s,' % repr(bbbcbbb))
        print(']')

# end of file
