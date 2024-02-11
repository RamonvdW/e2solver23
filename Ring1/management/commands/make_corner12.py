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

    def _save(self, c1, c2):
        p25 = Piece2x2.objects.get(nr=c1.loc25)
        p32 = Piece2x2.objects.get(nr=c2.loc32)

        c12 = Corner12(
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
        print('saved Corner12 pk=%s' % c12.pk)
        self.count += 1

    def _iter_c2(self, c1):
        used = [c1.nr1, c1.nr2, c1.nr3, c1.nr4, c1.nr5, c1.nr6, c1.nr7, c1.nr8, c1.nr9, c1.nr10, c1.nr11, c1.nr12,
                c1.nr13, c1.nr14, c1.nr15, c1.nr16, c1.nr17, c1.nr18, c1.nr19, c1.nr20, c1.nr21, c1.nr22, c1.nr23,
                c1.nr24, c1.nr25, c1.nr26, c1.nr27, c1.nr28, c1.nr29, c1.nr30, c1.nr31, c1.nr32, c1.nr33, c1.nr34,
                c1.nr35, c1.nr36, c1.nr37, c1.nr38, c1.nr39, c1.nr40]

        exp_s4 = self.twoside2reverse[c1.side2]

        for c2 in (Corner2
                   .objects
                   .filter(side4=exp_s4)
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

            self._save(c1, c2)
        # for

    def _iter_c1(self):
        for c1 in Corner1.objects.all().iterator(chunk_size=1000):
            self._iter_c2(c1)
        # for

    def handle(self, *args, **options):

        Corner12.objects.all().delete()

        try:
            self._iter_c1()
        except KeyboardInterrupt:
            pass

        print('[INFO] Created %s Corner12' % self.count)


# end of file
