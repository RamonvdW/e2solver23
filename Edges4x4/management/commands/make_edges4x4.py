# -*- coding: utf-8 -*-

#  Copyright (c) 2023-2024 Ramon van der Winkel.
#  All rights reserved.
#  Licensed under BSD-3-Clause-Clear. See LICENSE file for details.

from django.core.management.base import BaseCommand
from Pieces2x2.models import TwoSide, Piece2x2
from Edges4x4.models import FourSides, Edge4x4


class Command(BaseCommand):

    help = "Make all 4x4 edges"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.twoside_border = TwoSide.objects.get(two_sides='XX').nr
        self.side_nr2reverse = dict()
        self.nr2two = dict()
        two2nr = dict()
        for two in TwoSide.objects.all():
            two2nr[two.two_sides] = two.nr
            self.nr2two[two.nr] = two.two_sides
        # for
        for two_sides, nr in two2nr.items():
            two_rev = two_sides[1] + two_sides[0]
            rev_nr = two2nr[two_rev]
            self.side_nr2reverse[nr] = rev_nr
        # for
        self.four2nr = dict()

    def _make_all_four_sides(self):
        # base pieces 1..4 are corners
        # base pieces 5..60 are borders (14x4 = 56)
        # base pieces have 17 unique sides (excluding borders)
        sides = (Piece2x2
                 .objects
                 .filter(nr1__gt=60, nr2__gt=60, nr3__gt=60, nr4__gt=60)
                 .distinct('side1')
                 .values_list('side1', flat=True))
        sides = list(sides)
        # 17x17 = 289
        if len(sides) != 289:
            raise ValueError('Wrong number of Piece2x2 sides')

        count = FourSides.objects.count()
        if count != 289*289:
            self.stdout.write('[INFO] Generating FourSides (was: %s)' % count)
            FourSides.objects.all().delete()
            sides.sort()
            bulk = []
            nr = 1
            for side1 in sides:
                for side2 in sides:
                    four_sides = self.nr2two[side1] + self.nr2two[side2]
                    four = FourSides(nr=nr, four_sides=four_sides)
                    bulk.append(four)
                    nr += 1
                    if len(bulk) >= 1000:
                        FourSides.objects.bulk_create(bulk)
                        bulk = []
                # for
            # for
            FourSides.objects.bulk_create(bulk)

        # load all FourSides
        for four in FourSides.objects.all():
            self.four2nr[four.four_sides] = four.nr
        # for

    def _get_four(self, nr1, nr2):
        four_sides = self.nr2two[nr1] + self.nr2two[nr2]
        return self.four2nr[four_sides]

    def handle(self, *args, **options):

        """ a 4x4 edge consists of 4 Piece2x2

                     side 1
                   +---+---+
                   | 1 | 2 |
            side 4 +---+---+ side 2
                   | 3 | 4 |
                   +---+---+
                     side 3
        """

        # make all FourSides
        self._make_all_four_sides()

        qset = (Piece2x2
                .objects
                .exclude(side1=self.twoside_border)
                .exclude(side2=self.twoside_border)
                .exclude(side3=self.twoside_border)
                .exclude(side4=self.twoside_border))

        last = Edge4x4.objects.order_by('nr').last()
        if last:
            nr = last.nr
        else:
            nr = 0

        bulk = []
        for p1 in qset.all().iterator(chunk_size=1000):

            print('p1: %s' % p1.nr)

            p2_exp_s4 = self.side_nr2reverse[p1.side2]
            p3_exp_s1 = self.side_nr2reverse[p1.side3]

            for p2 in qset.filter(side4=p2_exp_s4).iterator(chunk_size=1000):
                p4_exp_s1 = self.side_nr2reverse[p2.side3]

                for p3 in qset.filter(side1=p3_exp_s1).iterator(chunk_size=1000):
                    p4_exp_s4 = self.side_nr2reverse[p3.side2]

                    for p4 in qset.filter(side1=p4_exp_s1, side4=p4_exp_s4):

                        # make the edges, clockwise order
                        side1 = self._get_four(p1.side1, p2.side1)
                        side2 = self._get_four(p2.side2, p4.side2)
                        side3 = self._get_four(p4.side3, p3.side3)
                        side4 = self._get_four(p3.side4, p1.side4)

                        if not Edge4x4.objects.filter(side1=side1, side2=side2, side3=side3, side4=side4).first():
                            nr += 1
                            edge = Edge4x4(nr=nr, side1=side1, side2=side2, side3=side3, side4=side4)
                            bulk.append(edge)

                            if len(bulk) > 1000:
                                Edge4x4.objects.bulk_create(bulk)
                                bulk = []
                                print(nr)
                    # for
                # for
            # for
        # for

        if len(bulk) > 1000:
            Edge4x4.objects.bulk_create(bulk)

# end of file
