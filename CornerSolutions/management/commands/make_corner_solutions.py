# -*- coding: utf-8 -*-

#  Copyright (c) 2023 Ramon van der Winkel.
#  All rights reserved.
#  Licensed under BSD-3-Clause-Clear. See LICENSE file for details.

# maak een account HWL van specifieke vereniging, vanaf de commandline

from django.core.management.base import BaseCommand
from BasePieces.hints import HINT_NRS
from Pieces4x4.models import Piece4x4

USE_CACHE = True
DO_STORE = True


class Command(BaseCommand):

    help = "Generate all corner solutions"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def handle(self, *args, **options):

        """ a corner solution consists of 4 Piece4x4, each under a certain rotation
            each corner has one of the 4 hint pieces
            total solution must have 4x16 = 64 unique base pieces

                   +---+      +---+
                   |4x4|      |4x4|
                   +---+      +---+

                   +---+      +---+
                   |4x4|      |4x4|
                   +---+      +---+

            The corner is in position 1
            The hint is in position 11

               +---+---+---+---+
               | 1 | 2 | 3 | 4 |
               +---+---+---+---+
               | 5 | 6 | 7 | 8 |
               +---+---+---+---+
               | 9 |10 |11 |12 |
               +---+---+---+---+
               |13 |14 |15 |16 |
               +---+---+---+---+
        """

        hint2, hint4, hint1, hint3 = HINT_NRS

        count = 0
        for p1 in Piece4x4.objects.filter(nr11=hint1).iterator(chunk_size=10):
            base1 = [p1.nr1, p1.nr2, p1.nr3, p1.nr4, p1.nr5, p1.nr6, p1.nr7, p1.nr8,
                     p1.nr9, p1.nr10, p1.nr11, p1.nr12, p1.nr13, p1.nr14, p1.nr15, p1.nr16]

            # check = len(set(base1))
            # if check != 16:
            #     print(repr(base1))
            #     continue

            print('p1: %s' % p1.nr)

            for p2 in (Piece4x4
                       .objects
                       .filter(nr11=hint2)
                       .exclude(nr1=p1.nr1)
                       .exclude(nr2__in=base1)
                       .exclude(nr3__in=base1)
                       .exclude(nr4__in=base1)
                       .exclude(nr5__in=base1)
                       .exclude(nr6__in=base1)
                       .exclude(nr7__in=base1)
                       .exclude(nr8__in=base1)
                       .exclude(nr9__in=base1)
                       .exclude(nr10__in=base1)
                       .exclude(nr12__in=base1)
                       .exclude(nr13__in=base1)
                       .exclude(nr14__in=base1)
                       .exclude(nr15__in=base1)
                       .exclude(nr16__in=base1)
                       .iterator(chunk_size=100)):

                base2 = base1 + [p2.nr1, p2.nr2, p2.nr3, p2.nr4, p2.nr5, p2.nr6, p2.nr7, p2.nr8,
                                 p2.nr9, p2.nr10, p2.nr11, p2.nr12, p2.nr13, p2.nr14, p2.nr15, p2.nr16]

                check = len(set(base2))
                if check != 32:
                    continue

                print('p2:', p2.nr)

                for p3 in (Piece4x4
                           .objects
                           .filter(nr11=hint3)
                           .exclude(nr1__in=(p1.nr1, p2.nr1))
                           .exclude(nr2__in=base2)
                           .exclude(nr3__in=base2)
                           .exclude(nr4__in=base2)
                           .exclude(nr5__in=base2)
                           .exclude(nr6__in=base2)
                           .exclude(nr7__in=base2)
                           .exclude(nr8__in=base2)
                           .exclude(nr9__in=base2)
                           .exclude(nr10__in=base2)
                           .exclude(nr12__in=base2)
                           .exclude(nr13__in=base2)
                           .exclude(nr14__in=base2)
                           .exclude(nr15__in=base2)
                           .exclude(nr16__in=base2)
                           .iterator(chunk_size=100)):

                    base3 = base2 + [p3.nr1, p3.nr2, p3.nr3, p3.nr4, p3.nr5, p3.nr6, p3.nr7, p3.nr8,
                                     p3.nr9, p3.nr10, p3.nr11, p3.nr12, p3.nr13, p3.nr14, p3.nr15, p3.nr16]

                    check = len(set(base3))
                    if check != 48:
                        continue

                    print('p3: %s' % p3.nr)

                    for p4 in (Piece4x4
                               .objects
                               .filter(nr11=hint4)
                               .exclude(nr1__in=(p1.nr1, p2.nr1, p3.nr1))
                               .exclude(nr2__in=base3)
                               .exclude(nr3__in=base3)
                               .exclude(nr4__in=base3)
                               .exclude(nr5__in=base3)
                               .exclude(nr6__in=base3)
                               .exclude(nr7__in=base3)
                               .exclude(nr8__in=base3)
                               .exclude(nr9__in=base3)
                               .exclude(nr10__in=base3)
                               .exclude(nr12__in=base3)
                               .exclude(nr13__in=base3)
                               .exclude(nr14__in=base3)
                               .exclude(nr15__in=base3)
                               .exclude(nr16__in=base3)
                               .iterator(chunk_size=1000)):

                        base4 = base3 + [p4.nr1, p4.nr2, p4.nr3, p4.nr4, p4.nr5, p4.nr6, p4.nr7, p4.nr8,
                                         p4.nr9, p4.nr10, p4.nr11, p4.nr12, p4.nr13, p4.nr14, p4.nr15, p4.nr16]
                        check = len(set(base4))
                        if check == 64:
                            print('[Solution]:',p1.nr, p2.nr, p3.nr, p4.nr)
                            count += 1
                        else:
                            print('p4: %s (check=%s)' % (p4.nr, check))
                    # for
                # for
            # for
        # for

        print('[INFO] Totaal: %s' % count)

# end of file
