# -*- coding: utf-8 -*-

#  Copyright (c) 2023 Ramon van der Winkel.
#  All rights reserved.
#  Licensed under BSD-3-Clause-Clear. See LICENSE file for details.

from django.core.management.base import BaseCommand
from Bars12x2.models import Bar12x2
from BasePieces.hints import HINT_NRS
from BasePieces.models import BasePiece
from Pieces2x2.models import Piece2x2, TwoSides


class Command(BaseCommand):

    help = "Generate all 8x2 pieces along the border"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # load all TwoSides and calculate to what number it matches
        self.side_nr2reverse = dict()       # [side nr] = reverse side nr

        two_sides2nr = dict()   # ['XX'] = nr
        for two in TwoSides.objects.all():
            two_sides2nr[two.two_sides] = two.nr
        # for
        for two in TwoSides.objects.all():
            reverse = two.two_sides[1] + two.two_sides[0]
            try:
                self.side_nr2reverse[two.nr] = two_sides2nr[reverse]
            except KeyError:
                self.side_nr2reverse[two.nr] = 9999   # bestaat niet
        # for

        self.nr = 0

    def add_arguments(self, parser):
        hints_str = ", ".join([str(nr) for nr in HINT_NRS])
        parser.add_argument('hint', nargs=1, help="Hint for top-left corner (%s)" % hints_str)

    def _find_2x2_h1(self, used_nrs, hint_nr):
        # hint number is expected in the top-left corner
        for p in Piece2x2.objects.filter(nr1=hint_nr).exclude(nr2__in=used_nrs).exclude(nr3__in=used_nrs).exclude(nr4__in=used_nrs):
            used_nrs2 = used_nrs + (p.nr1, p.nr2, p.nr3, p.nr4)
            exp_side4 = self.side_nr2reverse[p.side2]
            yield p, used_nrs, exp_side4

    def _find_2x2_side4(self, used_nrs, exp_side4):
        for p in Piece2x2.objects.filter(side4=exp_side4).exclude(nr1__in=used_nrs).exclude(nr2__in=used_nrs).exclude(nr3__in=used_nrs).exclude(nr4__in=used_nrs):
            used_nrs2 = used_nrs + (p.nr1, p.nr2, p.nr3, p.nr4)
            exp_side4 = self.side_nr2reverse[p.side2]
            yield p, used_nrs2, exp_side4

    @staticmethod
    def _find_2x2_side4_h2(used_nrs, exp_side4):
        for p in Piece2x2.objects.filter(side4=exp_side4).filter(nr2__in=HINT_NRS).exclude(nr1__in=used_nrs).exclude(nr2__in=used_nrs).exclude(nr3__in=used_nrs).exclude(nr4__in=used_nrs):
            yield p

    def handle(self, *args, **options):
        try:
            hint_nr = int(options['hint'][0])
        except ValueError:
            hint_nr = 0
        if hint_nr not in HINT_NRS:
            self.stdout.write('[ERROR] Unsupported hint number (%s)' % repr(options['hint'][0]))
            return

        base_nr = hint_nr * 10 * 1000000   # 10M spread

        # delete all previously generate 8x2 pieces
        Bar12x2.objects.filter(h1=hint_nr).delete()

        bulk = list()
        used_nrs0 = (139,)
        for p1, used_nrs1, p2_exp_side4 in self._find_2x2_h1(used_nrs0, hint_nr):

            for p2, used_nrs2, p3_exp_side4 in self._find_2x2_side4(used_nrs1, p2_exp_side4):

                for p3, used_nrs3, p4_exp_side4 in self._find_2x2_side4(used_nrs2, p3_exp_side4):

                    for p4, used_nrs4, p5_exp_side4 in self._find_2x2_side4(used_nrs3, p4_exp_side4):

                        for p5, used_nrs5, p6_exp_side4 in self._find_2x2_side4(used_nrs4, p5_exp_side4):

                            for p6 in self._find_2x2_side4_h2(used_nrs5, p6_exp_side4):

                                self.nr += 1
                                bar = Bar12x2(
                                            nr=base_nr + self.nr,
                                            h1=p1.nr1,
                                            h2=p6.nr2,
                                            p1=p1.nr,
                                            p2=p2.nr,
                                            p3=p3.nr,
                                            p4=p4.nr,
                                            p5=p5.nr,
                                            p6=p6.nr)

                                bulk.append(bar)
                                if len(bulk) >= 10000:
                                    Bar12x2.objects.bulk_create(bulk)
                                    bulk = list()
                                    print(self.nr)
                            # for
                        # for
                    # for
                # for
            # for
        # for

        if len(bulk):
            Bar12x2.objects.bulk_create(bulk)

        self.stdout.write('[INFO] Total generated: %s' % self.nr)

# end of file
