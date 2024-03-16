# -*- coding: utf-8 -*-

#  Copyright (c) 2023-2024 Ramon van der Winkel.
#  All rights reserved.
#  Licensed under BSD-3-Clause-Clear. See LICENSE file for details.

from django.core.management.base import BaseCommand
from Pieces2x2.models import TwoSide, TwoSideOptions, Piece2x2
from Pieces2x2.helpers import calc_segment
from WorkQueue.operations import (propagate_segment_reduction, set_loc_used, get_unused_for_locs, request_eval_claims,
                                  used_note_add)


class Command(BaseCommand):

    help = "Fix one of the locations to one of possible Piece2x2"

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

        self.loc = 0
        self.processor = 0
        self.reductions = {1: 0, 2: 0, 3: 0, 4: 0}     # [side_nr] = count
        self.unused = []
        self.do_commit = False
        self.bulk_reduce = dict()       # [segment] = [two_side, ..]

    def add_arguments(self, parser):
        parser.add_argument('--commit', action='store_true')
        parser.add_argument('processor', type=int, help='Processor number to use')
        parser.add_argument('loc', type=int, help='Location on board')
        parser.add_argument('index', type=int, help='i-th Piece2x2 number to use')
        parser.add_argument('claimed', nargs='*', type=int, help="Base piece number claimed for other location")

    def _get_unused(self, claimed):
        unused = get_unused_for_locs(self.processor, [self.loc])

        if self.loc != 36 and 139 in unused:
            unused.remove(139)

        # if self.loc != 10 and 208 in unused:
        #     unused.remove(208)
        #
        # if self.loc != 15 and 255 in unused:
        #     unused.remove(255)
        #
        # if self.loc != 50 and 181 in unused:
        #     unused.remove(181)
        #
        # if self.loc != 55 and 249 in unused:
        #     unused.remove(249)

        for claim in claimed:
            if claim in unused:
                unused.remove(claim)
        # for

        self.stdout.write('[INFO] %s base pieces in use or claimed' % (256 - len(unused)))
        self.unused = unused

    def _reverse_sides(self, options):
        return [self.twoside2reverse[two_side] for two_side in options]

    def _get_side_options(self, side_nr):
        segment = calc_segment(self.loc, side_nr)
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

        try:
            self.bulk_reduce[segment].append(two_side)
        except KeyError:
            self.bulk_reduce[segment] = [two_side]

        self.reductions[side_nr] += 1
        return

    def handle(self, *args, **options):

        self.do_commit = options['commit']

        self.loc = options['loc']

        self.processor = options['processor']

        index = options['index']

        self.stdout.write('[INFO] Processor=%s; Location: %s' % (self.processor, self.loc))

        self._get_unused(options['claimed'])

        options1 = self._get_side_options(1)
        options2 = self._get_side_options(2)
        options3 = self._get_side_options(3)        # is reversed
        options4 = self._get_side_options(4)        # is reversed

        qset = Piece2x2.objects.filter(side1__in=options1, side2__in=options2, side3__in=options3, side4__in=options4,
                                       nr1__in=self.unused, nr2__in=self.unused,
                                       nr3__in=self.unused, nr4__in=self.unused)

        if self.loc == 36:
            qset = qset.filter(nr2=139)
        # elif self.loc == 10:
        #     qset = qset.filter(nr1=208)
        # elif self.loc == 15:
        #     qset = qset.filter(nr2=255)
        # elif self.loc == 50:
        #     qset = qset.filter(nr3=181)
        # elif self.loc == 55:
        #     qset = qset.filter(nr4=249)

        nrs = list(qset.values_list('nr', flat=True))

        if len(options1) + len(options2) + len(options3) + len(options4) == 0:
            self.stdout.write('[WARNING] Nothing found in that location')
            return

        if len(options1) + len(options2) + len(options3) + len(options4) <= 4:
            self.stdout.write('[WARNING] Location seems filled already')
            return

        self.stdout.write('[INFO] Selecting %s / %s' % (index, len(nrs)))

        try:
            nr = nrs[index]
        except IndexError:
            self.stderr.write('[ERROR] Invalid index')
            return

        # perform a reduction first
        self.stdout.write('[INFO] Performing eval_loc_1 equivalent check for loc %s' % self.loc)
        side1_new = list(qset.distinct('side1').values_list('side1', flat=True))
        side2_new = list(qset.distinct('side2').values_list('side2', flat=True))
        side3_new = list(qset.distinct('side3').values_list('side3', flat=True))
        side4_new = list(qset.distinct('side4').values_list('side4', flat=True))

        segment = calc_segment(self.loc, 1)
        for side in options1:
            if side not in side1_new:
                self._reduce(segment, side, 1)
        # for

        segment = calc_segment(self.loc, 2)
        for side in options2:
            if side not in side2_new:
                self._reduce(segment, side, 2)
        # for

        segment = calc_segment(self.loc, 3)
        for side in options3:
            if side not in side3_new:
                self._reduce(segment, side, 3)
        # for

        segment = calc_segment(self.loc, 4)
        for side in options4:
            if side not in side4_new:
                self._reduce(segment, side, 4)
        # for

        p2x2 = qset.get(nr=nr)

        base_nrs = [p2x2.nr1, p2x2.nr2, p2x2.nr3, p2x2.nr4]
        print('[INFO] Selected p2x2 with base nrs: %s' % repr(base_nrs))
        # print('[DEBUG] p2x2 sides: %s, %s, %s, %s' % (p2x2.side1, p2x2.side2, p2x2.side3, p2x2.side4))

        if self.do_commit:
            msg = 'fix_loc %s %s' % (self.loc, index)
            msg += ' --> p2x2 nr %s' % nr
            msg += ' --> base nrs %s' % repr(base_nrs)
            used_note_add(self.processor, msg)

        for side_nr in (1, 2, 3, 4):
            segment = calc_segment(self.loc, side_nr)
            self.stdout.write('[INFO] Side %s is segment %s' % (side_nr, segment))

            side_options = self._get_side_options(side_nr)     # gets reversed for side 3 and 4

            side_field = 'side%s' % side_nr
            side_new = getattr(p2x2, side_field, self.twoside_border)

            for side in side_options:
                if side != side_new:
                    self._reduce(segment, side, side_nr)            # reverses back for side 3 and 4
            # for
        # for

        if self.do_commit:
            for segment, two_sides in self.bulk_reduce.items():
                qset = TwoSideOptions.objects.filter(processor=self.processor, segment=segment, two_side__in=two_sides)
                qset.delete()
            # for
            set_loc_used(self.processor, self.loc, p2x2)

            for segment in self.bulk_reduce.keys():
                propagate_segment_reduction(self.processor, segment)
            # for

        total = sum(self.reductions.values())
        if total == 0:
            self.stdout.write('[INFO] No reductions')
        else:
            self.stdout.write('[INFO] Reductions: %s, %s, %s, %s' % (self.reductions[1],
                                                                     self.reductions[2],
                                                                     self.reductions[3],
                                                                     self.reductions[4]))
            request_eval_claims(self.processor)

            if not self.do_commit:
                self.stdout.write('[WARNING] Use --commit to keep')


# end of file
