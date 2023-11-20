# -*- coding: utf-8 -*-

#  Copyright (c) 2023 Ramon van der Winkel.
#  All rights reserved.
#  Licensed under BSD-3-Clause-Clear. See LICENSE file for details.

from django.core.management.base import BaseCommand
from Pieces2x2.models import TwoSides, Piece2x2
from Solutions.models import Solution4x4, Solution6x6, P_CORNER, P_BORDER, P_HINTS
import time

ALL_HINT_NRS = (139, 181, 209, 249, 255)


class Command(BaseCommand):

    help = "Solver 6x6"

    """
         1   2  3  4  5  6  7   8
          
         9  10 11 12 13 14 15  16
        17  18 19 20 21 22 23  24
        25  26 27 28 29 30 31  32
        33  34 35 36 37 38 39  40
        41  42 43 44 45 46 47  48
        49  50 51 52 53 54 55  56
         
        57  58 59 60 61 62 63  64
    """

    solve_order = (
        13, 39, 52, 26,     # starter in each side
        12, 31, 53, 34,     # big plus
        11, 18, 10,         # corner 1
        14, 23, 15,         # corner 2
        47, 54, 55,         # corner 3
        42, 51, 50,         # corner 4
    )

    # solve_order = (
    #     12, 13,
    #     31, 39,
    #     52, 53,
    #     34, 26,       # grote plus = 24
    #
    #     11, 18, 10,   # corner 1
    #     14, 23, 15,   # corner 2
    #     47, 54, 55,   # corner 3
    #     42, 51, 50,   # corner 4
    # )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.verbose = 0
        self.board = dict()                 # [nr] = Piece2x2
        self.board_options = dict()         # [nr] = count of possible Piece2x2
        self.board_gap_count = 0
        self.board_unused_nrs = list()
        self.neighbours = dict()            # [nr] = (side 1, 2, 3, 4 neighbour nrs)
        self._count_cache = dict()
        self.board_solve_order = list()     # [nr, nr, ..]
        self.all_unused_nrs = list()
        self.based_on = 0

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

    def _count_all(self, work_nr, min_options):
        self._count_cache = dict()

        # start with the neighbours so we can quickly find a dead-end
        nrs = list(self.neighbours[work_nr])
        for nr in range(1, 64+1):
            if nr not in nrs:
                nrs.append(nr)
        # for

        for nr in nrs:
            if nr > 0 and self.board[nr] is None:
                self.board_options[nr] = count = self._count_2x2(nr, self.board_unused_nrs)
                if count < min_options:
                    # found a dead end
                    # self.stdout.write(' [%s] less than %s options for %s' % (work_nr, min_options, nr))
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

    def _save_board6x6(self):
        base_nrs = list()
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

        self.stdout.write('[INFO] Saving board with gap count %s' % self.board_gap_count)

        sol = Solution6x6(
                based_on_4x4=self.based_on)

        for nr in range(1, 64+1):
            if nr not in (1, 2, 3, 4, 5, 6, 7, 8,
                          9, 16,
                          17, 24,
                          25, 32,
                          33, 40,
                          41, 48,
                          49, 56,
                          57, 58, 59, 60, 61, 62, 63, 64):
                field_nr = 'nr%s' % nr
                setattr(sol, field_nr, nrs[nr])
        # for

        self._document_gaps(sol)

        sol.save()

        self.stdout.write('[INFO] Saved board %s' % sol.pk)

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

    def _try_fill_nr(self, nr, greater_than, min_options):
        for p in self._iter_for_nr(nr, greater_than):
            self._board_fill_nr(nr, p)
            is_dead_end = self._count_all(nr, min_options)
            if not is_dead_end:
                return True     # success
            self._board_free_nr(nr)
        # for
        return False            # failure

    def load_board_4x4(self, sol):
        for nr in range(1, 64+1):
            self.board[nr] = None
        # for

        self.board_unused_nrs = [nr for nr in range(1, 256+1) if nr not in ALL_HINT_NRS]

        for nr in (19, 20, 21, 22,
                   27, 28, 29, 30,
                   35, 36, 37, 38,
                   43, 44, 45, 46):

            field_nr = 'nr%s' % nr
            p_nr = getattr(sol, field_nr)
            p = Piece2x2.objects.get(nr=p_nr)       # TODO: get all with 1 query
            self._board_fill_nr(nr, p)
        # for

        self.board_gap_count = 64 - 16
        self.all_unused_nrs = self.board_unused_nrs[:]      # copy
        self._count_cache = dict()
        self.board_solve_order = list()     # [nr, nr, ..]
        self.based_on = sol.pk

        self._count_all(1, 1)

    def find_6x6(self):
        min_options = 1
        best = 999

        while self.board_gap_count > 0:

            current_depth = len(self.board_solve_order)
            if current_depth < len(self.solve_order):
                nr = self.solve_order[current_depth]
            else:
                nr = 0

            greater_than = 0
            placed_piece = False
            while not placed_piece:
                if nr > 0 and self._try_fill_nr(nr, greater_than, min_options):
                    # success
                    self.board_solve_order.append(nr)
                    placed_piece = True
                    if self.board_gap_count < best:
                        self._save_board6x6()
                        best = self.board_gap_count
                else:
                    # backtrack and continue with next option in previous spot
                    if len(self.board_solve_order) == 0:
                        self.stdout.write('[INFO] Reached the end')
                        return

                    nr = self.board_solve_order.pop(-1)
                    p = self.board[nr]
                    greater_than = p.nr
                    # self.stdout.write('[INFO] Backtracked to nr %s with greater_than %s' % (nr, greater_than))
                    self._board_free_nr(nr)
            # while

            if len(self.board_solve_order) == 36:
                self._save_board6x6()
        # while

    def handle(self, *args, **options):

        if options['verbose']:
            self.verbose += 1

        my_processor = int(time.time() - 946684800.0)     # seconds since Jan 1, 2000
        self.stdout.write('[INFO] my_processor is %s' % my_processor)

        while True:
            sol = Solution4x4.objects.filter(is_processed=False, processor=0).order_by('pk').first()     # lowest first

            if sol:
                self.stdout.write('[INFO] Loading Solution4x4 nr %s' % sol.pk)
                sol.processor = my_processor
                sol.save(update_fields=['processor'])

                self.load_board_4x4(sol)
                self.find_6x6()

                sol.is_processed = True
                sol.save(update_fields=['is_processed'])

            else:
                self.stdout.write('[INFO] Waiting for new 4x4 (press Ctrl+C to abort)')
                time.sleep(60)
        # while


# end of file
