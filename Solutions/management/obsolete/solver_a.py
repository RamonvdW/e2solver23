# -*- coding: utf-8 -*-

#  Copyright (c) 2023-2024 Ramon van der Winkel.
#  All rights reserved.
#  Licensed under BSD-3-Clause-Clear. See LICENSE file for details.

from django.core.management.base import BaseCommand
from Pieces2x2.models import TwoSides, Piece2x2
from Solutions.models import Solution, P_CORNER, P_BORDER, P_HINTS, ALL_HINT_NRS
import datetime


class Command(BaseCommand):

    help = "Solver A"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.verbose = 0
        self.board = dict()             # [nr] = Piece2x2
        self.board_options = dict()     # [nr] = count of possible Piece2x2
        self.board_gap_count = 0
        self.board_unused_nrs = []
        self.lowest_gap_count = 0
        self.last_used_state = 0
        self.neighbours = dict()     # [nr] = (side 1, 2, 3, 4 neighbour nrs)
        self._evict_cache = []
        self._solve_nr = 0
        self._count_cache = dict()
        self.board_solve_order = []     # [nr, nr, ..]

        self._calc_neighbours()

        self.rev_border = TwoSides.objects.get(two_sides='XX').nr
        self.side_nr2reverse = dict()
        two2nr = dict()
        for two in TwoSides.objects.all():
            two2nr[two.two_sides] = two.nr
        # for
        for two_sides, nr in two2nr.items():
            two_rev = two_sides[1] + two_sides[0]
            rev_nr = two2nr[two_rev]
            self.side_nr2reverse[nr] = rev_nr
        # for

    def _calc_neighbours(self):
        for nr in range(1, 64+1):
            self.neighbours[nr] = (nr - 8, nr + 1, nr + 8, nr - 1)

        # redo the corners
        self.neighbours[1] = (0, 1 + 1, 1 + 8, 0)
        self.neighbours[8] = (0, 0, 8 + 8, 8 - 1)
        self.neighbours[57] = (57 - 8, 57 + 1, 0, 0)
        self.neighbours[64] = (64 - 8, 0, 0, 64 - 1)

        # redo for the borders
        for nr in range(2, 7+1):
            self.neighbours[nr] = (0, nr + 1, nr + 8, nr - 1)
        for nr in range(9, 49+1, 8):
            self.neighbours[nr] = (nr - 8, nr + 1, nr + 8, 0)
        for nr in range(16, 56+1, 8):
            self.neighbours[nr] = (nr - 8, 0, nr + 8, nr - 1)
        for nr in range(58, 63+1):
            self.neighbours[nr] = (nr - 8, nr + 1, 0, nr - 1)

    def add_arguments(self, parser):
        parser.add_argument('--verbose', action='store_true')
        parser.add_argument('layout', nargs=1, help='Initial board layout to use')

    def _count_2x2(self, nr, unused_nrs):
        # get the sides
        s1, s2, s3, s4 = self._get_sides(nr)
        p1 = p2 = p3 = p4 = None
        x1 = x2 = x3 = x4 = None

        if nr in P_CORNER:
            if nr == 1:
                s1 = s4 = self.rev_border
            elif nr == 8:
                s1 = s2 = self.rev_border
            elif nr == 57:
                s3 = s4 = self.rev_border
            else:
                s2 = s3 = self.rev_border

        elif nr in P_BORDER:
            if nr < 9:
                s1 = self.rev_border
                x2 = self.rev_border
                x4 = self.rev_border

            elif nr > 57:
                x2 = self.rev_border
                s3 = self.rev_border
                x4 = self.rev_border

            elif nr & 1 == 1:
                x1 = self.rev_border
                x3 = self.rev_border
                s4 = self.rev_border

            else:
                x1 = self.rev_border
                s2 = self.rev_border
                x3 = self.rev_border

        else:
            x1 = x2 = x3 = x4 = self.rev_border

            if nr in P_HINTS:
                if nr == 10:
                    p1 = 208
                elif nr == 15:
                    p2 = 255
                elif nr == 36:
                    p2 = 139
                elif nr == 50:
                    p3 = 181
                elif nr == 55:
                    p4 = 249

        tup = (s1, s2, s3, s4, p1, p2, p3, p4, x1, x2, x3, x4, tuple(unused_nrs))
        try:
            count = self._count_cache[tup]
        except KeyError:
            qset = Piece2x2.objects.all()

            if s1:
                qset = qset.filter(side1=s1)
            elif x1:
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
            else:
                qset = qset.filter(nr1__in=unused_nrs)

            if p2:
                qset = qset.filter(nr2=p2)
            else:
                qset = qset.filter(nr2__in=unused_nrs)

            if p3:
                qset = qset.filter(nr3=p3)
            else:
                qset = qset.filter(nr3__in=unused_nrs)

            if p4:
                qset = qset.filter(nr4=p4)
            else:
                qset = qset.filter(nr4__in=unused_nrs)

            self._count_cache[tup] = count = qset.count()

        return count

    def _count_all(self, work_nr):
        self._count_cache = dict()

        nrs = list(self.neighbours[work_nr])
        for nr in range(1, 64+1):
            if nr not in nrs:
                nrs.append(nr)
        # for

        for nr in nrs:
            if nr > 0 and self.board[nr] is None:
                self.board_options[nr] = count = self._count_2x2(nr, self.board_unused_nrs)
                if count == 0:
                    # found a dead end
                    self.stdout.write(' [%s] no options for %s' % (work_nr, nr))
                    return True
        # for
        return False

    def _document_gaps(self, sol):
        for nr in range(1, 64+1):
            p = self.board[nr]
            if not p:
                # gap
                field_note = 'note%s' % nr

                # could the number of Piece2x2 that could fit here, not considered unused_nrs
                count1 = self.board_options[nr]     # self._count_2x2(nr, self.board_unused_nrs)
                count2 = self._count_2x2(nr, self.all_unused_nrs)
                note = '%s (max %s)' % (count1, count2)

                setattr(sol, field_note, note)
        # for

    def _save_board(self):
        base_nrs = []
        p_count = 0
        nrs = [0]
        for nr in range(1, 64+1):
            p = self.board[nr]
            if p:
                nrs.append(p.nr)
                base_nrs.extend([p.nr1, p.nr2, p.nr3, p.nr4])
                p_count += 1
            else:
                nrs.append(0)
        # for

        l1 = len(set(base_nrs))
        l2 = p_count * 4
        if l1 != l2:
            self.stdout.write('[ERROR] Solution has %s instead of %s base nrs: %s' % (l1, l2, repr(base_nrs)))
            return

        sol_nr = 1
        s = Solution.objects.all().order_by('-nr').first()
        if s:
            sol_nr = s.nr + 1

        self.stdout.write('[INFO] Saving board %s with gap count %s' % (sol_nr, self.board_gap_count))

        sol = Solution(
                nr=sol_nr,
                state=self.last_used_state,
                gap_count=self.board_gap_count)

        for nr in range(1, 64+1):
            field_nr = 'nr%s' % nr
            setattr(sol, field_nr, nrs[nr])
        # for

        self._document_gaps(sol)

        sol.save()

        self.stdout.write('[INFO] Done')

    def _board_free_nr(self, nr):
        p = self.board[nr]
        if p:
            if self.verbose:
                self.stdout.write('-[%s] = %s' % (nr, p.nr))
            self.board[nr] = None
            free_nrs = [nr for nr in (p.nr1, p.nr2, p.nr3, p.nr4) if nr not in ALL_HINT_NRS]
            self.board_unused_nrs.extend(free_nrs)
            self.board_gap_count += 1

    def _board_fill_nr(self, nr, p):
        if self.verbose:
            self.stdout.write('+[%s] = %s with base nrs %s' % (nr, p.nr, repr([p.nr1, p.nr2, p.nr3, p.nr4])))

        p.exp_s1 = self.side_nr2reverse[p.side3]
        p.exp_s2 = self.side_nr2reverse[p.side4]
        p.exp_s3 = self.side_nr2reverse[p.side1]
        p.exp_s4 = self.side_nr2reverse[p.side2]

        self.board[nr] = p
        for nr in (p.nr1, p.nr2, p.nr3, p.nr4):
            try:
                self.board_unused_nrs.remove(nr)
            except ValueError:
                # happens with the hints
                pass
        # for
        self.board_gap_count -= 1

    def _select_solve_nr(self):
        self._solve_nr += 1
        if self._solve_nr > 64:
            self._solve_nr = 1

        # find a free spot on the board
        limiter = 65
        while self.board[self._solve_nr] and limiter > 0:
            limiter -= 1
            self._solve_nr += 1
            if self._solve_nr > 64:
                self._solve_nr = 1
        # while

        if limiter == 0:
            self.stdout.write('[INFO] Could not find a free position on the board!')

        return self._solve_nr

    def _get_sides(self, nr):
        nr1, nr2, nr3, nr4 = self.neighbours[nr]

        s1 = s2 = s3 = s4 = None

        if nr1 > 0:
            p = self.board[nr1]
            if p:
                s1 = p.exp_s1

        if nr2 > 0:
            p = self.board[nr2]
            if p:
                s2 = p.exp_s2

        if nr3 > 0:
            p = self.board[nr3]
            if p:
                s3 = p.exp_s3

        if nr4 > 0:
            p = self.board[nr4]
            if p:
                s4 = p.exp_s4

        return s1, s2, s3, s4

    def _iter_for_nr(self, nr, greater_than):

        # get the sides
        s1, s2, s3, s4 = self._get_sides(nr)
        p1 = p2 = p3 = p4 = None
        x1 = x2 = x3 = x4 = None

        if nr in P_CORNER:
            if nr == 1:
                s1 = s4 = self.rev_border
            elif nr == 8:
                s1 = s2 = self.rev_border
            elif nr == 57:
                s3 = s4 = self.rev_border
            else:
                s2 = s3 = self.rev_border

        elif nr in P_BORDER:
            if nr < 9:
                s1 = self.rev_border
                x2 = self.rev_border
                x4 = self.rev_border

            elif nr > 57:
                x2 = self.rev_border
                s3 = self.rev_border
                x4 = self.rev_border

            elif nr & 1 == 1:
                x1 = self.rev_border
                x3 = self.rev_border
                s4 = self.rev_border

            else:
                x1 = self.rev_border
                s2 = self.rev_border
                x3 = self.rev_border

        else:
            x1 = x2 = x3 = x4 = self.rev_border

            if nr in P_HINTS:
                if nr == 10:
                    p1 = 208
                elif nr == 15:
                    p2 = 255
                elif nr == 36:
                    p2 = 139
                elif nr == 50:
                    p3 = 181
                elif nr == 55:
                    p4 = 249

        # print('[%s] s=%s,%s,%s,%s x=%s,%s,%s,%s p=%s,%s,%s,%s' % (nr, s1, s2, s3, s4, x1, x2, x3, x4, p1, p2, p3, p4))

        qset = Piece2x2.objects.filter(nr__gt=greater_than).order_by('nr')

        if s1:
            qset = qset.filter(side1=s1)
        elif x1:
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
        else:
            qset = qset.filter(nr1__in=self.board_unused_nrs)

        if p2:
            qset = qset.filter(nr2=p2)
        else:
            qset = qset.filter(nr2__in=self.board_unused_nrs)

        if p3:
            qset = qset.filter(nr3=p3)
        else:
            qset = qset.filter(nr3__in=self.board_unused_nrs)

        if p4:
            qset = qset.filter(nr4=p4)
        else:
            qset = qset.filter(nr4__in=self.board_unused_nrs)

        for p in qset:
            yield p

    def _try_fill_nr(self, nr, greater_than):
        for p in self._iter_for_nr(nr, greater_than):
            self._board_fill_nr(nr, p)
            is_dead_end = self._count_all(nr)
            if not is_dead_end:
                return True     # success
            self._board_free_nr(nr)
        # for
        return False            # failure

    def _init_board(self, layout):
        for nr in range(1, 64+1):
            self.board[nr] = None
        # for

        self.board_unused_nrs = [nr for nr in range(1, 256+1) if nr not in ALL_HINT_NRS]
        self.board_gap_count = self.lowest_gap_count = 64
        self.all_unused_nrs = self.board_unused_nrs[:]

        # fill every other position of the board
        if layout == '1':
            nr = 1
            row = 1
            while nr < 64:
                # print(row, nr)
                self._try_fill_nr(nr)
                self._try_fill_nr(nr+2)
                self._try_fill_nr(nr+4)
                self._try_fill_nr(nr+6)

                if row & 1 == 0:
                    nr += 7
                else:
                    nr += 9

                row += 1
            # for

        elif layout == '2':
            nr = 2
            row = 1
            while nr < 64:
                # print(row, nr)
                self._try_fill_nr(nr)
                self._try_fill_nr(nr+2)
                self._try_fill_nr(nr+4)
                self._try_fill_nr(nr+6)

                if row & 1 == 1:
                    nr += 7
                else:
                    nr += 9

                row += 1
            # for

        elif layout == '3':
            pass

        else:
            self.stderr.write('[ERROR] Unknown layout %s' % repr(layout))

        self._count_all(1)

    def handle(self, *args, **options):

        if options['verbose']:
            self.verbose += 1

        next = datetime.datetime.now() + datetime.timedelta(minutes=15)

        self.stdout.write('[INFO] Initializing board')
        self._init_board(options['layout'][0])
        self._save_board()

        while self.board_gap_count > 0:

            # find spot with fewest options
            best_spot = []
            for nr in range(1, 64+1):
                p = self.board[nr]
                if not p:
                    if self.board_gap_count <= 28 or (nr not in P_CORNER and nr not in P_BORDER):
                        options = self.board_options[nr]
                        tup = (options, nr)
                        best_spot.append(tup)
            # for
            best_spot.sort()    # lowest first

            nr = best_spot[0][1]
            greater_than = 0
            placed_piece = False
            while not placed_piece:
                if self._try_fill_nr(nr, greater_than):
                    # success
                    self.board_solve_order.append(nr)
                    placed_piece = True
                else:
                    # backtrack and continue with next option in previous spot
                    nr = self.board_solve_order.pop(-1)
                    p = self.board[nr]
                    greater_than = p.nr
                    # self.stdout.write('[INFO] Backtracked to nr %s with greater_than %s' % (nr, greater_than))
                    self._board_free_nr(nr)
            # while

            if datetime.datetime.now() > next:
                self.stdout.write('[INFO] Information milestone')
                self._save_board()
                next += datetime.timedelta(minutes=15)

            if self.board_gap_count < self.lowest_gap_count:
                self.lowest_gap_count = self.board_gap_count
                self._save_board()
                while self.board_gap_count == 0:
                    self.stderr.write('[INFO] Found a solution!')
                    return
        # while

        self._save_board()

# end of file
