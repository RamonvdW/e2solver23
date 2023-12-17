# -*- coding: utf-8 -*-

#  Copyright (c) 2023 Ramon van der Winkel.
#  All rights reserved.
#  Licensed under BSD-3-Clause-Clear. See LICENSE file for details.

from django.core.management.base import BaseCommand
from BasePieces.models import BasePiece
from Pieces2x2.models import TwoSide, TwoSideOptions, Piece2x2
from Pieces2x2.helpers import LOC_CORNERS, LOC_BORDERS, LOC_HINTS, calc_segment


class Command(BaseCommand):

    help = "Generate all initial TwoSideOptions"

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

        self._used_options = list()
        self._segment_done = list()

    def add_arguments(self, parser):
        parser.add_argument('--confirm', action='store_true')

    def _get_twosides_for_loc(self, loc):
        # get the sides
        p1 = p2 = p3 = p4 = None        # piece filter / must be
        s1 = s2 = s3 = s4 = None        # side filter  / must be
        x1 = x2 = x3 = x4 = None        # side exclude / must not be

        if loc in LOC_CORNERS:
            if loc == 1:
                s1 = s4 = self.twoside_border
            elif loc == 8:
                s1 = s2 = self.twoside_border
            elif loc == 57:
                s3 = s4 = self.twoside_border
            else:
                s2 = s3 = self.twoside_border

        elif loc in LOC_BORDERS:
            if loc < 9:
                s1 = self.twoside_border
                x2 = self.twoside_border
                x4 = self.twoside_border

            elif loc > 57:
                x2 = self.twoside_border
                s3 = self.twoside_border
                x4 = self.twoside_border

            elif loc & 1 == 1:
                x1 = self.twoside_border
                x3 = self.twoside_border
                s4 = self.twoside_border

            else:
                x1 = self.twoside_border
                s2 = self.twoside_border
                x3 = self.twoside_border

        else:
            x1 = x2 = x3 = x4 = self.twoside_border

            if loc in LOC_HINTS:
                if loc == 10:
                    p1 = 208
                elif loc == 15:
                    p2 = 255
                elif loc == 36:
                    p2 = 139
                elif loc == 50:
                    p3 = 181
                elif loc == 55:
                    p4 = 249

        # print('[%s] s=%s,%s,%s,%s x=%s,%s,%s,%s p=%s,%s,%s,%s' % (nr, s1, s2, s3, s4, x1, x2, x3, x4, p1, p2, p3, p4))

        qset = Piece2x2.objects.all()

        if s1:
            qset = qset.filter(side1=s1)
        if x1:
            qset = qset.exclude(side1=x1)

        if s2:
            qset = qset.filter(side2=s2)
        elif x2:
            qset = qset.exclude(side2=x2)

        if s3:
            qset = qset.filter(side3=s3)
        elif x3:
            qset = qset.exclude(side3=x3)

        if s4:
            qset = qset.filter(side4=s4)
        elif x4:
            qset = qset.exclude(side4=x4)

        if p1:
            qset = qset.filter(nr1=p1)

        if p2:
            qset = qset.filter(nr2=p2)

        if p3:
            qset = qset.filter(nr3=p3)

        if p4:
            qset = qset.filter(nr4=p4)

        twosides_side1 = list(qset.distinct('side1').values_list('side1', flat=True))
        twosides_side2 = list(qset.distinct('side2').values_list('side2', flat=True))
        twosides_side3 = list(qset.distinct('side3').values_list('side3', flat=True))
        twosides_side4 = list(qset.distinct('side4').values_list('side4', flat=True))

        twosides_side3 = [self.twoside2reverse[two_side] for two_side in twosides_side3]
        twosides_side4 = [self.twoside2reverse[two_side] for two_side in twosides_side4]

        return twosides_side1, twosides_side2, twosides_side3, twosides_side4

    def _save_options(self, loc, side, twosides):
        bulk = list()

        segment = calc_segment(loc, side)
        if segment in self._segment_done:
            return
        self._segment_done.append(segment)

        for two_side in twosides:
            tup = (segment, two_side)
            # avoid dupes
            if tup not in self._used_options:
                self._used_options.append(tup)
                option = TwoSideOptions(segment=segment, two_side=two_side)
                bulk.append(option)
        # for

        TwoSideOptions.objects.bulk_create(bulk)

    def handle(self, *args, **options):

        if options['confirm']:
            TwoSideOptions.objects.all().delete()

        # get all possibilities for a typical type
        qset = (Piece2x2
                .objects
                .filter(nr1__gt=60,
                        nr2__gt=60,
                        nr3__gt=60,
                        nr4__gt=60)
                .distinct('side1'))

        standard_twosides12 = list(qset.values_list('side1', flat=True))
        standard_twosides34 = [self.twoside2reverse[two_side] for two_side in standard_twosides12]
        self.stdout.write('[INFO] Standard number of two sides: %s' % len(standard_twosides12))

        self.stdout.write('[INFO] Generating all possible TwoSideOptions')

        self.stdout.write('[INFO] Hints')
        for loc in LOC_HINTS:
            # very limited set
            twosides_side1, twosides_side2, twosides_side3, twosides_side4 = self._get_twosides_for_loc(loc)

            if options['confirm']:
                self._save_options(loc, 1, twosides_side1)
                self._save_options(loc, 2, twosides_side2)
                self._save_options(loc, 3, twosides_side3)
                self._save_options(loc, 4, twosides_side4)
        # for

        self.stdout.write('[INFO] Corners')
        for loc in LOC_CORNERS:
            # limited set
            twosides_side1, twosides_side2, twosides_side3, twosides_side4 = self._get_twosides_for_loc(loc)

            if options['confirm']:
                self._save_options(loc, 1, twosides_side1)
                self._save_options(loc, 2, twosides_side2)
                self._save_options(loc, 3, twosides_side3)
                self._save_options(loc, 4, twosides_side4)
        # for

        self.stdout.write('[INFO] Borders')
        for loc in LOC_BORDERS:
            # limited set
            twosides_side1, twosides_side2, twosides_side3, twosides_side4 = self._get_twosides_for_loc(loc)

            if options['confirm']:
                self._save_options(loc, 1, twosides_side1)
                self._save_options(loc, 2, twosides_side2)
                self._save_options(loc, 3, twosides_side3)
                self._save_options(loc, 4, twosides_side4)
        # for

        # remainder gets the standard set
        self.stdout.write('[INFO] Remainder')
        twosides_side1 = twosides_side2 = standard_twosides12
        twosides_side3 = twosides_side4 = standard_twosides34

        for loc in range(1, 64+1):
            if loc not in LOC_CORNERS + LOC_BORDERS + LOC_HINTS:
                if options['confirm']:
                    self._save_options(loc, 1, twosides_side1)
                    self._save_options(loc, 2, twosides_side2)
                    self._save_options(loc, 3, twosides_side3)
                    self._save_options(loc, 4, twosides_side4)
        # for

        self.stdout.write('[INFO] Done')

        if not options['confirm']:
            self.stdout.write('[INFO] Use --confirm to delete all TwoSideOptions and initialize clean')

# end of file
