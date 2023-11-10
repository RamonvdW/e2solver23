# -*- coding: utf-8 -*-

#  Copyright (c) 2023 Ramon van der Winkel.
#  All rights reserved.
#  Licensed under BSD-3-Clause-Clear. See LICENSE file for details.

# maak een account HWL van specifieke vereniging, vanaf de commandline

from django.core.management.base import BaseCommand
from BasePieces.models import BasePiece
from Borders4x2.models import Border4x2


class Command(BaseCommand):

    help = "Generate all 8x2 pieces along the border"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.skip_base_nrs = (181, 208, 249, 255, 139)

        self.nr_side_rot2side = dict()    # [(base piece nr, side, rot)] = "A"

        for piece in BasePiece.objects.all():
            for side in range(4):
                for rot in range(4):
                    self.nr_side_rot2side[(piece.nr, side, rot)] = piece.get_side(side, rot)
                # for
            # for
        # for

    def handle(self, *args, **options):
        """
                      side1 = border
                    +---+---+---+---+
                    | 1 | 2 | 3 | 4 |
             side 4 +---+---+---+---+ side 2
                    | 5 | 6 | 7 | 8 |
                    +---+---+---+---+
                          side 3
        """
        count = 0
        bulk = list()
        for border in Border4x2.objects.all().iterator(chunk_size=10000):

            s5 = self.nr_side_rot2side[border.nr5, 3, border.rot5]
            s6 = self.nr_side_rot2side[border.nr6, 3, border.rot6]
            s7 = self.nr_side_rot2side[border.nr7, 3, border.rot7]
            s8 = self.nr_side_rot2side[border.nr8, 3, border.rot8]

            border.side3 = s8 + s7 + s6 + s5

            bulk.append(border)

            if len(bulk) == 5000:
                count += len(bulk)
                self.stdout.write('%s' % count)
                Border4x2.objects.bulk_update(bulk, ['side3'])
                bulk = list()
        # for

        if len(bulk):
            count += len(bulk)
            self.stdout.write('%s' % count)
            Border4x2.objects.bulk_update(bulk, ['side3'])

        self.stdout.write('[INFO] Done!')

# end of file
