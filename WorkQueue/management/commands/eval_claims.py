# -*- coding: utf-8 -*-

#  Copyright (c) 2023-2024 Ramon van der Winkel.
#  All rights reserved.
#  Licensed under BSD-3-Clause-Clear. See LICENSE file for details.

from django.core.management.base import BaseCommand
from Pieces2x2.models import TwoSide, TwoSideOptions, Piece2x2
from Pieces2x2.helpers import calc_segment
from WorkQueue.models import ProcessorUsedPieces
from WorkQueue.operations import get_unused


class Command(BaseCommand):

    help = "Show the base piece claims for locations with limited options"

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
        self.small_limit = 3
        self.unused = []

        self.nr_claims = dict()     # [loc, 1/2/3/4] = [nr, ..]
        for loc in range(1, 64+1):
            self.nr_claims[(loc, 1)] = []
            self.nr_claims[(loc, 2)] = []
            self.nr_claims[(loc, 3)] = []
            self.nr_claims[(loc, 4)] = []
        # for

        self.reached_dead_end = False

    def add_arguments(self, parser):
        # parser.add_argument('--verbose', action='store_true')
        parser.add_argument('processor', type=int, help='Processor number to use')
        parser.add_argument('--limit', type=int, default=3, help='Size of small claims to show')

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

    def _count_twoside(self):
        return TwoSideOptions.objects.filter(processor=self.processor).count()

    def _scan_locs(self, used):
        """ Determinate the claims for each location, not considering existing claims """
        used.claimed_at_twoside_count = self._count_twoside()
        used.save(update_fields=['claimed_at_twoside_count'])

        print_at = 1
        for loc in range(1, 64+1):
            if loc == print_at:
                self.stdout.write('[INFO] Scanning locs %s-%s' % (loc, loc + 8))
                print_at = loc + 8

            # see if this loc requires certain base pieces
            options1 = self._get_side_options(loc, 1)
            options2 = self._get_side_options(loc, 2)
            options3 = self._get_side_options(loc, 3)
            options4 = self._get_side_options(loc, 4)

            if len(options1) + len(options2) + len(options3) + len(options4) < 500:
                unused = self.unused[:]

                if loc != 36 and 139 in unused:
                    unused.remove(139)

                # if loc != 10 and 208 in unused:
                #     unused.remove(208)
                #
                # if loc != 15 and 255 in unused:
                #     unused.remove(255)
                #
                # if loc != 50 and 181 in unused:
                #     unused.remove(181)
                #
                # if loc != 55 and 249 in unused:
                #     unused.remove(249)

                qset = Piece2x2.objects.filter(side1__in=options1, side2__in=options2,
                                               side3__in=options3, side4__in=options4,
                                               nr1__in=unused, nr2__in=unused,
                                               nr3__in=unused, nr4__in=unused)

                if loc == 36:
                    qset = qset.filter(nr2=139)
                # elif loc == 10:
                #     qset = qset.filter(nr1=208)
                # elif loc == 15:
                #     qset = qset.filter(nr2=255)
                # elif loc == 50:
                #     qset = qset.filter(nr3=181)
                # elif loc == 55:
                #     qset = qset.filter(nr4=249)

                if 1 < qset.count() < 2000:
                    nrs1 = self.nr_claims[(loc, 1)]
                    nrs2 = self.nr_claims[(loc, 2)]
                    nrs3 = self.nr_claims[(loc, 3)]
                    nrs4 = self.nr_claims[(loc, 4)]

                    for p2x2 in qset.all():
                        if p2x2.nr1 not in nrs1:
                            nrs1.append(p2x2.nr1)
                        if p2x2.nr2 not in nrs2:
                            nrs2.append(p2x2.nr2)
                        if p2x2.nr3 not in nrs3:
                            nrs3.append(p2x2.nr3)
                        if p2x2.nr4 not in nrs4:
                            nrs4.append(p2x2.nr4)
                    # for

                    nrs1.sort()
                    nrs2.sort()
                    nrs3.sort()
                    nrs4.sort()
        # for

    def _limit_base_pieces(self, used):
        multi_claims = dict()        # [claim] = count
        changed = True
        claimed = []
        single_nrs = []
        while changed:
            changed = False

            for loc in range(1, 64+1):
                for nr in range(1, 4+1):
                    nrs = self.nr_claims[(loc, nr)]
                    nrs = tuple(nrs)

                    loc_nr = "%s.nr%s" % (loc, nr)
                    try:
                        multi_claims[nrs].append(loc_nr)
                    except KeyError:
                        multi_claims[nrs] = [loc_nr]

                    if len(nrs) == 1:
                        claim = nrs[0]
                        self.stdout.write('[INFO] Loc %s requires base %s on nr%s' % (loc, claim, nr))
                        tup = (claim, loc)
                        single_nrs.append(tup)
                        if claim in claimed:
                            self.stderr.write('[INFO] Detected multi-claim on base %s' % claim)
                            self.reached_dead_end = True
                        claimed.append(claim)
                # for
            # for

            # self.stdout.write('[INFO] Claimed: (%s) %s' % (len(claimed), repr(claimed)))
            for loc, nr in self.nr_claims.keys():
                nrs = self.nr_claims[(loc, nr)]
                if len(nrs) > 0:
                    for chk in nrs:
                        if chk in claimed:
                            nrs.remove(chk)
                            changed = True
                    # for
        # while

        self.stdout.write('[INFO] Remaining small claims:')
        for loc, nr in self.nr_claims.keys():
            nrs = self.nr_claims[(loc, nr)]
            multi = multi_claims[tuple(nrs)]
            multi = list(frozenset(multi))       # removes dupes
            multi.sort()
            count = len(multi)
            if 1 <= len(nrs) <= self.small_limit or (1 < len(nrs) < 2 * self.small_limit and count > 1):
                multi_str = ''
                if count > 1:
                    multi_str = '  *** MULTI (%s) %s ***' % (count, " + ".join(multi))
                self.stdout.write('%s.nr%s: %s%s' % (loc, nr, repr(nrs), multi_str))
        # for

        claimed_nrs = []
        single_nrs.sort()
        for nr, loc in single_nrs:
            # self.stdout.write('[WARNING] Single claim: %s needs %s' % (loc, nr))
            claimed_nrs.append('%s:%s' % (nr, loc))
        # for
        claimed_nrs_single = ",".join(claimed_nrs)

        if used.claimed_nrs_single != claimed_nrs_single:
            count1 = used.claimed_nrs_single.count(':')
            count2 = claimed_nrs_single.count(':')
            self.stdout.write('[INFO] Single claims changed from %s to %s nrs' % (count1, count2))
            used.claimed_nrs_single = claimed_nrs_single
            used.save(update_fields=['claimed_nrs_single'])
        else:
            self.stdout.write('[INFO] Single claims unchanged')

    def handle(self, *args, **options):

        self.processor = options['processor']
        self.small_limit = options['limit']

        self.stdout.write('[INFO] Processor=%s' % self.processor)

        try:
            used = ProcessorUsedPieces.objects.get(processor=self.processor)
        except ProcessorUsedPieces.DoesNotExist:
            self.stderr.write('[ERROR] Used pieces admin not found')
            return

        self._load_unused()

        self._scan_locs(used)

        self._limit_base_pieces(used)

        if self.reached_dead_end:
            used.reached_dead_end = True
            used.save(update_fields=['reached_dead_end'])


# end of file
