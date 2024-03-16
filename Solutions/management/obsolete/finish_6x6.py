# -*- coding: utf-8 -*-

#  Copyright (c) 2023-2024 Ramon van der Winkel.
#  All rights reserved.
#  Licensed under BSD-3-Clause-Clear. See LICENSE file for details.

from django.core.management.base import BaseCommand
from Pieces2x2.models import TwoSides, Piece2x2
from Solutions.models import Solution4x4, Solution6x6, P_CORNER, P_BORDER, P_HINTS, ALL_HINT_NRS
import datetime
import time


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

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.verbose = 0
        self.board = dict()                 # [nr] = Piece2x2
        self.board_options = dict()         # [nr] = count of possible Piece2x2
        self.board_must_have = dict()       # [nr] = list(base nrs)
        self.board_criticality = dict()     # [nr] = number (lower is more critical)
        self.board_freedom = dict()         # [nr] = "statement"
        self.board_gap_count = 0
        self.board_unused_nrs = []
        self.neighbours = dict()            # [nr] = (side 1, 2, 3, 4 neighbour nrs)
        self._count_freedom_cache = dict()
        self.board_solve_order = []     # [nr, nr, ..]
        # self.all_unused_nrs = []
        self.based_on = 0
        self.interval_mins = 15

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
        parser.add_argument('--interval', nargs=1, help='Interval in minutes (default: 15) for saving progress board')

    def _count_2x2(self, nr, unused_nrs):
        # get the sides
        s1, s2, s3, s4 = self._get_sides(nr)
        p1 = p2 = p3 = p4 = None
        x1 = x2 = x3 = x4 = None
        has_hint = False

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
                has_hint = True
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

        must_have_nrs = []

        tup = (s1, s2, s3, s4, p1, p2, p3, p4, x1, x2, x3, x4, tuple(unused_nrs))
        try:
            count, freedom = self._count_freedom_cache[tup]
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

            count = qset.count()

            if count > 0:
                avail_nr1 = list(qset.distinct('nr1').values_list('nr1', flat=True))
                avail_nr2 = list(qset.distinct('nr2').values_list('nr2', flat=True))
                avail_nr3 = list(qset.distinct('nr3').values_list('nr3', flat=True))
                avail_nr4 = list(qset.distinct('nr4').values_list('nr4', flat=True))

                avail_nrs = set(avail_nr1 + avail_nr2 + avail_nr3 + avail_nr4)
                avail_len = len(avail_nrs)

                if avail_len == 0 or avail_len > 5:
                    freedom = str(avail_len)
                else:
                    avail_nrs = list(avail_nrs)
                    avail_nrs.sort()
                    avail_nrs = [str(nr) for nr in avail_nrs]
                    freedom = ",".join(avail_nrs)

                for avail in (avail_nr1, avail_nr2, avail_nr3, avail_nr4):
                    if len(avail) == 1:
                        must_have_nrs.append(avail[0])
                # for

                # if nr == 12 and count < 20:
                #     print('[%s] count=%s, freedom=%s, must_have_nrs=%s' % (nr, count, freedom, must_have_nrs))
                #     print('     p1: %s' % avail_nr1)
                #     print('     p2: %s' % avail_nr2)
                #     print('     p3: %s' % avail_nr3)
                #     print('     p4: %s' % avail_nr4)
            else:
                freedom = '0'

            self._count_freedom_cache[tup] = (count, freedom)

        return count, freedom, must_have_nrs

    def _count_all(self, work_nr, min_options):
        self._count_freedom_cache = dict()

        # start with the neighbours so we can quickly find a dead-end
        nrs = list(self.neighbours[work_nr])
        for nr in range(1, 64+1):
            if nr not in nrs:
                nrs.append(nr)
        # for

        for nr in nrs:
            if nr > 0 and self.board[nr] is None:
                # empty spot on the board
                count, freedom, must_have_nrs = self._count_2x2(nr, self.board_unused_nrs)
                print('[%s] count=%s, freedom=%s, must_have_nrs=%s' % (nr, count, freedom, must_have_nrs))
                self.board_options[nr] = count
                self.board_freedom[nr] = freedom
                self.board_must_have[nr] = must_have_nrs

                if "," in freedom:
                    # is listing critical base pieces are critical
                    self.board_criticality[nr] = freedom.count(',')
                elif freedom == "?":
                    self.board_criticality[nr] = 999
                elif freedom == "20+":
                    self.board_criticality[nr] = 20
                else:
                    # convert back to number
                    self.board_criticality[nr] = int(freedom)

                if count < min_options:
                    # found a dead end
                    # self.stdout.write(' [%s] less than %s options for %s' % (work_nr, min_options, nr))
                    return True
        # for
        return False

    def _count_important(self, work_nr, min_options):
        self._count_freedom_cache = dict()

        important = (
            (10, 9, 1, 2),
            (11, 3),
            (12, 4),
            (13, 5),
            (14, 6),
            (15, 7, 8, 16),
            (23, 24),
            (31, 32),
            (39, 40),
            (47, 48),
            (55, 56, 64, 63),
            (54, 62),
            (53, 61),
            (52, 60),
            (51, 59),
            (50, 58, 57, 49),
            (42, 41),
            (34, 33),
            (26, 25),
            (18, 17),
        )

        # start with the neighbours so we can quickly find a dead-end
        nrs = list(self.neighbours[work_nr])
        for tup in important:
            nr = tup[0]
            if self.board[nr] is None:
                nrs.append(nr)
            else:
                for nr in tup[1:]:
                    nrs.append(nr)
        # for
        nrs = set(nrs)      # removes dupes

        for nr in nrs:
            if nr > 0 and self.board[nr] is None:
                # empty spot on the board
                count, freedom, must_have_nrs = self._count_2x2(nr, self.board_unused_nrs)
                self.board_options[nr] = count
                self.board_freedom[nr] = freedom
                self.board_must_have[nr] = must_have_nrs
                if "," in freedom:
                    # is listing critical base pieces are critical
                    self.board_criticality[nr] = freedom.count(',')
                elif freedom == "?":
                    self.board_criticality[nr] = 999
                elif freedom == "20+":
                    self.board_criticality[nr] = 20
                else:
                    # convert back to number
                    self.board_criticality[nr] = int(freedom)

                if count < min_options:
                    # found a dead end
                    self.stdout.write(' [%s] less than %s options for %s' % (work_nr, min_options, nr))
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
                freedom = self.board_freedom[nr]
                # count2, _, _ = self._count_2x2(nr, self.board_unused_nrs)
                # note = '%s{%s}%s' % (count1, count2, freedom)
                note = "%s %s" % (count1, freedom)
                note = note[:30]        # avoid database errors

                setattr(sol, field_note, note)
        # for

    def _save_board6x6(self):
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
            base_nrs.sort()
            self.stdout.write('[ERROR] Solution has %s instead of %s base nrs: %s' % (l1, l2, repr(base_nrs)))

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

        reserved_nrs = []
        for chk_nr in range(1, 64+1):
            if chk_nr != nr:
                reserved_nrs.extend(self.board_must_have[chk_nr])
        # for
        # print('[%s] reserved_nrs=%s' % (nr, reserved_nrs))

        # skip outer borders
        # skip base pieces reserved for certain positions on the board
        unused_nrs = [nr for nr in self.board_unused_nrs if nr > 60 and nr not in reserved_nrs]

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

        # print(qset.explain())

        todo = qset.count()
        for p in qset:
            print('%s[%s] %s left' % (" " * len(self.board_solve_order), nr, todo))
            yield p
            todo -= 1

    def _try_fill_nr(self, nr, greater_than, min_options):
        for p in self._iter_for_nr(nr, greater_than):
            print('[%s] trying %s' % (nr, p.nr))
            self._board_fill_nr(nr, p)
            # is_dead_end = self._count_all(nr, min_options)
            is_dead_end = self._count_important(nr, min_options)
            if not is_dead_end:
                return True     # success
            self._board_free_nr(nr)
        # for
        return False            # failure

    def load_partial(self, partial):
        for nr in range(1, 64+1):
            self.board[nr] = None
            self.board_criticality[nr] = 999
        # for

        # start at 65 to skip all outer border pieces?
        self.board_unused_nrs = [nr for nr in range(1, 256+1) if nr not in ALL_HINT_NRS]

        for nr, p_nr in partial.items():
            if p_nr > 0:
                p = Piece2x2.objects.get(nr=p_nr)
                self._board_fill_nr(nr, p)
        # for

        self.board_gap_count = 64 - 16
        # self.all_unused_nrs = self.board_unused_nrs[:]      # copy
        self._count_freedom_cache = dict()
        self.board_solve_order = []     # [nr, nr, ..]
        self.based_on = 0

        # lst = self.board_unused_nrs[:]
        # lst.sort()
        # print('[DEBUG] Unused base nrs (excl. hints): %s' % ", ".join([str(nr) for nr in lst]))

        self._count_all(1, 1)

    def get_next_nr(self):
        # collect all
        # print('get_next_nr:')
        # print('  board_solve_order = %s' % repr(self.board_solve_order))

        current_depth = len(self.board_solve_order)
        # print('  current_depth = %s' % current_depth)

        # if current_depth < 8:
        #     solve_start = (11, 13, 23, 39, 54, 52, 42, 26)
        #     nr = solve_start[current_depth]
        #     return nr

        solve_todo = (
            10, 11, 12, 13, 14, 15,
            18, 23, 26, 31, 34, 39, 42, 47,
            50, 51, 52, 53, 54, 55)

        corners_todo = (10, 15, 50, 55)

        if current_depth >= 20:
            # trigger back-tracking
            nr = 0
        else:
            # find the critical items
            critical = []
            corners = []
            for nr in solve_todo:
                if nr not in self.board_solve_order:
                    tup = (self.board_criticality[nr], nr)
                    critical.append(tup)
                    if nr in corners_todo:
                        corners.append(nr)
            # for
            critical.sort()     # smallest first
            # print('   critical nrs:')
            # for tup in critical[:5]:
            #     print('      [%s] %s' % (tup[1], tup[0]))
            # # for

            if len(corners) == 1 and len(critical) > 1:
                # preference is to wait with the last corner
                idx = 0
                while idx < len(critical) and critical[idx][1] in corners:
                    idx += 1
                tup = critical[idx]
            else:
                tup = critical[0]
            nr = tup[1]

            # nr = solve_order[current_depth]

        print('  returning nr = %s' % nr)
        return nr

    def find_6x6(self):

        next_time = datetime.datetime.now() + datetime.timedelta(minutes=self.interval_mins)
        min_options = 1
        best = 999

        for nr in range(1, 64+1):
            self.board_must_have[nr] = []
        # for

        while True:

            nr = self.get_next_nr()     # can return 0 to trigger backtracking

            greater_than = 0
            placed_piece = False
            while not placed_piece:
                if nr > 0 and self._try_fill_nr(nr, greater_than, min_options):
                    # success
                    self.board_solve_order.append(nr)
                    placed_piece = True
                    if self.board_gap_count < best:
                        self._save_board6x6()
                        next_time = datetime.datetime.now() + datetime.timedelta(minutes=self.interval_mins)
                        best = self.board_gap_count
                else:
                    # backtrack and continue with next option in previous spot
                    if len(self.board_solve_order) == 0:
                        self.stdout.write('[INFO] Reached the end')
                        return

                    nr = self.board_solve_order.pop(-1)
                    p = self.board[nr]
                    if not p:
                        self.stderr.write('[DEBUG] No p2x2 at nr %s !!' % nr)
                        return
                    greater_than = p.nr
                    # self.stdout.write('[INFO] Backtracked to nr %s with greater_than %s' % (nr, greater_than))
                    self._board_free_nr(nr)
                    self._count_important(nr, min_options)      # update the criticality stats
            # while

            if len(self.board_solve_order) == 36:
                self._save_board6x6()

            if datetime.datetime.now() > next_time:
                self.stdout.write('[INFO] Progress milestone')
                self._save_board6x6()
                next_time = datetime.datetime.now() + datetime.timedelta(minutes=self.interval_mins)

        # while

    def handle(self, *args, **options):

        if options['verbose']:
            self.verbose += 1

        if options['interval']:
            self.interval_mins = int(options['interval'][0])
        self.stdout.write('[INFO] Progress interval is %s minutes' % self.interval_mins)

        partial1 = {
            10: 0,
            11: 0,
            12: 1948650,
            13: 1712192,
            14: 2663384,
            15: 1755894,
            18: 2740263,
            19: 706730,
            20: 234350,
            21: 2141126,
            22: 2037716,
            23: 2527875,
            26: 909813,
            27: 202379,
            28: 1278745,
            29: 405930,
            30: 1011715,
            31: 3534169,
            34: 813700,
            35: 144432,
            36: 273976,
            37: 1069726,
            38: 1263838,
            39: 3112472,
            42: 1777621,
            43: 323294,
            44: 308974,
            45: 2113579,
            46: 3736845,
            47: 3376081,
            50: 1453403,
            51: 2819370,
            52: 3709672,
            53: 2459420,
            54: 2480212,
            55: 745975}

        partial = {
            10: 3024145,
            11: 1044036,
            12: 1412996,
            13: 468924,
            14: 2182589,
            15: 3555703,
            18: 914030,
            19: 567095,
            20: 239697,
            21: 531427,
            22: 3706169,
            23: 3400664,
            26: 2283179,
            27: 181660,
            28: 654090,
            29: 659839,
            30: 951086,
            31: 1287433,
            34: 919848,
            35: 167843,
            36: 2136028,
            37: 625560,
            38: 1865427,
            39: 1939379,
            42: 2252958,
            43: 492230,
            44: 418518,
            45: 3012047,
            46: 1564358,
            47: 1205935,
            51: 1267452,
            52: 3254878,
            53: 2843051,
            54: 1357437,
            55: 3786691,
        }

        self.load_partial(partial)
        self.find_6x6()

# end of file
