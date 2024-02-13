# -*- coding: utf-8 -*-

#  Copyright (c) 2024 Ramon van der Winkel.
#  All rights reserved.
#  Licensed under BSD-3-Clause-Clear. See LICENSE file for details.

from django.core.management.base import BaseCommand
from Pieces2x2.models import TwoSide
from Ring1.models import Ring1, Corner12, Corner34


class Command(BaseCommand):

    help = "Compile a Ring1 from Corner12 and Corner34"

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

    def add_arguments(self, parser):
        parser.add_argument('seed', type=int, help='Randomization seed')

    def reverse_sides(self, sides):
        return [self.twoside2reverse[side] for side in sides]

    def _save(self, c12, c34):
        ring1 = Ring1(
                    seed=c12.seed,

                    nr1=c12.loc1,
                    nr2=c12.loc2,
                    nr3=c12.loc3,
                    nr4=c12.loc4,

                    nr5=c12.loc5,
                    nr6=c12.loc6,
                    nr7=c12.loc7,
                    nr8=c12.loc8,

                    nr9=c12.loc9,
                    nr10=c12.loc10,
                    nr11=c12.loc11,

                    nr14=c12.loc14,
                    nr15=c12.loc15,
                    nr16=c12.loc16,

                    nr17=c12.loc17,
                    nr18=c12.loc18,

                    nr23=c12.loc23,
                    nr24=c12.loc24,

                    nr25=c12.loc25,

                    nr32=c12.loc32,

                    nr33=c34.loc33,

                    nr40=c34.loc40,

                    nr41=c34.loc41,
                    nr42=c34.loc42,

                    nr47=c34.loc47,
                    nr48=c34.loc48,

                    nr49=c34.loc49,
                    nr50=c34.loc50,
                    nr51=c34.loc51,

                    nr54=c34.loc54,
                    nr55=c34.loc55,
                    nr56=c34.loc56,

                    nr57=c34.loc57,
                    nr58=c34.loc58,
                    nr59=c34.loc59,
                    nr60=c34.loc60,

                    nr61=c34.loc61,
                    nr62=c34.loc62,
                    nr63=c34.loc63,
                    nr64=c34.loc64,

                    nr36=0)

        ring1.save()
        self.stdout.write('saved Ring1 pk=%s' % ring1.pk)
        self.count += 1

    def _check(self, c12, c34):

        # TODO: check solution locs 26, 34, 31, 39 with remaining unused pieces

        # TODO: check solution locs 12, 13, 31, 39, 52, 53, 26, 34 with remaining unused pieces

        self._save(c12, c34)

    def _iter_c34(self, c12):

        used = [c12.nr1, c12.nr2, c12.nr3, c12.nr4, c12.nr5, c12.nr6, c12.nr7, c12.nr8, c12.nr9,
                c12.nr10, c12.nr11, c12.nr12, c12.nr13, c12.nr14, c12.nr15, c12.nr16, c12.nr17, c12.nr18, c12.nr19,
                c12.nr20, c12.nr21, c12.nr22, c12.nr23, c12.nr24, c12.nr25, c12.nr26, c12.nr27, c12.nr28, c12.nr29,
                c12.nr30, c12.nr31, c12.nr32, c12.nr33, c12.nr34, c12.nr35, c12.nr36, c12.nr37, c12.nr38, c12.nr39,
                c12.nr40, c12.nr41, c12.nr42, c12.nr43, c12.nr44, c12.nr45, c12.nr46, c12.nr47, c12.nr48, c12.nr49,
                c12.nr50, c12.nr51, c12.nr52, c12.nr53, c12.nr54, c12.nr55, c12.nr56, c12.nr57, c12.nr58, c12.nr59,
                c12.nr60, c12.nr61, c12.nr62, c12.nr63, c12.nr64, c12.nr65, c12.nr66, c12.nr67, c12.nr68, c12.nr69,
                c12.nr70, c12.nr71, c12.nr72, c12.nr73, c12.nr74, c12.nr75, c12.nr76, c12.nr77, c12.nr78, c12.nr79,
                c12.nr80]

        exp_s1_left = self.twoside2reverse[c12.side3_left]
        exp_s1_right = self.twoside2reverse[c12.side3_right]

        for c34 in (Corner34
                    .objects
                    .filter(seed=c12.seed,
                            side1_left=exp_s1_left,
                            side1_right=exp_s1_right)
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
                    .exclude(nr41__in=used)
                    .exclude(nr42__in=used)
                    .exclude(nr43__in=used)
                    .exclude(nr44__in=used)
                    .exclude(nr45__in=used)
                    .exclude(nr46__in=used)
                    .exclude(nr47__in=used)
                    .exclude(nr48__in=used)
                    .exclude(nr49__in=used)
                    .exclude(nr50__in=used)
                    .exclude(nr51__in=used)
                    .exclude(nr52__in=used)
                    .exclude(nr53__in=used)
                    .exclude(nr54__in=used)
                    .exclude(nr55__in=used)
                    .exclude(nr56__in=used)
                    .exclude(nr57__in=used)
                    .exclude(nr58__in=used)
                    .exclude(nr59__in=used)
                    .exclude(nr60__in=used)
                    .exclude(nr61__in=used)
                    .exclude(nr62__in=used)
                    .exclude(nr63__in=used)
                    .exclude(nr64__in=used)
                    .exclude(nr65__in=used)
                    .exclude(nr66__in=used)
                    .exclude(nr67__in=used)
                    .exclude(nr68__in=used)
                    .exclude(nr69__in=used)
                    .exclude(nr70__in=used)
                    .exclude(nr71__in=used)
                    .exclude(nr72__in=used)
                    .exclude(nr73__in=used)
                    .exclude(nr74__in=used)
                    .exclude(nr75__in=used)
                    .exclude(nr76__in=used)
                    .exclude(nr77__in=used)
                    .exclude(nr78__in=used)
                    .exclude(nr79__in=used)
                    .exclude(nr80__in=used)
                    .iterator(chunk_size=1000)):

            self._check(c12, c34)
        # for

    def _iter_c12(self, seed):
        count = 0
        print_at = 100
        for c12 in Corner12.objects.filter(seed=seed).iterator(chunk_size=1000):
            self._iter_c34(c12)

            count += 1
            if count >= print_at:
                self.stdout.write('[INFO] Tried %s Corner12' % count)
                print_at += 100
        # for

        self.stdout.write('[INFO] Tried %s Corner12' % count)

    def handle(self, *args, **options):

        seed = options['seed']

        Ring1.objects.filter(seed=seed).delete()

        try:
            self._iter_c12(seed)
        except KeyboardInterrupt:
            pass

        self.stdout.write('[INFO] Created %s Ring1' % self.count)


# end of file
