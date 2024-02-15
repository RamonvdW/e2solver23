# -*- coding: utf-8 -*-

#  Copyright (c) 2024 Ramon van der Winkel.
#  All rights reserved.
#  Licensed under BSD-3-Clause-Clear. See LICENSE file for details.

from django.core.management.base import BaseCommand
from Pieces2x2.models import TwoSide
from Ring1.models import Ring1, Corner12, Corner34, Corner1, Corner2, Corner3, Corner4


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

    def _save(self, c1: Corner1, c2: Corner2, c3: Corner3, c4: Corner4):
        ring1 = Ring1(
                    seed=c1.seed,

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
        self.stdout.write('saved Ring1 pk=%s' % ring1.pk)
        self.count += 1

    def _check(self, c12, c34):

        used = [c12.nr1, c12.nr2, c12.nr3, c12.nr4, c12.nr5, c12.nr6, c12.nr7, c12.nr8, c12.nr9,
                c12.nr10, c12.nr11, c12.nr12, c12.nr13, c12.nr14, c12.nr15, c12.nr16, c12.nr17, c12.nr18, c12.nr19,
                c12.nr20, c12.nr21, c12.nr22, c12.nr23, c12.nr24, c12.nr25, c12.nr26, c12.nr27, c12.nr28, c12.nr29,
                c12.nr30, c12.nr31, c12.nr32, c12.nr33, c12.nr34, c12.nr35, c12.nr36, c12.nr37, c12.nr38, c12.nr39,
                c12.nr40, c12.nr41, c12.nr42, c12.nr43, c12.nr44, c12.nr45, c12.nr46, c12.nr47, c12.nr48, c12.nr49,
                c12.nr50, c12.nr51, c12.nr52, c12.nr53, c12.nr54, c12.nr55, c12.nr56, c12.nr57, c12.nr58, c12.nr59,
                c12.nr60, c12.nr61, c12.nr62, c12.nr63, c12.nr64, c12.nr65, c12.nr66, c12.nr67, c12.nr68, c12.nr69,
                c12.nr70, c12.nr71, c12.nr72, c12.nr73, c12.nr74, c12.nr75, c12.nr76, c12.nr77, c12.nr78, c12.nr79,
                c12.nr80,
                c34.nr1, c34.nr2, c34.nr3, c34.nr4, c34.nr5, c34.nr6, c34.nr7, c34.nr8, c34.nr9,
                c34.nr10, c34.nr11, c34.nr12, c34.nr13, c34.nr14, c34.nr15, c34.nr16, c34.nr17, c34.nr18, c34.nr19,
                c34.nr20, c34.nr21, c34.nr22, c34.nr23, c34.nr24, c34.nr25, c34.nr26, c34.nr27, c34.nr28, c34.nr29,
                c34.nr30, c34.nr31, c34.nr32, c34.nr33, c34.nr34, c34.nr35, c34.nr36, c34.nr37, c34.nr38, c34.nr39,
                c34.nr40, c34.nr41, c34.nr42, c34.nr43, c34.nr44, c34.nr45, c34.nr46, c34.nr47, c34.nr48, c34.nr49,
                c34.nr50, c34.nr51, c34.nr52, c34.nr53, c34.nr54, c34.nr55, c34.nr56, c34.nr57, c34.nr58, c34.nr59,
                c34.nr60, c34.nr61, c34.nr62, c34.nr63, c34.nr64, c34.nr65, c34.nr66, c34.nr67, c34.nr68, c34.nr69,
                c34.nr70, c34.nr71, c34.nr72, c34.nr73, c34.nr74, c34.nr75, c34.nr76, c34.nr77, c34.nr78, c34.nr79,
                c34.nr80]

        c1 = Corner1.objects.get(nr=c12.c1)
        c2 = Corner2.objects.get(nr=c12.c2)
        c3 = Corner3.objects.get(nr=c34.c3)
        c4 = Corner4.objects.get(nr=c34.c4)

        # TODO: check solution locs 26, 34, 31, 39 with remaining unused pieces

        # TODO: check solution locs 12, 13, 31, 39, 52, 53, 26, 34 with remaining unused pieces

        self._save(c1, c2, c3, c4)

    def _iter_c34(self, c12):

        # only the border pieces can overlap
        used = [
            # nr 10
            # c12.nr1, c12.nr2, c12.nr3, c12.nr4,
            # nr 9
            c12.nr5,  # c12.nr6,
            c12.nr7,  # c12.nr8,
            # nr 1
            c12.nr9, c12.nr10, c12.nr11,  # c12.nr12,
            # nr 2
            c12.nr13, c12.nr14,  # c12.nr15, c12.nr16,
            # nr 3
            c12.nr17, c12.nr18,  # c12.nr19, c12.nr20,
            # nr 11
            # c12.nr21, c12.nr22, c12.nr23, c12.nr24,
            # nr 17
            c12.nr25,  # c12.nr26,
            c12.nr27,  # c12.nr28,
            # nr 18
            # c12.nr29, c12.nr30, c12.nr31, c12.nr32,
            # nr 25
            c12.nr33,  # c12.nr34,
            c12.nr35,  # c12.nr36,
            # nr 4
            c12.nr37, c12.nr38,  # c12.nr39, c12.nr40,
            # nr 15
            # c12.nr41, c12.nr42, c12.nr43, c12.nr44,
            # nr 16
            # c12.nr45,
            c12.nr46,
            # c12.nr47,
            c12.nr48,
            # nr 8
            c12.nr49, c12.nr50,
            # c12.nr51,
            c12.nr52,
            # nr 7
            c12.nr53, c12.nr54,  # c12.nr55, c12.nr56,
            # nr 6
            c12.nr57, c12.nr58,  # c12.nr59, c12.nr60,
            # nr 14
            # c12.nr61, c12.nr62, c12.nr63, c12.nr64,
            # nr 24
            # c12.nr65,
            c12.nr66,
            # c12.nr67,
            c12.nr68,
            # nr 23
            # c12.nr69, c12.nr70, c12.nr71, c12.nr72,
            # nr 32
            # c12.nr73,
            c12.nr74,
            # c12.nr75,
            c12.nr76,
            # nr 5
            c12.nr77, c12.nr78,  # c12.nr79, c12.nr80
        ]

        exp_s1_left = self.twoside2reverse[c12.side3_left]
        exp_s1_right = self.twoside2reverse[c12.side3_right]

        for c34 in (Corner34
                    .objects
                    .filter(seed=c12.seed,
                            side1_left=exp_s1_left,
                            side1_right=exp_s1_right)
                    # nr 55
                    # .exclude(nr1__in=used)
                    # .exclude(nr2__in=used)
                    # .exclude(nr3__in=used)
                    # .exclude(nr4__in=used)
                    # nr 56
                    # .exclude(nr5__in=used)
                    .exclude(nr6__in=used)
                    # .exclude(nr7__in=used)
                    .exclude(nr8__in=used)
                    # nr 64
                    # .exclude(nr9__in=used)
                    .exclude(nr10__in=used)
                    .exclude(nr11__in=used)
                    .exclude(nr12__in=used)
                    # nr 63
                    # .exclude(nr13__in=used)
                    # .exclude(nr14__in=used)
                    .exclude(nr15__in=used)
                    .exclude(nr16__in=used)
                    # 62
                    # .exclude(nr17__in=used)
                    # .exclude(nr18__in=used)
                    .exclude(nr19__in=used)
                    .exclude(nr20__in=used)
                    # 54
                    # .exclude(nr21__in=used)
                    # .exclude(nr22__in=used)
                    # .exclude(nr23__in=used)
                    # .exclude(nr24__in=used)
                    # 48
                    # .exclude(nr25__in=used)
                    .exclude(nr26__in=used)
                    # .exclude(nr27__in=used)
                    .exclude(nr28__in=used)
                    # 47
                    # .exclude(nr29__in=used)
                    # .exclude(nr30__in=used)
                    # .exclude(nr31__in=used)
                    # .exclude(nr32__in=used)
                    # 40
                    # .exclude(nr33__in=used)
                    .exclude(nr34__in=used)
                    # .exclude(nr35__in=used)
                    .exclude(nr36__in=used)
                    # 61
                    # .exclude(nr37__in=used)
                    # .exclude(nr38__in=used)
                    .exclude(nr39__in=used)
                    .exclude(nr40__in=used)
                    # 50
                    # .exclude(nr41__in=used)
                    # .exclude(nr42__in=used)
                    # .exclude(nr43__in=used)
                    # .exclude(nr44__in=used)
                    # 49
                    .exclude(nr45__in=used)
                    # .exclude(nr46__in=used)
                    .exclude(nr47__in=used)
                    # .exclude(nr48__in=used)
                    # 57
                    .exclude(nr49__in=used)
                    # .exclude(nr50__in=used)
                    .exclude(nr51__in=used)
                    .exclude(nr52__in=used)
                    # 58
                    # .exclude(nr53__in=used)
                    # .exclude(nr54__in=used)
                    .exclude(nr55__in=used)
                    .exclude(nr56__in=used)
                    # 59
                    # .exclude(nr57__in=used)
                    # .exclude(nr58__in=used)
                    .exclude(nr59__in=used)
                    .exclude(nr60__in=used)
                    # 51
                    # .exclude(nr61__in=used)
                    # .exclude(nr62__in=used)
                    # .exclude(nr63__in=used)
                    # .exclude(nr64__in=used)
                    # 41
                    .exclude(nr65__in=used)
                    # .exclude(nr66__in=used)
                    .exclude(nr67__in=used)
                    # .exclude(nr68__in=used)
                    # 42
                    # .exclude(nr69__in=used)
                    # .exclude(nr70__in=used)
                    # .exclude(nr71__in=used)
                    # .exclude(nr72__in=used)
                    # 33
                    .exclude(nr73__in=used)
                    # .exclude(nr74__in=used)
                    .exclude(nr75__in=used)
                    # .exclude(nr76__in=used)
                    # 60
                    # .exclude(nr77__in=used)
                    # .exclude(nr78__in=used)
                    .exclude(nr79__in=used)
                    .exclude(nr80__in=used)
                    .iterator(chunk_size=1000)):

            self._check(c12, c34)
        # for

    def _iter_c12(self, seed):
        count = 0
        print_at = 10
        for c12 in Corner12.objects.filter(seed=seed).iterator(chunk_size=1000):
            self._iter_c34(c12)

            count += 1
            if count >= print_at:
                self.stdout.write('[INFO] Tried %s Corner12' % count)
                print_at += 10
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
