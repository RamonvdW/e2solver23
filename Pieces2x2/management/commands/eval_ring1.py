# -*- coding: utf-8 -*-

#  Copyright (c) 2023 Ramon van der Winkel.
#  All rights reserved.
#  Licensed under BSD-3-Clause-Clear. See LICENSE file for details.

from django.utils import timezone
from django.core.management.base import BaseCommand
from Pieces2x2.models import TwoSide, TwoSideOptions, Piece2x2, EvalProgress
from Pieces2x2.helpers import calc_segment
from Solutions.models import Solution8x8
import datetime
import time


class Command(BaseCommand):

    help = "Eval a possible reduction in TwoSideOptions for the first ring"

    """
        +----+----+----+----+----+----+----+----+
        | 1  | 2  | 3  | 4  | 5  | 6  | 7  | 8  |
        +----+----+----+----+----+----+----+----+
        | 9  |                             | 16 |
        +----+                             +----+
        | 17 |                             | 24 |
        +----+                             +----+
        | 25 |                             | 32 |
        +----+                             +----+
        | 33 |                             | 40 |
        +----+                             +----+
        | 41 |                             | 48 |
        +----+                             +----+
        | 49 |                             | 56 |
        +----+----+----+----+----+----+----+----+
        | 57 | 58 | 59 | 60 | 61 | 62 | 63 | 64 |
        +----+----+----+----+----+----+----+----+
    """

    def _calc_neighbours(self):
        neighbours = dict()

        # order of the entries: side 1, 2, 3, 4
        for nr in range(1, 64+1):
            if nr in self.locs:
                n = list()
                col = (nr - 1) % 8
                row = int((nr - 1) / 8)

                # side 1
                if row == 0:
                    n.append(-1)    # outer border
                elif nr - 8 in self.locs:
                    n.append(nr - 8)
                else:
                    n.append(-2)    # inner gap

                # side 2
                if col == 7:
                    n.append(-1)    # outer border
                elif nr + 1 in self.locs:
                    n.append(nr + 1)
                else:
                    n.append(-2)    # inner gap

                # side 3
                if row == 7:
                    n.append(-1)    # outer border
                elif nr + 8 in self.locs:
                    n.append(nr + 8)
                else:
                    n.append(-2)    # inner gap

                # side 4
                if col == 0:
                    n.append(-1)    # outer border
                elif nr - 1 in self.locs:
                    n.append(nr - 1)
                else:
                    n.append(-2)    # inner gap

                neighbours[nr] = tuple(n)
        # for
        return neighbours

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
        self.segment = 0
        self.locs = (1, 2, 3, 4, 5, 6, 7, 8,
                     9, 16,
                     17, 24,
                     25, 32,
                     33, 40,
                     41, 48,
                     49, 56,
                     57, 58, 59, 60, 61, 62, 63, 64)
        self.segment_options = dict()       # [segment] = side_options
        self.segment_options_rev = dict()   # [segment] = side_options
        self.reductions = 0

        self.unused0 = list()

        self.do_commit = True

        # [p_nr] = [p_nr on side1..4 or -1 if border or -2 if neighbour is a gap]
        self.neighbours = self._calc_neighbours()

        # [p_nr] = [4 side nr]
        self.segment_nrs: dict[int, tuple] = dict()
        for loc in self.locs:
            self.segment_nrs[loc] = (calc_segment(loc, 1),
                                     calc_segment(loc, 2),
                                     calc_segment(loc, 3),
                                     calc_segment(loc, 4))
        # for

        # [0..8] = None or Piece2x2 with side1/2/3/4
        self.board: dict[int, Piece2x2 | None] = {}
        for loc in self.locs:
            self.board[loc] = None

        self.board_order = list()   # solve order (for popping)
        self.board_unused = list()
        self.solve_order = list()
        self.requested_order = list()
        self.prev_tick = 0
        self.progress = None

        self.progress_15min = -1

    def add_arguments(self, parser):
        parser.add_argument('processor', nargs=1, type=int, help='Processor number to use')
        parser.add_argument('segment', nargs=1, type=int, help='Segment to work on (1..72, 129..193)')
        parser.add_argument('--dryrun', action='store_true')
        parser.add_argument('order', nargs='*', type=int, help='Solving order (1..64), max %s' % len(self.locs))

    def _check_progress_15min(self):
        # returns True when it is time to do a 15min-interval report
        minute = datetime.datetime.now().minute
        curr_15min = int(minute / 15) % 4
        if curr_15min != self.progress_15min:
            next_15min = (curr_15min + 1) % 4
            self.progress_15min = next_15min
            return True
        return False

    def _save_progress_solution(self):
        sol = Solution8x8(based_on_6x6=0)
        for loc in range(1, 64+1):
            field_str = 'nr%s' % loc
            setattr(sol, field_str, 0)
        # for
        for loc in self.locs:
            p2x2 = self.board[loc]
            if p2x2:
                field_str = 'nr%s' % loc
                setattr(sol, field_str, p2x2.nr)
        # for
        sol.save()
        print('[INFO] Saved progress solution: pk=%s' % sol.pk)

    def _calc_unused0(self):
        self.unused0 = list(range(1, 256+1))
        # none of the hints are in Ring1
        self.unused0.remove(139)
        self.unused0.remove(208)
        self.unused0.remove(255)
        self.unused0.remove(181)
        self.unused0.remove(249)

    def _reverse_sides(self, options):
        return [self.twoside2reverse[two_side] for two_side in options]

    def _query_segment_options(self, segment):
        """ Return the options remaining for a specific segment """
        options = (TwoSideOptions
                   .objects
                   .filter(processor=self.processor,
                           segment=segment)
                   .values_list('two_side', flat=True))
        options = list(options)
        # self.stdout.write('[DEBUG] Segment %s has %s options' % (segment, len(options)))
        return options

    def _get_segments_options(self):
        for loc in self.locs:
            for side in range(1, 4+1):
                segment = calc_segment(loc, side)
                options = self._query_segment_options(segment)
                self.segment_options[segment] = options
                self.segment_options_rev[segment] = self._reverse_sides(options)
        # for

    def _board_place(self, p_nr: int, p2x2):
        self.board_order.append(p_nr)
        self.board[p_nr] = p2x2
        self.board_unused.remove(p2x2.nr1)
        self.board_unused.remove(p2x2.nr2)
        self.board_unused.remove(p2x2.nr3)
        self.board_unused.remove(p2x2.nr4)

    def _board_pop(self):
        p_nr = self.board_order[-1]
        self.board_order = self.board_order[:-1]
        p2x2 = self.board[p_nr]
        self.board[p_nr] = None
        self.board_unused.extend([p2x2.nr1, p2x2.nr2, p2x2.nr3, p2x2.nr4])

    def _iter(self, loc, options_side1, options_side2, options_side3, options_side4):
        unused = self.board_unused[:]

        # if loc != 36 and 139 in unused:
        #     unused.remove(139)
        #
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

        for p in (Piece2x2
                  .objects
                  .filter(side1__in=options_side1,
                          side2__in=options_side2,
                          side3__in=options_side3,
                          side4__in=options_side4,
                          nr1__in=unused,
                          nr2__in=unused,
                          nr3__in=unused,
                          nr4__in=unused)):
            yield p
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

    def _check_open_ends(self):
        #  verify each twoside open end can still be solved
        twoside_open = list()
        empty_locs = [loc
                      for loc in self.locs
                      if not self.board[loc]]
        empty_locs.append(-2)        # also do open-end check against the internal gap
        for loc in self.locs:
            p2x2 = self.board[loc]
            if p2x2:
                neighs = self.neighbours[loc]

                if neighs[0] in empty_locs:
                    twoside_open.append(p2x2.side1)
                if neighs[1] in empty_locs:
                    twoside_open.append(p2x2.side2)
                if neighs[2] in empty_locs:
                    twoside_open.append(p2x2.side3)
                if neighs[3] in empty_locs:
                    twoside_open.append(p2x2.side4)
        # for

        qset = Piece2x2.objects.filter(nr1__in=self.board_unused, nr2__in=self.board_unused,
                                       nr3__in=self.board_unused, nr4__in=self.board_unused)
        # counts = dict()
        for side in set(twoside_open):
            # ensure we have a Piece2x2 that can connect to this side
            side_rev = self.twoside2reverse[side]
            p2x2 = qset.filter(side1=side_rev).first()
            if not p2x2:
                # no solution
                # print('[DEBUG] check_open_ends: out of options for side: %s' % repr(side))
                return False
            # counts[side] = qset.filter(side1=side_rev).count()
        # for

        # print('[DEBUG] check_open_ends: all good: %s' % repr(counts))
        return True

    def _select_next_loc(self):
        # decide which position on the board has the fewest options

        # follow previous solve order
        for loc in self.solve_order:
            if self.board[loc] is None:
                return loc, False
        # for

        # decide the next best position on the board to solve

        qset = Piece2x2.objects.filter(nr1__in=self.board_unused,
                                       nr2__in=self.board_unused,
                                       nr3__in=self.board_unused,
                                       nr4__in=self.board_unused)

        loc_counts = list()
        for loc in self.locs:
            if self.board[loc] is None:
                # empty position on the board
                seg1, seg2, seg3, seg4 = self.segment_nrs[loc]
                options_side1 = self.segment_options[seg1]
                options_side2 = self.segment_options[seg2]
                options_side3 = self.segment_options_rev[seg3]
                options_side4 = self.segment_options_rev[seg4]

                n1, n2, n3, n4 = self.neighbours[loc]
                if n1 >= 0:
                    p = self.board[n1]
                    if p:
                        options_side1 = [self.twoside2reverse[p.side3]]
                if n2 >= 0:
                    p = self.board[n2]
                    if p:
                        options_side2 = [self.twoside2reverse[p.side4]]
                if n3 >= 0:
                    p = self.board[n3]
                    if p:
                        options_side3 = [self.twoside2reverse[p.side1]]
                if n4 >= 0:
                    p = self.board[n4]
                    if p:
                        options_side4 = [self.twoside2reverse[p.side2]]

                count = qset.filter(side1__in=options_side1,
                                    side2__in=options_side2,
                                    side3__in=options_side3,
                                    side4__in=options_side4).count()
                tup = (count, loc)
                loc_counts.append(tup)

                if count == 0:
                    # dead end
                    # self.stdout.write('[DEBUG] No options for %s' % p_nr)
                    return -1, True
        # for

        # take the lowest
        if len(loc_counts) > 0:
            loc_counts.sort()       # lowest first
            loc = loc_counts[0][-1]
            # self.stdout.write('[INFO] Added %s' % p_nr)
            self.solve_order.append(loc)
            return loc, False

        # niets kunnen kiezen
        self.stdout.write('[DEBUG] select_next_loc failed')
        return -1, True

    def _find_recurse(self):
        tick = time.monotonic()
        if tick - self.prev_tick > 30:
            self.prev_tick = tick
            msg = '(%s) %s' % (len(self.board_order), repr(self.board_order))
            # print(msg)
            self.progress.solve_order = msg
            self.progress.updated = timezone.now()
            self.progress.save(update_fields=['solve_order', 'updated'])

        if len(self.board_order) == len(self.locs):
            if self._check_progress_15min():
                self._save_progress_solution()
            return True

        # decide which p_nr to continue with
        loc, has_zero = self._select_next_loc()
        if has_zero:
            return False

        seg1, seg2, seg3, seg4 = self.segment_nrs[loc]
        options_side1 = self.segment_options[seg1]
        options_side2 = self.segment_options[seg2]
        options_side3 = self.segment_options_rev[seg3]
        options_side4 = self.segment_options_rev[seg4]

        n1, n2, n3, n4 = self.neighbours[loc]
        if n1 >= 0:
            p = self.board[n1]
            if p:
                options_side1 = [self.twoside2reverse[p.side3]]
        if n2 >= 0:
            p = self.board[n2]
            if p:
                options_side2 = [self.twoside2reverse[p.side4]]
        if n3 >= 0:
            p = self.board[n3]
            if p:
                options_side3 = [self.twoside2reverse[p.side1]]
        if n4 >= 0:
            p = self.board[n4]
            if p:
                options_side4 = [self.twoside2reverse[p.side2]]

        for p in self._iter(loc, options_side1, options_side2, options_side3, options_side4):
            self._board_place(loc, p)

            if self._check_open_ends():
                found = self._find_recurse()
            else:
                found = False

            self._board_pop()

            if found:
                return True
        # for

        return False

    def _segment_to_loc(self, segment):
        """ reverse of calc_segment """

        if segment > 128:
            # assume side = 2
            loc2 = segment - 129
            loc4 = segment - 128

            if loc2 in self.locs and loc4 in self.locs:
                # we can choose
                if loc4 == self.requested_order[0]:
                    loc2 = 99

            if loc2 in self.locs:
                return loc2, 2

            # use side=4
            if loc4 in self.locs:
                return loc4, 4
        else:
            # assume side=1
            loc1 = segment
            loc3 = segment - 8

            if loc1 in self.locs and loc3 in self.locs:
                # we can choose
                if loc3 == self.requested_order[0]:
                    loc1 = 99

            if loc1 in self.locs:
                return loc1, 1

            # use side=3
            if loc3 in self.locs:
                return loc3, 3

        print('[ERROR] segment_to_loc failed for segment %s' % segment)
        return -42

    def _find_reduce(self):
        sides = self.segment_options[self.segment]
        todo = len(sides)
        self.stdout.write('[INFO] Checking %s options in segment %s' % (len(sides), self.segment))
        self.solve_order = self.requested_order[:]       # allow deciding optimal order anew

        loc, side_n = self._segment_to_loc(self.segment)
        self.stdout.write('[INFO] Starting at loc %s, side %s' % (loc, side_n))

        self.progress.todo_count = todo
        self.progress.save(update_fields=['segment', 'todo_count'])

        for side in sides:
            # update the progress record in the database
            self.progress.left_count = todo
            self.progress.updated = timezone.now()
            self.progress.save(update_fields=['left_count', 'updated'])

            # place the first piece
            seg1, seg2, seg3, seg4 = self.segment_nrs[loc]
            options_side1 = self.segment_options[seg1]
            options_side2 = self.segment_options[seg2]
            options_side3 = self.segment_options_rev[seg3]
            options_side4 = self.segment_options_rev[seg4]

            if side_n == 1:
                options_side1 = [side]
            elif side_n == 2:
                options_side2 = [side]
            elif side_n == 3:
                options_side3 = [self.twoside2reverse[side]]
            else:   # side_n == 4:
                options_side4 = [self.twoside2reverse[side]]

            found = False
            for p in self._iter(loc, options_side1, options_side2, options_side3, options_side4):
                self._board_place(loc, p)
                found = self._find_recurse()
                self._board_pop()
                if found:
                    break
            # for

            if not found:
                self._reduce(self.segment, side)

            todo -= 1
            self.stdout.write('[INFO] Remaining: %s/%s' % (todo, len(sides)))
            self.prev_tick = time.monotonic()
        # for

    def handle(self, *args, **options):
        if options['dryrun']:
            self.do_commit = False

        self.processor = options['processor'][0]
        self.stdout.write('[INFO] Processor: %s' % self.processor)

        self.segment = options['segment'][0]
        self.stdout.write('[INFO] Segment: %s' % self.segment)

        for loc in options['order']:
            if loc not in self.locs:
                self.stdout.write('[WARNING] Skipping invalid order: %s' % loc)
            elif loc not in self.requested_order:
                self.requested_order.append(loc)
            else:
                self.stdout.write('[WARNING] Duplicate in requested order: %s' % loc)
        # for
        self.stdout.write('[INFO] Initial solve order: %s' % repr(self.requested_order))

        self._calc_unused0()
        self.board_unused = self.unused0[:]

        self._get_segments_options()
        # self.stdout.write('%s' % ", ".join([str(len(opt)) for opt in self.side_options]))

        self.prev_tick = time.monotonic()

        self.progress = EvalProgress(
                        eval_size=48,  # 8x8-4x4 = 64-16 = 48
                        eval_loc=1,
                        processor=self.processor,
                        segment=self.segment,
                        todo_count=0,
                        left_count=0,
                        solve_order='',
                        updated=timezone.now())
        self.progress.save()

        try:
            self._find_reduce()
        except KeyboardInterrupt:
            pass

        self.progress.delete()

        if self.reductions == 0:
            self.stdout.write('[INFO] No reductions')
        else:
            self.stdout.write('[INFO] Reductions: %s' % self.reductions)
            if not self.do_commit:
                self.stdout.write('[WARNING] Drop the --dryrun to keep')

# end of file