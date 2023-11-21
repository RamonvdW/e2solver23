# -*- coding: utf-8 -*-

#  Copyright (c) 2023 Ramon van der Winkel.
#  All rights reserved.
#  Licensed under BSD-3-Clause-Clear. See LICENSE file for details.

from django.core.management.base import BaseCommand
from Pieces2x2.models import TwoSides, Piece2x2


class Command(BaseCommand):

    help = "Check all 2x2 pieces"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def handle(self, *args, **options):

        self.stdout.write('[INFO] Checking all 2x2 pieces')

        """ a 2x2 piece consists of 4 base pieces, each under a certain rotation

            each side consists of 2 base piece sides and is given a new simple numeric

                     side 1
                   +---+---+
                   | 1 | 2 |
            side 4 +---+---+ side 2
                   | 3 | 4 |
                   +---+---+
                     side 3
        """

        border = TwoSides.objects.get(two_sides='XX')

        c1 = Piece2x2.objects.filter(side1=border.nr).count()
        c2 = Piece2x2.objects.filter(side2=border.nr).count()
        c3 = Piece2x2.objects.filter(side3=border.nr).count()
        c4 = Piece2x2.objects.filter(side4=border.nr).count()
        self.stdout.write('Border counts: %s, %s, %s, %s' % (c1, c2, c3, c4))

        for hint in ALL_HINT_NRS:
            c1 = Piece2x2.objects.filter(nr1=hint).count()
            c2 = Piece2x2.objects.filter(nr2=hint).count()
            c3 = Piece2x2.objects.filter(nr3=hint).count()
            c4 = Piece2x2.objects.filter(nr4=hint).count()
            self.stdout.write('Hint %s counts: %s, %s, %s, %s' % (hint, c1, c2, c3, c4))

        for p in Piece2x2.objects.all():

            # nrs, clockwise
            nrs = (p.nr1, p.nr2, p.nr4, p.nr3)

            # rotate 1x
            nrs2 = nrs[-1] + nrs[:3]
            check = Piece2x2.objects.filter(nr1=nrs[0], nr2=nrs[1], nr3=nrs[2], nr4=nrs[3])
            if not check:
                self.stdout.write('[ERROR] Could not locate rotation variant 1 of %s' % p.nr)

            # rotate 2x
            nrs2 = nrs[-1] + nrs[:3]
            check = Piece2x2.objects.filter(nr1=nrs[0], nr2=nrs[1], nr3=nrs[2], nr4=nrs[3])
            if not check:
                self.stdout.write('[ERROR] Could not locate rotation variant 2 of %s' % p.nr)

            # rotate 3x
            nrs2 = nrs[-1] + nrs[:3]
            check = Piece2x2.objects.filter(nr1=nrs[0], nr2=nrs[1], nr3=nrs[2], nr4=nrs[3])
            if not check:
                self.stdout.write('[ERROR] Could not locate rotation variant 3 of %s' % p.nr)
        # for

# end of file
