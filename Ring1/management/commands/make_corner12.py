# -*- coding: utf-8 -*-

#  Copyright (c) 2024 Ramon van der Winkel.
#  All rights reserved.
#  Licensed under BSD-3-Clause-Clear. See LICENSE file for details.

from django.core.management.base import BaseCommand
from Pieces2x2.models import TwoSide, Piece2x2
from Ring1.models import Corner1, Corner2, Corner12


class Command(BaseCommand):

    help = "Compile a Corner12 from Corner1 and Corner2"

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

        self.count = 0

    def add_arguments(self, parser):
        parser.add_argument('seed', type=int, help='Randomization seed')

    def reverse_sides(self, sides):
        return [self.twoside2reverse[side] for side in sides]

    def _save(self, c1, c2):
        p25 = Piece2x2.objects.get(nr=c1.loc25)
        p32 = Piece2x2.objects.get(nr=c2.loc32)

        c12 = Corner12(
                    seed=c1.seed,

                    c1=c1.nr,
                    c2=c2.nr,

                    side3_left=p25.side3,
                    side3_right=p32.side3)

        for nr in range(1, 40+1):
            nr_str = 'nr%s' % nr
            nr1_str = nr_str
            nr2_str = 'nr%s' % (40 + nr)
            setattr(c12, nr1_str, getattr(c1, nr_str))
            setattr(c12, nr2_str, getattr(c2, nr_str))
        # for

        c12.save()
        self.stdout.write('saved Corner12 pk=%s' % c12.pk)
        self.count += 1

    def _check(self, c1, c2):
        # verify location 12 and 13 can be filled with the remaining pieces
        p2x2_loc4 = Piece2x2.objects.get(nr=c1.loc4)
        p2x2_loc11 = Piece2x2.objects.get(nr=c1.loc11)
        p2x2_loc5 = Piece2x2.objects.get(nr=c2.loc5)
        p2x2_loc14 = Piece2x2.objects.get(nr=c2.loc14)

        loc12_exp_s1 = self.twoside2reverse[p2x2_loc4.side3]
        loc12_exp_s4 = self.twoside2reverse[p2x2_loc11.side2]
        loc13_exp_s1 = self.twoside2reverse[p2x2_loc5.side3]
        loc13_exp_s2 = self.twoside2reverse[p2x2_loc14.side4]

        used = [c1.nr1, c1.nr2, c1.nr3, c1.nr4, c1.nr5, c1.nr6, c1.nr7, c1.nr8, c1.nr9, c1.nr10, c1.nr11, c1.nr12,
                c1.nr13, c1.nr14, c1.nr15, c1.nr16, c1.nr17, c1.nr18, c1.nr19, c1.nr20, c1.nr21, c1.nr22, c1.nr23,
                c1.nr24, c1.nr25, c1.nr26, c1.nr27, c1.nr28, c1.nr29, c1.nr30, c1.nr31, c1.nr32, c1.nr33, c1.nr34,
                c1.nr35, c1.nr36, c1.nr37, c1.nr38, c1.nr39, c1.nr40,
                c2.nr1, c2.nr2, c2.nr3, c2.nr4, c2.nr5, c2.nr6, c2.nr7, c2.nr8, c2.nr9, c2.nr10, c2.nr11, c2.nr12,
                c2.nr13, c2.nr14, c2.nr15, c2.nr16, c2.nr17, c2.nr18, c2.nr19, c2.nr20, c2.nr21, c2.nr22, c2.nr23,
                c2.nr24, c2.nr25, c2.nr26, c2.nr27, c2.nr28, c2.nr29, c2.nr30, c2.nr31, c2.nr32, c2.nr33, c2.nr34,
                c2.nr35, c2.nr36, c2.nr37, c2.nr38, c2.nr39, c2.nr40]

        qset = Piece2x2.objects.exclude(nr1__in=used).exclude(nr2__in=used).exclude(nr3__in=used).exclude(nr4__in=used)
        qset = qset.exclude(side3=self.twoside_border)

        found = False
        for p2x2_loc12 in qset.filter(side1=loc12_exp_s1, side4=loc12_exp_s4):
            loc13_exp_s4 = self.twoside2reverse[p2x2_loc12.side2]

            p2x2_loc13 = qset.filter(side1=loc13_exp_s1, side2=loc13_exp_s2, side4=loc13_exp_s4).first()
            if p2x2_loc13:
                found = True
                break
        # for

        # TODO: check solution for locs 19, 26, 22, 31 with remaining unused pieces

        if found:
            self._save(c1, c2)
        
    def _iter_c2(self, c1):
        used = [c1.nr1, c1.nr2, c1.nr3, c1.nr4, c1.nr5, c1.nr6, c1.nr7, c1.nr8, c1.nr9, c1.nr10, c1.nr11, c1.nr12,
                c1.nr13, c1.nr14, c1.nr15, c1.nr16, c1.nr17, c1.nr18, c1.nr19, c1.nr20, c1.nr21, c1.nr22, c1.nr23,
                c1.nr24, c1.nr25, c1.nr26, c1.nr27, c1.nr28, c1.nr29, c1.nr30, c1.nr31, c1.nr32, c1.nr33, c1.nr34,
                c1.nr35, c1.nr36, c1.nr37, c1.nr38, c1.nr39, c1.nr40]

        exp_s4 = self.twoside2reverse[c1.side2]

        for c2 in (Corner2
                   .objects
                   .filter(seed=c1.seed,
                           side4=exp_s4)
                   .exclude(nr1__in=used)
                   .exclude(nr2__in=used)
                   .exclude(nr3__in=used)
                   .exclude(nr4__in=used)
                   .exclude(nr5__in=used)
                   .exclude(nr6__in=used)
                   .exclude(nr7__in=used)
                   .exclude(nr8__in=used)
                   .exclude(nr9__in=used)
                   .exclude(nr10__in=used)
                   .exclude(nr11__in=used)
                   .exclude(nr12__in=used)
                   .exclude(nr13__in=used)
                   .exclude(nr14__in=used)
                   .exclude(nr15__in=used)
                   .exclude(nr16__in=used)
                   .exclude(nr17__in=used)
                   .exclude(nr18__in=used)
                   .exclude(nr19__in=used)
                   .exclude(nr20__in=used)
                   .exclude(nr21__in=used)
                   .exclude(nr22__in=used)
                   .exclude(nr23__in=used)
                   .exclude(nr24__in=used)
                   .exclude(nr25__in=used)
                   .exclude(nr26__in=used)
                   .exclude(nr27__in=used)
                   .exclude(nr28__in=used)
                   .exclude(nr29__in=used)
                   .exclude(nr30__in=used)
                   .exclude(nr31__in=used)
                   .exclude(nr32__in=used)
                   .exclude(nr33__in=used)
                   .exclude(nr34__in=used)
                   .exclude(nr35__in=used)
                   .exclude(nr36__in=used)
                   .exclude(nr37__in=used)
                   .exclude(nr38__in=used)
                   .exclude(nr39__in=used)
                   .exclude(nr40__in=used)):

            self._check(c1, c2)
        # for

    def _iter_c1(self, seed):
        for c1 in Corner1.objects.filter(seed=seed).iterator(chunk_size=1000):
            self._iter_c2(c1)
        # for

    def handle(self, *args, **options):

        seed = options['seed']

        Corner12.objects.filter(seed=seed).delete()

        try:
            self._iter_c1(seed)
        except KeyboardInterrupt:
            pass

        self.stdout.write('[INFO] Created %s Corner12' % self.count)

        count1 = Corner12.objects.distinct('side3_left').count()
        count2 = Corner12.objects.distinct('side3_right').count()
        self.stdout.write('[INFO] Distinct sides: %s, %s' % (count1, count2))

# end of file
