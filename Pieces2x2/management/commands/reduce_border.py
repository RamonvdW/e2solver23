# -*- coding: utf-8 -*-

#  Copyright (c) 2024 Ramon van der Winkel.
#  All rights reserved.
#  Licensed under BSD-3-Clause-Clear. See LICENSE file for details.

from django.core.management.base import BaseCommand
from BasePieces.pieces_1x1 import INTERNAL_BORDER_SIDES
from Pieces2x2.models import TwoSide, TwoSideOptions


class Command(BaseCommand):

    help = "Reduce the outer border to 1 workable solution"

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

        self._used_options = list()
        self._segment_done = list()

    def add_arguments(self, parser):
        parser.add_argument('processor', type=int, help='Processor to use')
        parser.add_argument('variant', type=int, help='Variant to use')

    def handle(self, *args, **options):
        processor = options['processor']
        variant = options['variant']

        self.stdout.write('[INFO] processor=%s, variant=%s' % (processor, variant))

        segments1 = (130, 131, 132, 133, 134, 135, 136,
                     57, 49, 41, 33, 25, 17, 9)

        segments2 = (16, 24, 32, 40, 48, 56, 64,
                     192, 191, 190, 189, 188, 187, 186)

        borders = INTERNAL_BORDER_SIDES * 10
        borders = borders[variant:]
        borders = borders[:len(segments1) + len(segments2)]
        self.stdout.write('[INFO] Borders = %s' % borders)

        for segment in segments1:
            keep = borders[0]
            borders = borders[1:]

            nrs = list(TwoSide.objects.filter(two_sides__startswith=keep).values_list('nr', flat=True))

            qset = TwoSideOptions.objects.filter(processor=processor, segment=segment, two_side__in=nrs)
            qset.delete()
            # self.stdout.write('segment=%s, keep=%s, count=%s' % (segment, keep, qset.count()))
        # for

        for segment in segments2:
            keep = borders[0]
            borders = borders[1:]

            nrs = list(TwoSide.objects.filter(two_sides__endswith=keep).values_list('nr', flat=True))

            qset = TwoSideOptions.objects.filter(processor=processor, segment=segment, two_side__in=nrs)
            qset.delete()
            # self.stdout.write('segment=%s, keep=%s, count=%s' % (segment, keep, qset.count()))
        # for



# end of file
