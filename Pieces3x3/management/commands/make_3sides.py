# -*- coding: utf-8 -*-

#  Copyright (c) 2023 Ramon van der Winkel.
#  All rights reserved.
#  Licensed under BSD-3-Clause-Clear. See LICENSE file for details.

from django.core.management.base import BaseCommand
from BasePieces.pieces_1x1 import INTERNAL_SIDES
from Pieces3x3.models import ThreeSide


class Command(BaseCommand):

    help = "Generate all ThreeSides"

    def handle(self, *args, **options):

        self.stdout.write('[INFO] Filling caches')

        self.stdout.write('[INFO] Deleting all ThreeSide objects')
        ThreeSide.objects.all().delete()

        bulk = list()
        nr = 0
        for side1 in INTERNAL_SIDES:
            for side2 in INTERNAL_SIDES:
                for side3 in INTERNAL_SIDES:
                    nr += 1
                    three = ThreeSide(nr=nr,
                                      three_sides=side1 + side2 + side3)
                    bulk.append(three)
                # for
            # for
        # for

        self.stdout.write('[INFO] Creating %s ThreeSides' % len(bulk))
        ThreeSide.objects.bulk_create(bulk)


# end of file
