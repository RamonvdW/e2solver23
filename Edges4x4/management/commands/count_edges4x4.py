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

        self.stdout.write('[INFO] Loading FourSides')

        nr2side2 = dict()
        nr2side3 = dict()
        for four in FourSides.objects.all():
            # last half of side2 is interesting
            nr2side2[four.nr] = four.four_sides[2:]

            # first half of side3 is interesting
            nr2side3[four.nr] = four.four_sides[:2]
        # for

        all_long_sides = []
        print_len = 1000
        count = 0
        for edge in Edge4x4.objects.distinct('side2', 'side3').iterator(chunk_size=10000):
            count += 1
            long_side = nr2side2[edge.side2] + nr2side2[edge.side3]
            if long_side not in all_long_sides:
                all_long_sides.append(long_side)
                if len(all_long_sides) == print_len:
                    self.stdout.write('[INFO] Aantal %s; aantal long_sides: %s' % (count, print_len))
                    print_len = len(all_long_sides) + 1000
        # for

        print('[INFO] Aantal long_sides: %s' % len(all_long_sides))

# end of file
