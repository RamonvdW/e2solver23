# -*- coding: utf-8 -*-

#  Copyright (c) 2023-2024 Ramon van der Winkel.
#  All rights reserved.
#  Licensed under BSD-3-Clause-Clear. See LICENSE file for details.

from django.core.management.base import BaseCommand
from Pieces2x2.models import TwoSideOptions, TwoSide, Piece2x2
from Pieces2x2.helpers import calc_segment
from Ring1.models import Ring1, Corner1, Corner2, Corner3, Corner4


class Command(BaseCommand):

    help = "Compile a Ring1 from Corner1..4"

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

    def reverse_sides(self, sides):
        return [self.twoside2reverse[side] for side in sides]

    def _save(self, c1, c2, c3, c4):
        ring1 = Ring1(
                    nr1=c1.loc1,
                    nr2=c1.loc2,
                    nr3=c1.loc3,
                    nr4=c1.loc4,

                    nr5=c2.loc5,
                    nr6=c2.loc6,
                    nr7=c2.loc7,
                    nr8=c2.loc8,

                    nr9=c1.loc9,
                    nr10=c1.loc10,
                    nr11=c1.loc11,

                    nr14=c2.loc14,
                    nr15=c2.loc15,
                    nr16=c2.loc16,

                    nr17=c1.loc17,
                    nr18=c1.loc18,

                    nr23=c2.loc23,
                    nr24=c2.loc24,

                    nr25=c1.loc25,

                    nr32=c2.loc32,

                    nr33=c4.loc33,

                    nr40=c3.loc40,

                    nr41=c4.loc41,
                    nr42=c4.loc42,

                    nr47=c3.loc47,
                    nr48=c3.loc48,

                    nr49=c4.loc49,
                    nr50=c4.loc50,
                    nr51=c4.loc51,

                    nr54=c3.loc54,
                    nr55=c3.loc55,
                    nr56=c3.loc56,

                    nr57=c4.loc57,
                    nr58=c4.loc58,
                    nr59=c4.loc59,
                    nr60=c4.loc60,

                    nr61=c3.loc61,
                    nr62=c3.loc62,
                    nr63=c3.loc63,
                    nr64=c3.loc64,

                    nr36=0)

        ring1.save()
        print('saved Ring1 pk=%s' % ring1.pk)

    def _iter_c4(self, c1, c2, c3):
        print('c1:%s c2:%s c3:%s' % (c1.pk, c2.pk, c3.pk))

        c4 = Corner4(loc33=0, loc41=0, loc42=0, loc49=0, loc50=0, loc51=0, loc57=0, loc58=0, loc59=0, loc60=0)
        self._save(c1, c2, c3, c4)
        return

        used = [c1.nr1, c1.nr2, c1.nr3, c1.nr4, c1.nr5, c1.nr6, c1.nr7, c1.nr8, c1.nr9, c1.nr10, c1.nr11, c1.nr12,
                c1.nr13, c1.nr14, c1.nr15, c1.nr16, c1.nr17, c1.nr18, c1.nr19, c1.nr20, c1.nr21, c1.nr22, c1.nr23,
                c1.nr24, c1.nr25, c1.nr26, c1.nr27, c1.nr28, c1.nr29, c1.nr30, c1.nr31, c1.nr32, c1.nr33, c1.nr34,
                c1.nr35, c1.nr36, c1.nr37, c1.nr38, c1.nr39, c1.nr40,
                c2.nr1, c2.nr2, c2.nr3, c2.nr4, c2.nr5, c2.nr6, c2.nr7, c2.nr8, c2.nr9, c2.nr10, c2.nr11, c2.nr12,
                c2.nr13, c2.nr14, c2.nr15, c2.nr16, c2.nr17, c2.nr18, c2.nr19, c2.nr20, c2.nr21, c2.nr22, c2.nr23,
                c2.nr24, c2.nr25, c2.nr26, c2.nr27, c2.nr28, c2.nr29, c2.nr30, c2.nr31, c2.nr32, c2.nr33, c2.nr34,
                c2.nr35, c2.nr36, c2.nr37, c2.nr38, c2.nr39, c2.nr40,
                c3.nr1, c3.nr2, c3.nr3, c3.nr4, c3.nr5, c3.nr6, c3.nr7, c3.nr8, c3.nr9, c3.nr10, c3.nr11, c3.nr12,
                c3.nr13, c3.nr14, c3.nr15, c3.nr16, c3.nr17, c3.nr18, c3.nr19, c3.nr20, c3.nr21, c3.nr22, c3.nr23,
                c3.nr24, c3.nr25, c3.nr26, c3.nr27, c3.nr28, c3.nr29, c3.nr30, c3.nr31, c3.nr32, c3.nr33, c3.nr34,
                c3.nr35, c3.nr36, c3.nr37, c3.nr38, c3.nr39, c3.nr40]

        exp_s2 = self.twoside2reverse[c3.side4]
        exp_s1 = self.twoside2reverse[c1.side3]
        for c4 in (Corner4
                   .objects
                   .filter(side1=exp_s1,
                           side2=exp_s2)
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

            self._save(c1, c2, c3, c4)
        # for

    def _iter_c2(self, c1, c3):
        print('c1:%s c3:%s' % (c1.pk, c3.pk))

        used = [c1.nr1, c1.nr2, c1.nr3, c1.nr4, c1.nr5, c1.nr6, c1.nr7, c1.nr8, c1.nr9, c1.nr10, c1.nr11, c1.nr12,
                c1.nr13, c1.nr14, c1.nr15, c1.nr16, c1.nr17, c1.nr18, c1.nr19, c1.nr20, c1.nr21, c1.nr22, c1.nr23,
                c1.nr24, c1.nr25, c1.nr26, c1.nr27, c1.nr28, c1.nr29, c1.nr30, c1.nr31, c1.nr32, c1.nr33, c1.nr34,
                c1.nr35, c1.nr36, c1.nr37, c1.nr38, c1.nr39, c1.nr40,
                c3.nr1, c3.nr2, c3.nr3, c3.nr4, c3.nr5, c3.nr6, c3.nr7, c3.nr8, c3.nr9, c3.nr10, c3.nr11, c3.nr12,
                c3.nr13, c3.nr14, c3.nr15, c3.nr16, c3.nr17, c3.nr18, c3.nr19, c3.nr20, c3.nr21, c3.nr22, c3.nr23,
                c3.nr24, c3.nr25, c3.nr26, c3.nr27, c3.nr28, c3.nr29, c3.nr30, c3.nr31, c3.nr32, c3.nr33, c3.nr34,
                c3.nr35, c3.nr36, c3.nr37, c3.nr38, c3.nr39, c3.nr40]

        exp_s4 = self.twoside2reverse[c1.side2]
        exp_s3 = self.twoside2reverse[c3.side1]

        for c2 in (Corner2
                   .objects
                   .filter(side4=exp_s4,
                           side3=exp_s3)
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

            self._iter_c4(c1, c2, c3)
        # for

    def _iter_c3(self, c1):

        used = [c1.nr1, c1.nr2, c1.nr3, c1.nr4, c1.nr5, c1.nr6, c1.nr7, c1.nr8, c1.nr9, c1.nr10, c1.nr11, c1.nr12,
                c1.nr13, c1.nr14, c1.nr15, c1.nr16, c1.nr17, c1.nr18, c1.nr19, c1.nr20, c1.nr21, c1.nr22, c1.nr23,
                c1.nr24, c1.nr25, c1.nr26, c1.nr27, c1.nr28, c1.nr29, c1.nr30, c1.nr31, c1.nr32, c1.nr33, c1.nr34,
                c1.nr35, c1.nr36, c1.nr37, c1.nr38, c1.nr39, c1.nr40]

        for c3 in (Corner3
                   .objects
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

            self._iter_c2(c1, c3)
        # for

    def _iter_c1(self):
        for c1 in Corner1.objects.all().iterator(chunk_size=1000):
            self._iter_c3(c1)
        # for

    def handle(self, *args, **options):

        self._iter_c1()


# end of file
