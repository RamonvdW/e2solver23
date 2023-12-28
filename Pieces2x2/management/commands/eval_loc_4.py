# -*- coding: utf-8 -*-

#  Copyright (c) 2023 Ramon van der Winkel.
#  All rights reserved.
#  Licensed under BSD-3-Clause-Clear. See LICENSE file for details.

from django.core.management.base import BaseCommand
from Pieces2x2.models import TwoSide, TwoSideOptions, Piece2x2
from Pieces2x2.helpers import calc_segment


class Command(BaseCommand):

    help = "Eval a possible reduction in TwoSideOptions for a square of 4 locations"

    """
              s0          s1
            +----+      +----+
        s2  | p0 |  s3  | p1 |  s4
            +----+      +----+
              s5          s6
            +----+      +----+
        s7  | p2 |  s8  | p3 |  s9
            +----+      +----+
             s10         s11
    """

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
        self.locs = (0, 0, 0, 0)        # p0..p3
        self.side_options = ([], [], [], [], [], [], [], [], [], [], [], [])        # s0..s11
        self.side_options_rev = ([], [], [], [], [], [], [], [], [], [], [], [])    # s0..s11
        self.reductions = 0

        self.unused0 = list()

        self.do_commit = True

    def add_arguments(self, parser):
        parser.add_argument('processor', nargs=1, type=int, help='Processor number to use')
        parser.add_argument('loc', nargs=1, type=int, help='Location on board (1..55)')
        parser.add_argument('--dryrun', action='store_true')

    def _get_unused(self):
        unused0 = list(range(1, 256+1))

        if 36 not in self.locs:
            unused0.remove(139)

        if 10 not in self.locs:
            unused0.remove(208)

        if 15 not in self.locs:
            unused0.remove(255)

        if 50 not in self.locs:
            unused0.remove(181)

        if 55 not in self.locs:
            unused0.remove(249)

        unused = unused0[:]

        # load all the segments
        seg2count = dict()
        for options in TwoSideOptions.objects.filter(processor=self.processor):
            try:
                seg2count[options.segment] += 1
            except KeyError:
                seg2count[options.segment] = 1
        # for

        # check how many Piece2x2 fit each location
        for loc in range(1, 64+1):
            if loc not in self.locs:                # avoid blocking an evaluation location
                seg1 = calc_segment(loc, 1)
                seg2 = calc_segment(loc, 2)
                seg3 = calc_segment(loc, 3)
                seg4 = calc_segment(loc, 4)

                count1 = seg2count[seg1]
                count2 = seg2count[seg2]
                count3 = seg2count[seg3]
                count4 = seg2count[seg4]

                if count1 == 1 and count2 == 1 and count3 == 1 and count4 == 1:
                    # limited options on this location: get the Piece2x2
                    side1 = TwoSideOptions.objects.get(processor=self.processor, segment=seg1).two_side
                    side2 = TwoSideOptions.objects.get(processor=self.processor, segment=seg2).two_side
                    side3 = TwoSideOptions.objects.get(processor=self.processor, segment=seg3).two_side
                    side4 = TwoSideOptions.objects.get(processor=self.processor, segment=seg4).two_side

                    side3 = self.twoside2reverse[side3]
                    side4 = self.twoside2reverse[side4]

                    nrs = dict()
                    p2x2_count = 0
                    for p2x2 in Piece2x2.objects.filter(side1=side1, side2=side2, side3=side3, side4=side4,
                                                        nr1__in=unused0, nr2__in=unused0,
                                                        nr3__in=unused0, nr4__in=unused0):
                        p2x2_count += 1
                        for nr in (p2x2.nr1, p2x2.nr2, p2x2.nr3, p2x2.nr4):
                            try:
                                nrs[nr] += 1
                            except KeyError:
                                nrs[nr] = 1
                        # for
                    # for
                    for nr, nr_count in nrs.items():
                        if nr_count == p2x2_count:
                            unused.remove(nr)
                    # for
        # for

        self.stdout.write('[INFO] %s base pieces in use' % (256 - len(unused)))

        return unused

    def _reverse_sides(self, options):
        return [self.twoside2reverse[two_side] for two_side in options]

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

    def _get_side_options(self):
        """
                  s0          s1
                +----+      +----+
            s2  | p0 |  s3  | p1 |  s4
                +----+      +----+
                  s5          s6
                +----+      +----+
            s7  | p2 |  s8  | p3 |  s9
                +----+      +----+
                 s10         s11
        """
        s0 = self._get_loc_side_options(self.locs[0], 1)
        s1 = self._get_loc_side_options(self.locs[1], 1)
        s2 = self._get_loc_side_options(self.locs[0], 4)
        s3 = self._get_loc_side_options(self.locs[0], 2)
        s4 = self._get_loc_side_options(self.locs[1], 2)
        s5 = self._get_loc_side_options(self.locs[2], 1)
        s6 = self._get_loc_side_options(self.locs[3], 1)
        s7 = self._get_loc_side_options(self.locs[2], 4)
        s8 = self._get_loc_side_options(self.locs[2], 2)
        s9 = self._get_loc_side_options(self.locs[3], 2)
        s10 = self._get_loc_side_options(self.locs[2], 3)
        s11 = self._get_loc_side_options(self.locs[3], 3)

        self.side_options = [s0, s1, s2, s3, s4, s5, s6, s7, s8, s9, s10, s11]

        s0 = self._reverse_sides(s0)
        s1 = self._reverse_sides(s1)
        s2 = self._reverse_sides(s2)
        s3 = self._reverse_sides(s3)
        s4 = self._reverse_sides(s4)
        s5 = self._reverse_sides(s5)
        s6 = self._reverse_sides(s6)
        s7 = self._reverse_sides(s7)
        s8 = self._reverse_sides(s8)
        s9 = self._reverse_sides(s9)
        s10 = self._reverse_sides(s10)
        s11 = self._reverse_sides(s11)

        self.side_options_rev = [s0, s1, s2, s3, s4, s5, s6, s7, s8, s9, s10, s11]

    @staticmethod
    def _iter(unused1, options_side1, options_side2, options_side3, options_side4):
        for p in (Piece2x2
                  .objects
                  .filter(side1__in=options_side1,
                          side2__in=options_side2,
                          side3__in=options_side3,
                          side4__in=options_side4,
                          nr1__in=unused1,
                          nr2__in=unused1,
                          nr3__in=unused1,
                          nr4__in=unused1)):
            unused2 = unused1[:]
            unused2.remove(p.nr1)
            unused2.remove(p.nr2)
            unused2.remove(p.nr3)
            unused2.remove(p.nr4)
            yield p, unused2
        # for

    def _reduce(self, segment, two_side):
        qset = TwoSideOptions.objects.filter(processor=self.processor, segment=segment, two_side=two_side)
        if qset.count() != 1:
            self.stderr.write('[ERROR] Cannot find segment=%s, two_side=%s' % (segment, two_side))
        else:
            self.stdout.write('[INFO] Reduction segment %s: %s' % (segment, two_side))
            if self.do_commit:
                qset.delete()
            self.reductions += 1

    def _reduce_s3(self):
        """
                  s0          s1
                +----+      +----+
            s2  | p0 |  s3  | p1 |  s4
                +----+      +----+
                  s5          s6
                +----+      +----+
            s7  | p2 |  s8  | p3 |  s9
                +----+      +----+
                 s10         s11
        """
        segment = calc_segment(self.locs[0], 2)
        sides = self.side_options[3]
        todo = len(sides)
        self.stdout.write('[INFO] Checking %s options in segment %s' % (todo, segment))
        for side in sides:
            p0_exp_s2 = side
            p1_exp_s4 = self.twoside2reverse[side]
            found = False
            for p0, unused1 in self._iter(self.unused0,
                                          self.side_options[0],
                                          [p0_exp_s2],
                                          self.side_options_rev[5],
                                          self.side_options_rev[2]):
                p2_exp_s1 = self.twoside2reverse[p0.side3]

                for p1, unused2 in self._iter(unused1,
                                              self.side_options[1],
                                              self.side_options[4],
                                              self.side_options_rev[6],
                                              [p1_exp_s4]):
                    p3_exp_s1 = self.twoside2reverse[p1.side3]

                    for p2, unused3 in self._iter(unused2,
                                                  [p2_exp_s1],
                                                  self.side_options[8],
                                                  self.side_options_rev[10],
                                                  self.side_options_rev[7]):
                        p3_exp_s4 = self.twoside2reverse[p2.side2]

                        for _ in self._iter(unused3,
                                            [p3_exp_s1],
                                            self.side_options[9],
                                            self.side_options_rev[11],
                                            [p3_exp_s4]):
                            # found a combi of p0..p3
                            found = True
                            break
                        # for
                        if found:
                            break
                    # for
                    if found:
                        break
                # for
                if found:
                    break
            # for

            if not found:
                self._reduce(segment, side)

            todo -= 1
            self.stdout.write('[INFO] Remaining: %s/%s' % (todo, len(sides)))
        # for

    def _reduce_s5(self):
        """
                  s0          s1
                +----+      +----+
            s2  | p0 |  s3  | p1 |  s4
                +----+      +----+
                  s5          s6
                +----+      +----+
            s7  | p2 |  s8  | p3 |  s9
                +----+      +----+
                 s10         s11
        """
        segment = calc_segment(self.locs[0], 3)
        sides = self.side_options[5]
        todo = len(sides)
        self.stdout.write('[INFO] Checking %s options in segment %s' % (todo, segment))
        for side in sides:
            p0_exp_s3 = self.twoside2reverse[side]
            p2_exp_s1 = side
            found = False
            for p0, unused1 in self._iter(self.unused0,
                                          self.side_options[0],
                                          self.side_options[3],
                                          [p0_exp_s3],
                                          self.side_options_rev[2]):
                p1_exp_s4 = self.twoside2reverse[p0.side2]

                for p2, unused2 in self._iter(unused1,
                                              [p2_exp_s1],
                                              self.side_options[8],
                                              self.side_options_rev[10],
                                              self.side_options_rev[7]):
                    p3_exp_s4 = self.twoside2reverse[p2.side2]

                    for p1, unused3 in self._iter(unused2,
                                                  self.side_options[1],
                                                  self.side_options[4],
                                                  self.side_options_rev[6],
                                                  [p1_exp_s4]):
                        p3_exp_s1 = self.twoside2reverse[p1.side3]

                        for _ in self._iter(unused3,
                                            [p3_exp_s1],
                                            self.side_options[9],
                                            self.side_options_rev[11],
                                            [p3_exp_s4]):
                            # found a combi of p0..p3
                            found = True
                            break
                        # for
                        if found:
                            break
                    # for
                    if found:
                        break
                # for
                if found:
                    break
            # for

            if not found:
                self._reduce(segment, side)

            todo -= 1
            self.stdout.write('[INFO] Remaining: %s/%s' % (todo, len(sides)))
        # for

    def _reduce_s6(self):
        """
                  s0          s1
                +----+      +----+
            s2  | p0 |  s3  | p1 |  s4
                +----+      +----+
                  s5          s6
                +----+      +----+
            s7  | p2 |  s8  | p3 |  s9
                +----+      +----+
                 s10         s11
        """
        segment = calc_segment(self.locs[1], 3)
        sides = self.side_options[6]
        todo = len(sides)
        self.stdout.write('[INFO] Checking %s options in segment %s' % (todo, segment))
        for side in sides:
            p1_exp_s3 = self.twoside2reverse[side]
            p3_exp_s1 = side
            found = False
            for p1, unused1 in self._iter(self.unused0,
                                          self.side_options[1],
                                          self.side_options[4],
                                          [p1_exp_s3],
                                          self.side_options_rev[3]):
                p0_exp_s2 = self.twoside2reverse[p1.side4]

                for p3, unused2 in self._iter(unused1,
                                              [p3_exp_s1],
                                              self.side_options[9],
                                              self.side_options_rev[11],
                                              self.side_options_rev[8]):
                    p2_exp_s2 = self.twoside2reverse[p3.side4]

                    for p0, unused3 in self._iter(unused2,
                                                  self.side_options[0],
                                                  [p0_exp_s2],
                                                  self.side_options_rev[5],
                                                  self.side_options_rev[2]):
                        p2_exp_s1 = self.twoside2reverse[p0.side3]

                        for _ in self._iter(unused3,
                                            [p2_exp_s1],
                                            [p2_exp_s2],
                                            self.side_options_rev[10],
                                            self.side_options_rev[7]):
                            # found a combi of p0..p3
                            found = True
                            break
                        # for
                        if found:
                            break
                    # for
                    if found:
                        break
                # for
                if found:
                    break
            # for

            if not found:
                self._reduce(segment, side)

            todo -= 1
            self.stdout.write('[INFO] Remaining: %s/%s' % (todo, len(sides)))
        # for

    def _reduce_s8(self):
        """
                  s0          s1
                +----+      +----+
            s2  | p0 |  s3  | p1 |  s4
                +----+      +----+
                  s5          s6
                +----+      +----+
            s7  | p2 |  s8  | p3 |  s9
                +----+      +----+
                 s10         s11
        """
        segment = calc_segment(self.locs[2], 2)
        sides = self.side_options[8]
        todo = len(sides)
        self.stdout.write('[INFO] Checking %s options in segment %s' % (todo, segment))
        for side in sides:
            p2_exp_s2 = side
            p3_exp_s4 = self.twoside2reverse[side]
            found = False
            for p2, unused1 in self._iter(self.unused0,
                                          self.side_options[5],
                                          [p2_exp_s2],
                                          self.side_options_rev[10],
                                          self.side_options_rev[7]):
                p0_exp_s3 = self.twoside2reverse[p2.side1]

                for p3, unused2 in self._iter(unused1,
                                              self.side_options[6],
                                              self.side_options[9],
                                              self.side_options_rev[11],
                                              [p3_exp_s4]):
                    p1_exp_s3 = self.twoside2reverse[p3.side1]

                    for p0, unused3 in self._iter(unused2,
                                                  self.side_options[0],
                                                  self.side_options[3],
                                                  [p0_exp_s3],
                                                  self.side_options_rev[2]):
                        p1_exp_s4 = self.twoside2reverse[p0.side2]

                        for _ in self._iter(unused3,
                                            self.side_options[1],
                                            self.side_options[4],
                                            [p1_exp_s3],
                                            [p1_exp_s4]):
                            # found a combi of p0..p3
                            found = True
                            break
                        # for
                        if found:
                            break
                    # for
                    if found:
                        break
                # for
                if found:
                    break
            # for

            if not found:
                self._reduce(segment, side)

            todo -= 1
            self.stdout.write('[INFO] Remaining: %s/%s' % (todo, len(sides)))
        # for

    def handle(self, *args, **options):

        """
                  s0          s1
                +----+      +----+
            s2  | p0 |  s3  | p1 |  s4
                +----+      +----+
                  s5          s6
                +----+      +----+
            s7  | p2 |  s8  | p3 |  s9
                +----+      +----+
                 s10         s11
        """

        if options['dryrun']:
            self.do_commit = False

        loc = options['loc'][0]
        if loc < 1 or loc > 55 or loc in (8, 16, 24, 32, 40, 48):
            self.stderr.write('[ERROR] Invalid location')
            return
        self.locs = (loc, loc + 1,
                     loc + 8, loc + 9)
        self.stdout.write('[INFO] Locations: %s' % repr(self.locs))

        self.processor = options['processor'][0]
        self.stdout.write('[INFO] Processor=%s' % self.processor)

        self.unused0 = self._get_unused()

        self._get_side_options()
        # self.stdout.write('%s' % ", ".join([str(len(opt)) for opt in self.side_options]))

        self._reduce_s3()
        self._reduce_s5()
        self._reduce_s6()
        self._reduce_s8()

        if self.reductions == 0:
            self.stdout.write('[INFO] No reductions')
        else:
            self.stdout.write('[INFO] Reductions: %s' % self.reductions)
            if not self.do_commit:
                self.stdout.write('[WARNING] Use --commit to keep')

# end of file
