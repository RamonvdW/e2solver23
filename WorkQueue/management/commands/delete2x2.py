# -*- coding: utf-8 -*-

#  Copyright (c) 2023-2024 Ramon van der Winkel.
#  All rights reserved.
#  Licensed under BSD-3-Clause-Clear. See LICENSE file for details.

from django.utils import timezone
from django.core.management.base import BaseCommand
from Pieces2x2.models import TwoSide, TwoSideOptions, Piece2x2, EvalProgress
from Pieces2x2.helpers import calc_segment
from WorkQueue.operations import propagate_segment_reduction, get_unused_for_locs, check_dead_end
import time


class Command(BaseCommand):

    help = "Delete 2x2 pieces that cannot be placed"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.processor = 0
        self.reductions = 0
        self.do_commit = False

    def add_arguments(self, parser):
        parser.add_argument('processor', type=int, help='Processor number to use')
        parser.add_argument('loc', type=int, help='Location to work on (1..64)')
        parser.add_argument('--commit', action='store_true')

    def _get_unused(self):
        unused = get_unused_for_locs(self.processor, self.locs)

        if 36 not in self.locs and 139 in unused:
            unused.remove(139)

        # if 10 not in self.locs and 208 in unused:
        #     unused.remove(208)
        #
        # if 15 not in self.locs and 255 in unused:
        #     unused.remove(255)
        #
        # if 50 not in self.locs and 181 in unused:
        #     unused.remove(181)
        #
        # if 55 not in self.locs and 249 in unused:
        #     unused.remove(249)

        self.stdout.write('[INFO] %s base pieces in use' % (256 - len(unused)))
        return unused

    def _get_loc_side_options(self, loc, side_nr):
        segment = calc_segment(loc, side_nr)
        options = (TwoSideOptions
                   .objects
                   .filter(processor=self.processor,
                           segment=segment)
                   .values_list('two_side', flat=True))
        options = list(options)
        # self.stdout.write('[DEBUG] Segment %s has %s options' % (segment, len(options)))
        return options

    def _get_side_options(self, loc):
        s1 = self._get_loc_side_options(loc, 1)
        s2 = self._get_loc_side_options(loc, 2)
        s3 = self._get_loc_side_options(loc, 3)
        s4 = self._get_loc_side_options(loc, 4)

        self.side_options = [s1, s2, s3, s4]

    def _delete_2x2(self, loc):
        if loc == 1:
            qset = Piece2x2.objects.filter(nr1__in=(1, 2, 3, 4))
        elif loc == 8:
            qset = Piece2x2.objects.filter(nr2__in=(1, 2, 3, 4))
        elif loc == 57:
            qset = Piece2x2.objects.filter(nr3__in=(1, 2, 3, 4))
        elif loc == 64:
            qset = Piece2x2.objects.filter(nr4__in=(1, 2, 3, 4))
        elif loc == 10:
            qset = Piece2x2.objects.filter(nr1=208)
        elif loc == 15:
            qset = Piece2x2.objects.filter(nr2=255)
        elif loc == 36:
            qset = Piece2x2.objects.filter(nr2=139)
        elif loc == 50:
            qset = Piece2x2.objects.filter(nr3=181)
        elif loc == 55:
            qset = Piece2x2.objects.filter(nr4=249)
        else:
            self.stdout.write('[ERROR] Unsupported location')
            return

        count1 = qset.count()
        self.stdout.write('[INFO] Piece2x2 count: %s' % count1)

        s1, s2, s3, s4 = self.side_options

        qset2 = qset.filter(side1__in=s1, side2__in=s2, side3__in=s3, side4__in=s4)
        count2 = qset2.count()
        self.stdout.write('[INFO] Limited set: %s' % count2)

        nrs = (qset2.values_list('nr', flat=True))
        qset3 = qset.exclude(nr__in=nrs)
        count3 = qset3.count()
        self.stdout.write('[INFO] Piece2x2 deletable: %s' % count3)
        self.reductions += count3

        if self.do_commit:
            qset3.delete()

        return

    def handle(self, *args, **options):

        if options['commit']:
            self.do_commit = True

        loc = options['loc']
        if loc < 1 or loc > 64:
            self.stdout.write('[ERROR] Invalid location')
            return
        self.stdout.write('[INFO] Location: %s' % repr(loc))

        self.processor = options['processor']
        self.stdout.write('[INFO] Processor=%s' % self.processor)

        self._get_side_options(loc)

        try:
            self._delete_2x2(loc)
        except KeyboardInterrupt:
            pass

        if self.reductions == 0:
            self.stdout.write('[INFO] No reductions')
        else:
            self.stdout.write('[INFO] Reductions: %s' % self.reductions)
            if not self.do_commit:
                self.stdout.write('[WARNING] Use --commit to keep')

# end of file
