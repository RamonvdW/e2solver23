# -*- coding: utf-8 -*-

#  Copyright (c) 2023-2024 Ramon van der Winkel.
#  All rights reserved.
#  Licensed under BSD-3-Clause-Clear. See LICENSE file for details.

from django.utils import timezone
from django.core.management.base import BaseCommand
from Pieces2x2.models import TwoSide, TwoSideOptions, Piece2x2, EvalProgress
from Pieces2x2.helpers import calc_segment
from WorkQueue.operations import propagate_segment_reduction, get_unused
import time


class Command(BaseCommand):

    help = "Eval a possible reduction in TwoSideOptions for a square of 9 locations"

    """
              s0          s1          s2 
            +----+      +----+      +----+
        s3  | p0 |  s4  | p1 |  s5  | p2 |  s6 
            +----+      +----+      +----+
              s7          s8          s9
            +----+      +----+      +----+
        s10 | p3 |  s11 | p4 |  s12 | p5 |  s13
            +----+      +----+      +----+
              s14         s15        s16
            +----+      +----+      +----+
        s17 | p6 |  s18 | p7 |  s19 | p8 |  s20
            +----+      +----+      +----+
              s21         s22         s23
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
        self.locs = (0, 0)                  # p0..p8
        self.side_options = ([], [])        # s0..s23
        self.side_options_rev = ([], [])    # s0..s23
        self.reductions = 0

        self.do_commit = True

        # [p_nr] = [p_nr on side1..4 or -1 if no neighbour]
        self.neighbours: dict[int, tuple] = {0: (-1, 1, 3, -1),
                                             1: (-1, 2, 4, 0),
                                             2: (-1, -1, 5, 1),
                                             3: (0, 4, 6, -1),
                                             4: (1, 5, 7, 3),
                                             5: (2, -1, 8, 4),
                                             6: (3, 7, -1, -1),
                                             7: (4, 8, -1, 6),
                                             8: (5, -1, -1, 7)}

        # [p_nr] = [4 side nr]
        self.side_nrs: dict[int, tuple] = {0: (0, 4, 7, 3),
                                           1: (1, 5, 8, 4),
                                           2: (2, 6, 9, 5),
                                           3: (7, 11, 14, 10),
                                           4: (8, 12, 15, 11),
                                           5: (9, 13, 16, 12),
                                           6: (14, 18, 21, 17),
                                           7: (15, 19, 22, 18),
                                           8: (16, 20, 23, 19)}

        # [0..8] = None or Piece2x2 with side1/2/3/4
        self.board: dict[int, Piece2x2 | None] = {0: None, 1: None, 2: None,
                                                  3: None, 4: None, 5: None,
                                                  6: None, 7: None, 8: None}

        self.board_order = list()   # solve order (for popping)
        self.board_unused = list()
        self.p_nrs_order = list()
        self.prev_tick = 0
        self.progress = None

    def add_arguments(self, parser):
        parser.add_argument('processor', nargs=1, type=int, help='Processor number to use')
        parser.add_argument('loc', nargs=1, type=int, help='Top-left location on the board (1..46)')
        parser.add_argument('--dryrun', action='store_true')

    def _get_unused(self):
        unused = get_unused(self.processor)

        if 36 not in self.locs and 139 in unused:
            unused.remove(139)

        if 10 not in self.locs and 208 in unused:
            unused.remove(208)

        if 15 not in self.locs and 255 in unused:
            unused.remove(255)

        if 50 not in self.locs and 181 in unused:
            unused.remove(181)

        if 55 not in self.locs and 249 in unused:
            unused.remove(249)

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
                  s0          s1          s2
                +----+      +----+      +----+
            s3  | p0 |  s4  | p1 |  s5  | p2 |  s6
                +----+      +----+      +----+
                  s7          s8          s9
                +----+      +----+      +----+
            s10 | p3 |  s11 | p4 |  s12 | p5 |  s13
                +----+      +----+      +----+
                  s14         s15        s16
                +----+      +----+      +----+
            s17 | p6 |  s18 | p7 |  s19 | p8 |  s20
                +----+      +----+      +----+
                  s21         s22         s23
        """
        s0 = self._get_loc_side_options(self.locs[0], 1)
        s1 = self._get_loc_side_options(self.locs[1], 1)
        s2 = self._get_loc_side_options(self.locs[2], 1)

        s3 = self._get_loc_side_options(self.locs[0], 4)
        s4 = self._get_loc_side_options(self.locs[1], 4)
        s5 = self._get_loc_side_options(self.locs[2], 4)
        s6 = self._get_loc_side_options(self.locs[2], 2)

        s7 = self._get_loc_side_options(self.locs[3], 1)
        s8 = self._get_loc_side_options(self.locs[4], 1)
        s9 = self._get_loc_side_options(self.locs[5], 1)

        s10 = self._get_loc_side_options(self.locs[3], 4)
        s11 = self._get_loc_side_options(self.locs[4], 4)
        s12 = self._get_loc_side_options(self.locs[5], 4)
        s13 = self._get_loc_side_options(self.locs[5], 2)

        s14 = self._get_loc_side_options(self.locs[6], 1)
        s15 = self._get_loc_side_options(self.locs[7], 1)
        s16 = self._get_loc_side_options(self.locs[8], 1)

        s17 = self._get_loc_side_options(self.locs[6], 4)
        s18 = self._get_loc_side_options(self.locs[7], 4)
        s19 = self._get_loc_side_options(self.locs[8], 4)
        s20 = self._get_loc_side_options(self.locs[8], 2)

        s21 = self._get_loc_side_options(self.locs[6], 3)
        s22 = self._get_loc_side_options(self.locs[7], 3)
        s23 = self._get_loc_side_options(self.locs[8], 3)

        self.side_options = [s0, s1, s2,
                             s3, s4, s5, s6,
                             s7, s8, s9,
                             s10, s11, s12, s13,
                             s14, s15, s16,
                             s17, s18, s19, s20,
                             s21, s22, s23]

        self.side_options_rev = [self._reverse_sides(s) for s in self.side_options]

    def _find_filled_locs(self):
        for p_nr, loc in enumerate(self.locs):
            s1, s2, s3, s4 = self.side_nrs[p_nr]
            options1 = self.side_options[s1]
            options2 = self.side_options[s2]
            options3 = self.side_options_rev[s3]
            options4 = self.side_options_rev[s4]

            if len(options1) == 1 and len(options2) == 1 and len(options3) == 1 and len(options4) == 1:
                # completely decided locations; no need to evaluate
                self.stdout.write('[INFO] loc %s is filled' % loc)
                self.board_order.append(loc)
                self.board[p_nr] = Piece2x2(nr=0,                   # dummy
                                            nr1=0, nr2=0, nr3=0, nr4=0,
                                            side1=options1[0],
                                            side2=options2[0],
                                            side3=options3[0],
                                            side4=options4[0])
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

    def _iter(self, options_side1, options_side2, options_side3, options_side4):
        unused = self.board_unused
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
            propagate_segment_reduction(self.processor, segment)

    def _decide_p_nr_order(self):
        qset = Piece2x2.objects.filter(nr1__in=self.board_unused,
                                       nr2__in=self.board_unused,
                                       nr3__in=self.board_unused,
                                       nr4__in=self.board_unused)

        p_nr_counts = list()
        for p_nr in range(9):
            if self.board[p_nr] is None:
                # empty position on the board
                s1, s2, s3, s4 = self.side_nrs[p_nr]
                options_side1 = self.side_options[s1]
                options_side2 = self.side_options[s2]
                options_side3 = self.side_options_rev[s3]
                options_side4 = self.side_options_rev[s4]

                n1, n2, n3, n4 = self.neighbours[p_nr]
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
                tup = (count, p_nr)
                p_nr_counts.append(tup)
        # for

        p_nr_counts.sort()  # smallest first
        self.p_nrs_order = [tup[-1] for tup in p_nr_counts]
        self.stdout.write('[INFO] p_nr order: %s' % repr(self.p_nrs_order))

    def _select_p_nr(self):
        # decide which position on the board has the fewest options

        # follow previous solve order
        for p_nr in self.p_nrs_order:
            if self.board[p_nr] is None:
                return p_nr, False
        # for

        # decide the next best position on the board to solve

        qset = Piece2x2.objects.filter(nr1__in=self.board_unused,
                                       nr2__in=self.board_unused,
                                       nr3__in=self.board_unused,
                                       nr4__in=self.board_unused)

        p_nr_counts = list()
        for p_nr in range(len(self.locs)):
            if self.board[p_nr] is None:
                # empty position on the board
                s1, s2, s3, s4 = self.side_nrs[p_nr]
                options_side1 = self.side_options[s1]
                options_side2 = self.side_options[s2]
                options_side3 = self.side_options_rev[s3]
                options_side4 = self.side_options_rev[s4]

                n1, n2, n3, n4 = self.neighbours[p_nr]
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
                tup = (count, p_nr)
                p_nr_counts.append(tup)

                if count == 0:
                    # dead end
                    # self.stdout.write('[DEBUG] No options for %s' % p_nr)
                    return -1, True
        # for

        # take the lowest
        if len(p_nr_counts) > 0:
            p_nr_counts.sort()       # lowest first
            p_nr = p_nr_counts[0][-1]
            # self.stdout.write('[INFO] Added %s' % p_nr)
            self.p_nrs_order.append(p_nr)
            return p_nr, False

        # niets kunnen kiezen
        self.stdout.write('[DEBUG] select_p_nr failure')
        return -1, True

    def _find_recurse(self):
        tick = time.monotonic()
        if tick - self.prev_tick > 30:
            self.prev_tick = tick
            msg = '(%s) %s' % (len(self.board_order), repr([self.locs[idx] for idx in self.board_order]))
            # print(msg)
            self.progress.solve_order = msg
            self.progress.updated = timezone.now()
            self.progress.save(update_fields=['solve_order', 'updated'])

        if len(self.board_order) == len(self.locs):
            return True

        # decide which p_nr to continue with
        p_nr, has_zero = self._select_p_nr()
        if has_zero:
            return False

        s1, s2, s3, s4 = self.side_nrs[p_nr]
        options_side1 = self.side_options[s1]
        options_side2 = self.side_options[s2]
        options_side3 = self.side_options_rev[s3]
        options_side4 = self.side_options_rev[s4]

        n1, n2, n3, n4 = self.neighbours[p_nr]
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

        for p in self._iter(options_side1, options_side2, options_side3, options_side4):
            self._board_place(p_nr, p)
            found = self._find_recurse()
            self._board_pop()

            if found:
                return True
        # for

        return False

    def _find_reduce(self, p_nr, side_n, s_nr):
        if self.board[p_nr] is not None:
            return

        segment = calc_segment(self.locs[p_nr], side_n)
        sides = self.side_options[s_nr]
        todo = len(sides)
        self.stdout.write('[INFO] Checking %s options in segment %s' % (len(sides), segment))
        self.p_nrs_order = list()       # allow deciding optimal order anew

        updated = list()
        if segment != self.progress.segment:
            self.progress.segment = segment
            updated.append('segment')

        if todo != self.progress.todo_count:
            self.progress.todo_count = todo
            updated.append('todo_count')

        for side in sides:
            # update the progress record in the database
            if todo != self.progress.left_count:
                self.progress.left_count = todo
                updated.append('left_count')
            self.progress.updated = timezone.now()
            updated.append('updated')
            self.progress.save(update_fields=updated)
            updated = list()

            # place the first piece
            s1, s2, s3, s4 = self.side_nrs[p_nr]
            options_side1 = self.side_options[s1]
            options_side2 = self.side_options[s2]
            options_side3 = self.side_options_rev[s3]
            options_side4 = self.side_options_rev[s4]

            if side_n == 1:
                options_side1 = [side]
            elif side_n == 2:
                options_side2 = [side]
            elif side_n == 3:
                options_side3 = [self.twoside2reverse[side]]
            else:   # side_n == 4:
                options_side4 = [self.twoside2reverse[side]]

            found = False
            for p in self._iter(options_side1, options_side2, options_side3, options_side4):
                self._board_place(p_nr, p)
                found = self._find_recurse()
                self._board_pop()
                if found:
                    break
            # for

            if not found:
                self._reduce(segment, side)

            todo -= 1
            self.stdout.write('[INFO] Remaining: %s/%s' % (todo, len(sides)))
            self.prev_tick = time.monotonic()
        # for

    def handle(self, *args, **options):
        """
                  s0          s1          s2
                +----+      +----+      +----+
            s3  | p0 |  s4  | p1 |  s5  | p2 |  s6
                +----+      +----+      +----+
                  s7          s8          s9
                +----+      +----+      +----+
            s10 | p3 |  s11 | p4 |  s12 | p5 |  s13
                +----+      +----+      +----+
                  s14         s15        s16
                +----+      +----+      +----+
            s17 | p6 |  s18 | p7 |  s19 | p8 |  s20
                +----+      +----+      +----+
                  s21         s22         s23
        """

        if options['dryrun']:
            self.do_commit = False

        loc = options['loc'][0]
        if loc < 1 or loc > 46 or loc in (7, 8,
                                          15, 16,
                                          23, 24,
                                          31, 32,
                                          39, 40):
            self.stderr.write('[ERROR] Invalid location')
            return
        self.locs = (loc + 0, loc + 1, loc + 2,
                     loc + 8, loc + 9, loc + 10,
                     loc + 16, loc + 17, loc + 18)
        self.stdout.write('[INFO] Locations: %s' % repr(self.locs))

        self.processor = options['processor'][0]
        self.stdout.write('[INFO] Processor=%s' % self.processor)

        self.board_unused = self._get_unused()

        self._get_side_options()
        # self.stdout.write('%s' % ", ".join([str(len(opt)) for opt in self.side_options]))

        self._find_filled_locs()

        self.prev_tick = time.monotonic()

        self.progress = EvalProgress(
                            eval_size=9,
                            eval_loc=self.locs[0],
                            processor=self.processor,
                            segment=0,
                            todo_count=0,
                            left_count=0,
                            solve_order='',
                            updated=timezone.now())
        self.progress.save()

        try:
            self._find_reduce(4, 1, 8)
            self._find_reduce(4, 2, 12)
            self._find_reduce(4, 3, 15)
            self._find_reduce(4, 4, 11)

            self._find_reduce(1, 4, 4)
            self._find_reduce(1, 2, 5)

            self._find_reduce(3, 1, 7)
            self._find_reduce(3, 3, 14)

            self._find_reduce(5, 1, 9)
            self._find_reduce(5, 3, 16)

            self._find_reduce(7, 4, 18)
            self._find_reduce(7, 2, 19)
        except KeyboardInterrupt:
            pass

        self.progress.delete()

        if self.reductions == 0:
            self.stdout.write('[INFO] No reductions')
        else:
            self.stdout.write('[INFO] Reductions: %s' % self.reductions)
            if not self.do_commit:
                self.stdout.write('[WARNING] Use --commit to keep')

# end of file
