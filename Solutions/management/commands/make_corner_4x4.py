# -*- coding: utf-8 -*-

#  Copyright (c) 2024 Ramon van der Winkel.
#  All rights reserved.
#  Licensed under BSD-3-Clause-Clear. See LICENSE file for details.

from django.core.management.base import BaseCommand
from BasePieces.hints import ALL_HINT_NRS, ALL_CORNER_NRS
from Pieces2x2.models import Piece2x2
import time


class Command(BaseCommand):

    help = "Make all corner + hint with four 2x2"

    """
        +---+---+
        | 1 | 2 |
        +---+---+
        | 3 | 4 |
        +---+---+
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.bad_nrs = list()
        self.bad_nrs.extend(ALL_HINT_NRS)
        self.bad_nrs.extend(ALL_CORNER_NRS)

        self.count = 0
        self.prev_tick = time.monotonic()

    def add_arguments(self, parser):
        parser.add_argument('corner', type=int, help='Which corner to work on (1..4)')

    def _found(self, p1, p2, p3, p4):
        self.count += 1

        tick = time.monotonic()
        if tick > self.prev_tick + 5:
            self.prev_tick = tick
            print('count: %s' % self.count)

        # TODO: extract useful information: sides, base pieces, etc.

    def _find_corner4(self):
        """
            +---+---+
            | 1 | 2 |       2 = hint: nr3=181
            +---+---+
            | 3 | 4 |       3 = corner: nr3=1..4
            +---+---+
        """
        print('corner: 4')

        qset_corner = Piece2x2.objects.filter(nr3__in=ALL_CORNER_NRS)
        qset_hint = Piece2x2.objects.filter(nr3=181)
        print('p2x2 corner: %s' % qset_corner.count())
        print('p2x2 hint:   %s' % qset_hint.count())

        left = qset_corner.count()
        for p3 in qset_corner:
            print('Corner left: %s' % left)
            left -= 1

            exp_p1_side3 = p3.side1
            exp_p4_side4 = p3.side2
            used3 = [p3.nr1, p3.nr2, p3.nr4]

            for p2 in qset_hint.exclude(nr1__in=used3).exclude(nr2__in=used3).exclude(nr4__in=used3):
                exp_p4_side1 = p2.side3
                exp_p1_side2 = p2.side4
                used23 = used3[:]
                used23.extend([p2.nr1, p2.nr2, p2.nr4])
                used23.extend(self.bad_nrs)

                for p1 in (Piece2x2.objects
                           .filter(side3=exp_p1_side3,
                                   side2=exp_p1_side2)
                           .exclude(nr1__in=used23)
                           .exclude(nr2__in=used23)
                           .exclude(nr3__in=used23)
                           .exclude(nr4__in=used23)):

                    used123 = used23[:]
                    used123.extend([p1.nr1, p1.nr2, p1.nr3, p1.nr4])

                    for p4 in (Piece2x2
                               .objects
                               .filter(side1=exp_p4_side1,
                                       side4=exp_p4_side4)
                               .exclude(nr1__in=used123)
                               .exclude(nr2__in=used123)
                               .exclude(nr3__in=used123)
                               .exclude(nr4__in=used123)):

                        self._found(p1, p2, p3, p4)
                    # for
                # for
            # for
        # for

        print('Total solutions: %s' % self.count)

    def _find_corner3(self):
        """
            +---+---+
            | 1 | 2 |       4 = corner: nr4=1..4
            +---+---+
            | 3 | 4 |       1 = hint: nr4=249
            +---+---+
        """
        print('corner: 3')

        qset_corner = Piece2x2.objects.filter(nr4__in=ALL_CORNER_NRS)
        qset_hint = Piece2x2.objects.filter(nr4=249)
        print('p2x2 corner: %s' % qset_corner.count())
        print('p2x2 hint:   %s' % qset_hint.count())

        left = qset_corner.count()
        for p4 in qset_corner:
            print('Corner left: %s' % left)
            left -= 1

            exp_p2_side3 = p4.side1
            exp_p3_side2 = p4.side4
            used4 = [p4.nr1, p4.nr2, p4.nr3]

            for p1 in qset_hint.exclude(nr1__in=used4).exclude(nr2__in=used4).exclude(nr3__in=used4):
                exp_p2_side4 = p1.side2
                exp_p3_side1 = p1.side3
                used14 = used4[:]
                used14.extend([p1.nr1, p1.nr2, p1.nr3])
                used14.extend(self.bad_nrs)

                for p2 in (Piece2x2
                           .objects
                           .filter(side3=exp_p2_side3,
                                   side4=exp_p2_side4)
                           .exclude(nr1__in=used14)
                           .exclude(nr2__in=used14)
                           .exclude(nr3__in=used14)
                           .exclude(nr4__in=used14)):

                    used124 = used14[:]
                    used124.extend([p2.nr1, p2.nr2, p2.nr3, p2.nr4])

                    for p3 in (Piece2x2
                               .objects
                               .filter(side1=exp_p3_side1,
                                       side2=exp_p3_side2)
                               .exclude(nr1__in=used124)
                               .exclude(nr2__in=used124)
                               .exclude(nr3__in=used124)
                               .exclude(nr4__in=used124)):

                        self._found(p1, p2, p3, p4)
                    # for
                # for
            # for
        # for

        print('Total solutions: %s' % self.count)

    def _find_corner2(self):
        """
            +---+---+
            | 1 | 2 |       2 = corner: nr2=1..4
            +---+---+
            | 3 | 4 |       3 = hint: nr2=255
            +---+---+
        """
        print('corner: 2')

        qset_corner = Piece2x2.objects.filter(nr2__in=ALL_CORNER_NRS)
        qset_hint = Piece2x2.objects.filter(nr2=255)
        print('p2x2 corner: %s' % qset_corner.count())
        print('p2x2 hint:   %s' % qset_hint.count())

        left = qset_corner.count()
        for p2 in qset_corner:
            print('Corner left: %s' % left)
            left -= 1

            exp_p1_side2 = p2.side4
            exp_p4_side1 = p2.side3
            used1 = [p2.nr1, p2.nr3, p2.nr4]

            for p3 in qset_hint.exclude(nr1__in=used1).exclude(nr3__in=used1).exclude(nr4__in=used1):
                exp_p1_side3 = p3.side1
                exp_p4_side4 = p3.side2
                used23 = used1[:]
                used23.extend([p3.nr1, p3.nr3, p3.nr4])
                used23.extend(self.bad_nrs)

                for p1 in (Piece2x2
                           .objects
                           .filter(side2=exp_p1_side2,
                                   side3=exp_p1_side3)
                           .exclude(nr1__in=used23)
                           .exclude(nr2__in=used23)
                           .exclude(nr3__in=used23)
                           .exclude(nr4__in=used23)):

                    used123 = used23[:]
                    used123.extend([p1.nr1, p1.nr2, p1.nr3, p1.nr4])

                    for p4 in (Piece2x2
                               .objects
                               .filter(side1=exp_p4_side1,
                                       side4=exp_p4_side4)
                               .exclude(nr1__in=used123)
                               .exclude(nr2__in=used123)
                               .exclude(nr3__in=used123)
                               .exclude(nr4__in=used123)):

                        self._found(p1, p2, p3, p4)
                    # for
                # for
            # for
        # for

        print('Total solutions: %s' % self.count)

    def _find_corner1(self):
        """
            +---+---+
            | 1 | 2 |       1 = corner: nr1=1..4
            +---+---+
            | 3 | 4 |       4 = hint: nr1=208
            +---+---+
        """
        print('corner: 1')

        qset_corner = Piece2x2.objects.filter(nr1__in=ALL_CORNER_NRS)
        qset_hint = Piece2x2.objects.filter(nr1=208)
        print('p2x2 corner: %s' % qset_corner.count())
        print('p2x2 hint: %s' % qset_hint.count())

        left = qset_corner.count()
        for p1 in qset_corner:
            print('Corner left: %s' % left)
            left -= 1

            exp_p2_side4 = p1.side2
            exp_p3_side1 = p1.side3
            used1 = [p1.nr2, p1.nr3, p1.nr4]

            for p4 in qset_hint.exclude(nr2__in=used1).exclude(nr3__in=used1).exclude(nr4__in=used1):
                exp_p2_side3 = p4.side1
                exp_p3_side2 = p4.side4
                used14 = used1[:]
                used14.extend([p4.nr2, p4.nr3, p4.nr4])
                used14.extend(self.bad_nrs)

                for p2 in (Piece2x2
                           .objects
                           .filter(side3=exp_p2_side3,
                                   side4=exp_p2_side4)
                           .exclude(nr1__in=used14)
                           .exclude(nr2__in=used14)
                           .exclude(nr3__in=used14)
                           .exclude(nr4__in=used14)):

                    used124 = used14[:]
                    used14.extend([p2.nr1, p2.nr2, p2.nr3, p2.nr4])

                    for p3 in (Piece2x2
                               .objects
                               .filter(side1=exp_p3_side1,
                                       side2=exp_p3_side2)
                               .exclude(nr1__in=used124)
                               .exclude(nr2__in=used124)
                               .exclude(nr3__in=used124)
                               .exclude(nr4__in=used124)):

                        self._found(p1, p2, p3, p4)
                    # for
                # for
            # for
        # for

        print('Total solutions: %s' % self.count)

    def handle(self, *args, **options):
        corner = options['corner']
        if corner == 1:
            self._find_corner1()
        elif corner == 2:
            self._find_corner2()
        elif corner == 3:
            self._find_corner3()
        elif corner == 4:
            self._find_corner4()
        else:
            self.stdout.write('[ERROR] Unsupported corner')

# end of file
