# -*- coding: utf-8 -*-

#  Copyright (c) 2023-2024 Ramon van der Winkel.
#  All rights reserved.
#  Licensed under BSD-3-Clause-Clear. See LICENSE file for details.

from django.core.management.base import BaseCommand
from Pieces2x2.models import TwoSide, TwoSideOptions, Piece2x2
from Pieces2x2.helpers import calc_segment
from WorkQueue.operations import propagate_segment_reduction, set_used, get_unused


class Command(BaseCommand):

    help = "Fix one of the corners locations to one of the 4 corner pieces"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.twoside_border = TwoSide.objects.get(two_sides='XX').nr

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

        self.processor = 0
        self.reductions = {1: 0, 2: 0, 3: 0, 4: 0}     # [side_nr] = count
        self.unused = list()

    def add_arguments(self, parser):
        # parser.add_argument('--verbose', action='store_true')
        parser.add_argument('processor', nargs=1, type=int, help='Processor number to use')
        parser.add_argument('loc', nargs=1, type=int, help='Location on board (10, 15, 50, 55, 36)')
        parser.add_argument('index', nargs=1, type=int, help='i-th Piece2x2 number to use')

    def _reverse_sides(self, options):
        return [self.twoside2reverse[two_side] for two_side in options]

    def _load_unused(self):
        self.unused = get_unused(self.processor)
        self.stdout.write('[INFO] %s base pieces in use' % (256 - len(self.unused)))

    def _get_side_options(self, loc, side_nr):
        segment = calc_segment(loc, side_nr)
        options = (TwoSideOptions
                   .objects
                   .filter(processor=self.processor,
                           segment=segment)
                   .values_list('two_side', flat=True))
        options = list(options)

        if side_nr >= 3:
            # sides 3 and 4 need to be reversed
            options = self._reverse_sides(options)

        # print('segment %s options: %s' % (segment, repr(options)))
        return options

    def _reduce(self, segment, two_side, side_nr):
        if side_nr in (3, 4):
            two_side = self.twoside2reverse[two_side]

        qset = TwoSideOptions.objects.filter(processor=self.processor, segment=segment, two_side=two_side)
        if qset.count() != 1:
            self.stderr.write('[ERROR] Cannot find segment=%s, two_side=%s' % (segment, two_side))
        else:
            self.stdout.write('[INFO] Reduction side%s: %s' % (side_nr, two_side))
            qset.delete()
            self.reductions[side_nr] += 1
            propagate_segment_reduction(self.processor, segment)

    def handle(self, *args, **options):

        loc = options['loc'][0]
        if loc not in (10, 15, 50, 55, 36):
            self.stderr.write('[ERROR] Invalid location')
            return

        self.processor = options['processor'][0]

        index = options['index'][0]

        self.stdout.write('[INFO] Processor=%s; Location: %s' % (self.processor, loc))

        self._load_unused()

        options1 = self._get_side_options(loc, 1)
        options2 = self._get_side_options(loc, 2)
        options3 = self._get_side_options(loc, 3)
        options4 = self._get_side_options(loc, 4)

        qset = Piece2x2.objects.filter(side1__in=options1, side2__in=options2, side3__in=options3, side4__in=options4)

        if loc == 10:
            qset = qset.filter(nr1=208, nr2__in=self.unused, nr3__in=self.unused, nr4__in=self.unused)
        elif loc == 15:
            qset = qset.filter(nr2=255, nr1__in=self.unused, nr3__in=self.unused, nr4__in=self.unused)
        elif loc == 50:
            qset = qset.filter(nr3=181, nr1__in=self.unused, nr2__in=self.unused, nr4__in=self.unused)
        elif loc == 55:
            qset = qset.filter(nr4=249, nr1__in=self.unused, nr2__in=self.unused, nr3__in=self.unused)
        elif loc == 36:
            qset = qset.filter(nr2=139, nr1__in=self.unused, nr2__in=self.unused, nr4__in=self.unused)

        nrs = list(qset.values_list('nr', flat=True))

        self.stdout.write('[INFO] Selecting %s / %s' % (index, len(nrs)))

        try:
            nr = nrs[index]
        except IndexError:
            self.stderr.write('[ERROR] Invalid index')
            return

        p2x2 = qset.get(nr=nr)

        base_nrs = [p2x2.nr1, p2x2.nr2, p2x2.nr3, p2x2.nr4]
        print('[INFO] Selected p2x2 with base nrs: %s' % repr(base_nrs))
        # print('[DEBUG] p2x2 sides: %s, %s, %s, %s' % (p2x2.side1, p2x2.side2, p2x2.side3, p2x2.side4))

        for side_nr in (1, 2, 3, 4):
            segment = calc_segment(loc, side_nr)
            self.stdout.write('[INFO] Side %s is segment %s' % (side_nr, segment))

            side_options = self._get_side_options(loc, side_nr)     # gets reversed for side 3 and 4

            side_field = 'side%s' % side_nr
            side_new = getattr(p2x2, side_field, self.twoside_border)

            for side in side_options:
                if side != side_new:
                    self._reduce(segment, side, side_nr)            # reverses back for side 3 and 4
            # for
        # for

        set_used(self.processor, base_nrs)

        total = sum(self.reductions.values())
        if total == 0:
            self.stdout.write('[INFO] No reductions')
        else:
            self.stdout.write('[INFO] Reductions: %s, %s, %s, %s' % (self.reductions[1],
                                                                     self.reductions[2],
                                                                     self.reductions[3],
                                                                     self.reductions[4]))


# end of file
