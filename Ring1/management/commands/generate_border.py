# -*- coding: utf-8 -*-

#  Copyright (c) 2024 Ramon van der Winkel.
#  All rights reserved.
#  Licensed under BSD-3-Clause-Clear. See LICENSE file for details.

from django.core.management.base import BaseCommand
from BasePieces.border import GenerateBorder
from BasePieces.hints import ALL_HINT_NRS
from Pieces2x2.models import Piece2x2


class Command(BaseCommand):

    help = "Generate solutions for the outer border ring"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.unused = list()

    def add_arguments(self, parser):
        parser.add_argument('seed', type=int, help='Randomization seed')

    def _make_used(self, p_nrs: tuple | list):
        for nr in p_nrs:
            self.unused.remove(nr)
        # for

    def _make_unused(self, p_nrs: tuple | list):
        self.unused.extend(p_nrs)

    def _check_usable(self, sol):
        self.bcb1 = sol[:15]
        self.bcb2 = sol[15:30]
        self.bcb3 = sol[30:45]
        self.bcb4 = sol[45:]

        c1 = self.bcb1[6:6+3]
        c2 = self.bcb2[6:6+3]
        c3 = self.bcb3[6:6+3]
        c4 = self.bcb4[6:6+3]

        b_loc2 = self.bcb1[9:9+2]
        b_loc9 = self.bcb1[4:4+2]
        b_loc7 = self.bcb2[4:4 + 2]
        b_loc16 = self.bcb2[9:9 + 2]

        self.unused = list(range(1, 256+1))
        for nr in ALL_HINT_NRS:
            self.unused.remove(nr)
        # for

        for p_loc1 in Piece2x2.objects.filter(nr3=c1[0], nr1=c1[1], nr2=c1[2]):
            exp_loc2_s4 = p_loc1.side2
            exp_loc9_s1 = p_loc1.side3
            p_nrs_loc1 = (p_loc1.nr1, p_loc1.nr2, p_loc1.nr3, p_loc1.nr4)
            self._make_used(p_nrs_loc1)

            for p_loc8 in Piece2x2.objects.filter(nr1=c2[0], nr2=c2[1], nr4=c2[2],
                                                  nr3__in=self.unused):
                exp_loc7_s2 = p_loc8.side4
                exp_loc16_s1 = p_loc8.side3

                p_nrs_loc8 = (p_loc8.nr1, p_loc8.nr2, p_loc8.nr3, p_loc8.nr4)
                self._make_used(p_nrs_loc8)

                for p_loc64 in Piece2x2.objects.filter(nr2=c3[0], nr4=c3[1], nr3=c3[2],
                                                       nr1__in=self.unused):
                    p_nrs_loc64 = (p_loc64.nr1, p_loc64.nr2, p_loc64.nr3, p_loc64.nr4)
                    self._make_used(p_nrs_loc64)

                    for p_loc57 in Piece2x2.objects.filter(nr4=c4[0], nr3=c4[1], nr1=c4[2],
                                                           nr2__in=self.unused):
                        p_nrs_loc57 = (p_loc57.nr1, p_loc57.nr2, p_loc57.nr3, p_loc57.nr4)
                        self._make_used(p_nrs_loc57)

                        for p_loc2 in Piece2x2.objects.filter(nr1=b_loc2[0], nr2=b_loc2[1],
                                                              nr3__in=self.unused, nr4__in=self.unused,
                                                              side4=exp_loc2_s4):
                            p_nrs_loc2 = (p_loc2.nr1, p_loc2.nr2, p_loc2.nr3, p_loc2.nr4)
                            self._make_used(p_nrs_loc2)

                            for p_loc9 in Piece2x2.objects.filter(nr3=b_loc9[0], nr1=b_loc9[1],
                                                                  nr2__in=self.unused, nr4__in=self.unused,
                                                                  side1=exp_loc9_s1):
                                p_nrs_loc9 = (p_loc9.nr1, p_loc9.nr2, p_loc9.nr3, p_loc9.nr4)
                                self._make_used(p_nrs_loc9)

                                for p_loc7 in Piece2x2.objects.filter(nr1=b_loc7[0], nr2=b_loc7[1],
                                                                      nr3__in=self.unused, nr4__in=self.unused,
                                                                      side2=exp_loc7_s2):
                                    p_nrs_loc7 = (p_loc7.nr1, p_loc7.nr2, p_loc7.nr3, p_loc7.nr4)
                                    self._make_used(p_nrs_loc7)

                                    qset = Piece2x2.objects.filter(nr2=b_loc16[0], nr4=b_loc16[1],
                                                                   nr1__in=self.unused, nr3__in=self.unused,
                                                                   side1=exp_loc16_s1)
                                    if qset.count() > 0:
                                        return True

                                    self._make_unused(p_nrs_loc7)
                                # for

                                self._make_unused(p_nrs_loc9)
                            # for

                            self._make_unused(p_nrs_loc2)
                        # for

                        self._make_unused(p_nrs_loc57)
                    # for

                    self._make_unused(p_nrs_loc64)
                # for

                self._make_unused(p_nrs_loc8)
            # for

            self._make_unused(p_nrs_loc1)
        # for

        print('DEAD-END: %s, %s, %s, %s' % (repr(c1), repr(c2), repr(c3), repr(c4)))
        return False

    def handle(self, *args, **options):
        seed = options['seed']
        gen = GenerateBorder(seed)
        for sol in gen.iter_solutions():

            chk = frozenset(sol)
            if len(chk) != len(sol):
                print('BAD solution: %s' % repr(sol))
                chk = list(frozenset(sol))
                chk.sort()
                print('              %s' % repr(chk))
                sol.sort()
                print('              %s' % repr(sol))
                continue        # with the for

            if not self._check_usable(sol):
                print('DEAD-END solution: %s' % repr(sol))
                continue        # with the for

            print('solution: %s' % repr(sol))

# end of file
