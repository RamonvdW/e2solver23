# -*- coding: utf-8 -*-

#  Copyright (c) 2024 Ramon van der Winkel.
#  All rights reserved.
#  Licensed under BSD-3-Clause-Clear. See LICENSE file for details.

from django.core.management.base import BaseCommand
from Pieces2x2.models import TwoSide, Piece2x2
from Ring1.models import Corner3, Corner4, Corner34


class Command(BaseCommand):

    help = "Compile a Corner34 from Corner3 and Corner4"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

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

    def reverse_sides(self, sides):
        return [self.twoside2reverse[side] for side in sides]

    def _save(self, c3, c4):
        p33 = Piece2x2.objects.get(nr=c4.loc33)
        p40 = Piece2x2.objects.get(nr=c3.loc40)

        c34 = Corner34(
                    c3=c3.nr,
                    c4=c4.nr,

                    side1_left=p33.side1,
                    side1_right=p40.side1)

        for nr in range(1, 40+1):
            nr_str = 'nr%s' % nr
            nr1_str = nr_str
            nr2_str = 'nr%s' % (40 + nr)
            setattr(c34, nr1_str, getattr(c3, nr_str))
            setattr(c34, nr2_str, getattr(c4, nr_str))
        # for

        c34.save()
        print('saved Corner34 pk=%s' % c34.pk)
        self.count += 1

    def _iter_c4(self, c3):
        used = [c3.nr1, c3.nr2, c3.nr3, c3.nr4, c3.nr5, c3.nr6, c3.nr7, c3.nr8, c3.nr9, c3.nr10, c3.nr11, c3.nr12,
                c3.nr13, c3.nr14, c3.nr15, c3.nr16, c3.nr17, c3.nr18, c3.nr19, c3.nr20, c3.nr21, c3.nr22, c3.nr23,
                c3.nr24, c3.nr25, c3.nr26, c3.nr27, c3.nr28, c3.nr29, c3.nr30, c3.nr31, c3.nr32, c3.nr33, c3.nr34,
                c3.nr35, c3.nr36, c3.nr37, c3.nr38, c3.nr39, c3.nr40]

        exp_s2 = self.twoside2reverse[c3.side4]

        for c4 in (Corner4
                   .objects
                   .filter(side2=exp_s2)
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
                   .exclude(nr40__in=used)
                   .iterator(chunk_size=1000)):

            self._save(c3, c4)
        # for

    def _iter_c3(self):
        for c3 in Corner3.objects.all().iterator(chunk_size=1000):
            # print('c3 pk=%s, side1=%s, side4=%s' % (c3.pk, c3.side1, c3.side4))
            self._iter_c4(c3)
        # for

    def handle(self, *args, **options):

        Corner34.objects.all().delete()

        try:
            self._iter_c3()
        except KeyboardInterrupt:
            pass

        self.stdout.write('[INFO] Created %s Corner34' % self.count)

        count1 = Corner34.objects.distinct('side1_left').count()
        count2 = Corner34.objects.distinct('side1_right').count()
        self.stdout.write('[INFO] Distinct sides: %s, %s' % (count1, count2))

# end of file
