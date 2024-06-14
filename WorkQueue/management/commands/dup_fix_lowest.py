# -*- coding: utf-8 -*-

#  Copyright (c) 2024 Ramon van der Winkel.
#  All rights reserved.
#  Licensed under BSD-3-Clause-Clear. See LICENSE file for details.

from django.core.management.base import BaseCommand
from Pieces2x2.models import TwoSideOptions, Piece2x2
from Pieces2x2.helpers import calc_segment
from WorkQueue.models import ProcessorUsedPieces
from WorkQueue.operations import set_loc_used, used_note_add


class Command(BaseCommand):

    help = "Duplicate a board and fix the location with the fewest options"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.proc: ProcessorUsedPieces | None = None

        # which locations are not yet filled?
        self.locs_free = list()

        self.loc2unused = dict()        # [loc] = [nr, nr, ..]
        self.loc2claims = dict()        # [loc] = [nr, nr, ..]
        self.segment2two_sides = dict()   # [segment] = [two_side, two_side, ..]

        self.verbose = False

    def add_arguments(self, parser):
        parser.add_argument('--verbose', action='store_true')
        parser.add_argument('processor', type=int, help='Processor to duplicate')

    def _load_filled_locations(self):
        for loc in range(1, 64+1):
            loc_str = 'loc%s' % loc
            if getattr(self.proc, loc_str) == 0:
                self.locs_free.append(loc)
        # for
        if self.verbose:
            self.stdout.write('[INFO] %s unfilled locations' % len(self.locs_free))

    def _load_unused(self):
        unused_border = list(range(1, 256 + 1))
        unused_center = list(range(61, 256 + 1))
        for nr in range(1, 256 + 1):
            nr_str = 'nr%s' % nr
            if getattr(self.proc, nr_str, False):
                # this piece is used
                if nr in unused_center:
                    unused_center.remove(nr)
                if nr in unused_border:
                    unused_border.remove(nr)
        # for
        if self.verbose:
            self.stdout.write('[INFO] %s unused pieces in the border' % len(unused_border))
            self.stdout.write('[INFO] %s unused pieces in the center' % len(unused_center))

        for loc in self.locs_free:
            if loc not in (1, 2, 3, 4, 5, 6, 7, 8,
                           9, 16,
                           17, 24,
                           25, 32,
                           33, 40,
                           41, 48,
                           49, 56,
                           57, 58, 59, 60, 61, 62, 63, 64):
                loc_unused = unused_center[:]
            else:
                loc_unused = unused_border[:]

            if loc != 36 and 139 in loc_unused:
                loc_unused.remove(139)

            if loc != 10 and 208 in loc_unused:
                loc_unused.remove(208)

            if loc != 15 and 255 in loc_unused:
                loc_unused.remove(255)

            if loc != 50 and 181 in loc_unused:
                loc_unused.remove(181)

            if loc != 55 and 249 in loc_unused:
                loc_unused.remove(249)

            self.loc2unused[loc] = loc_unused
        # for

    def _load_claims(self):
        for loc in self.locs_free:
            self.loc2claims[loc] = list()

        for claim in self.proc.claimed_nrs_single.split(','):
            if claim:
                base_nr_str, loc_str = claim.split(':')
                loc_nr = int(loc_str)
                base_nr = int(base_nr_str)
                self.loc2claims[loc_nr].append(base_nr)

                # remove as available piece for all locs except where needed
                for loc in self.locs_free:
                    if loc != loc_nr:
                        if base_nr in self.loc2unused[loc]:
                            self.loc2unused[loc].remove(base_nr)
                # for
        # for

        # for claim in used.claimed_nrs_double.split(','):
        #     if claim:
        #         nr_str, locs_str = claim.split(':')
        #         spl = locs_str.split(';')
        #         loc1 = int(spl[0])
        #         loc2 = int(spl[1])
        #         if loc1 not in locs and loc2 not in locs:
        #             nr = int(nr_str)
        #             if nr in unused:
        #                 unused.remove(nr)
        # # for

    def _load_side_options(self):
        for segment in range(1, 165+1):
            self.segment2two_sides[segment] = list()
        # for
        for option in TwoSideOptions.objects.filter(processor=self.proc.processor):
            self.segment2two_sides[option.segment].append(option.two_side)
        # for

    def _determine_loc_with_fewest_options(self):
        counts = list()
        for loc in self.locs_free:
            unused = self.loc2unused[loc]

            options1 = self.segment2two_sides[calc_segment(loc, 1)]
            options2 = self.segment2two_sides[calc_segment(loc, 2)]
            options3 = self.segment2two_sides[calc_segment(loc, 3)]
            options4 = self.segment2two_sides[calc_segment(loc, 4)]

            if len(options1) + len(options2) + len(options3) + len(options4) == 0:
                if self.verbose:
                    self.stdout.write('[WARNING] No options in location %s' % loc)
                continue

            if len(options1) + len(options2) + len(options3) + len(options4) <= 4:
                if self.verbose:
                    self.stdout.write('[WARNING] Location %s seems filled already' % loc)
                continue

            qset = Piece2x2.objects.filter(side1__in=options1, side2__in=options2,
                                           side3__in=options3, side4__in=options4,
                                           nr1__in=unused, nr2__in=unused,
                                           nr3__in=unused, nr4__in=unused)

            if loc == 36:
                qset = qset.filter(nr2=139)
            elif loc == 10:
                qset = qset.filter(nr1=208)
            elif loc == 15:
                qset = qset.filter(nr2=255)
            elif loc == 50:
                qset = qset.filter(nr3=181)
            elif loc == 55:
                qset = qset.filter(nr4=249)

            p2x2s = list(qset)
            tup = (len(p2x2s), loc, p2x2s)
            counts.append(tup)
        # for

        counts.sort()
        # for count, loc in counts[:5]:
        #     self.stdout.write('Loc %s has %s options' % (loc, count))
        # # for

        count, loc, p2x2s = counts[0]
        if self.verbose:
            self.stdout.write('[INFO] Selection location %s with %s options' % (loc, count))
        return loc, p2x2s

    def _dup_new(self):
        # automatically decide the next processor number
        last_proc = ProcessorUsedPieces.objects.order_by('processor').last()
        new_processor = last_proc.processor + 1
        if self.verbose:
            self.stdout.write('[INFO] Creating new processor %s' % new_processor)

        # load a copy, then modify and save
        work = ProcessorUsedPieces.objects.get(processor=self.proc.processor)
        work.pk = None
        work.processor = new_processor
        work.created_from = self.proc.processor
        work.save()

        used_note_add(work.processor, 'Duplicated from %s by dup_fix_lowest' % work.created_from)

        # clean-up (just in case)
        TwoSideOptions.objects.filter(processor=new_processor).all().delete()

        # copy all the TwoSideOptions
        bulk = []
        for segment, two_sides in self.segment2two_sides.items():
            for two_side in two_sides:
                option = TwoSideOptions(
                            processor=new_processor,
                            segment=segment,
                            two_side=two_side)
                bulk.append(option)
        # for
        TwoSideOptions.objects.bulk_create(bulk)
        if self.verbose:
            self.stdout.write('[INFO] Copied %s two-side options' % len(bulk))

        return work

    def _fix_loc(self, work, loc, index, p2x2):
        base_nrs = [p2x2.nr1, p2x2.nr2, p2x2.nr3, p2x2.nr4]
        if self.verbose:
            self.stdout.write('[INFO] Selected p2x2 nr %s with base nrs: %s' % (p2x2.nr, repr(base_nrs)))

        msg = 'dup_fix_lowest: fix %s %s' % (loc, index)
        msg += ' --> p2x2 nr %s' % p2x2.nr
        msg += ' --> base nrs %s' % repr(base_nrs)
        used_note_add(work.processor, msg)

        bulk_reduce = dict()       # [segment] = [two_side, ..]

        for side_nr in (1, 2, 3, 4):
            segment = calc_segment(loc, side_nr)
            side_options = list(TwoSideOptions
                                .objects
                                .filter(processor=work.processor,
                                        segment=segment)
                                .values_list('two_side', flat=True))

            side_field = 'side%s' % side_nr
            side_new = getattr(p2x2, side_field)

            # self.stdout.write('[INFO] Side %s is two_side %s' % (side_nr, side_new))

            for two_side in side_options:
                if two_side != side_new:
                    try:
                        bulk_reduce[segment].append(two_side)
                    except KeyError:
                        bulk_reduce[segment] = [two_side]
            # for
        # for

        for segment, two_sides in bulk_reduce.items():
            qset = TwoSideOptions.objects.filter(processor=work.processor, segment=segment, two_side__in=two_sides)
            qset.delete()
        # for

        set_loc_used(work.processor, loc, p2x2)

        # for segment in bulk_reduce.keys():
        #     propagate_segment_reduction(work, segment)
        # # for

    def handle(self, *args, **options):

        self.verbose = options['verbose']
        processor_nr = options['processor']

        try:
            self.proc = ProcessorUsedPieces.objects.get(processor=processor_nr)
        except ProcessorUsedPieces.DoesNotExist:
            self.stderr.write('[ERROR] Cannot load processor %s' % processor_nr)
            return

        if self.verbose:
            self.stdout.write('[INFO] Processor=%s' % self.proc.processor)

        # determine the unused pieces
        self._load_filled_locations()
        self._load_unused()
        self._load_claims()
        self._load_side_options()
        loc, p2x2s = self._determine_loc_with_fewest_options()

        # create new boards and fill on each board location 'loc' with a different p2x2 'nr'
        index = 0
        new_boards = list()
        for p2x2 in p2x2s:
            work = self._dup_new()
            new_boards.append(str(work.processor))
            self._fix_loc(work, loc, index, p2x2)
            index += 1
        # for

        self.stdout.write(" ".join(new_boards))

# end of file
