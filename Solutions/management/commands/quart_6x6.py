# -*- coding: utf-8 -*-

#  Copyright (c) 2023 Ramon van der Winkel.
#  All rights reserved.
#  Licensed under BSD-3-Clause-Clear. See LICENSE file for details.

from django.core.management.base import BaseCommand
from Pieces2x2.models import TwoSides, Piece2x2
from Solutions.models import Solution4x4, Solution6x6, Quart6, P_CORNER, P_BORDER, P_HINTS, ALL_HINT_NRS
import time


"""
    Experimental solver that starts with corner elbows.
"""


class Command(BaseCommand):

    help = "6x6 generator using Quart6"

    NR_IGNORE = (1, 2, 3, 4, 5, 6, 7, 8,
                 9, 16, 17, 24, 25, 32, 33, 40, 41, 48, 49, 56,
                 57, 58, 59, 60, 61, 62, 63, 64)

    NRS_4x4_C1 = (27, 19, 20)
    NRS_4x4_C2 = (21, 22, 30)
    NRS_4x4_C3 = (38, 46, 45)
    NRS_4x4_C4 = (44, 43, 35)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.verbose = 0
        self.board = dict()  # [nr] = Piece2x2
        self.board_options = dict()  # [nr] = count of possible Piece2x2
        self.board_must_have = dict()  # [nr] = list(base nrs)
        self.board_criticality = dict()  # [nr] = number (lower is more critical)
        self.board_freedom = dict()  # [nr] = "statement"
        self.board_gap_count = 0
        self.board_unused_nrs = list()
        self.neighbours = dict()  # [nr] = (side 1, 2, 3, 4 neighbour nrs)
        self._count_freedom_cache = dict()
        self.board_solve_order = list()  # [nr, nr, ..]
        # self.all_unused_nrs = list()
        self.based_on = 0
        self.interval_mins = 15
        self.my_processor = int(time.time() - 946684800.0)     # seconds since Jan 1, 2000

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
        for nr in range(1, 64 + 1):
            self.neighbours[nr] = (nr - 8, nr + 1, nr + 8, nr - 1)

        for nr in self.NR_IGNORE:
            self.neighbours[nr] = (0, 0, 0, 0)

    def add_arguments(self, parser):
        parser.add_argument('--verbose', action='store_true')

    def _count_2x2(self, nr, unused_nrs):
        # get the sides
        s1, s2, s3, s4 = self._get_sides(nr)
        p1 = p2 = p3 = p4 = None
        x1 = x2 = x3 = x4 = None
        # has_hint = False

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
                # has_hint = True
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

        must_have_nrs = list()

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
                #     self.stdout.write('[%s] count=%s, freedom=%s, must_have_nrs=%s' % (
                #                        nr, count, freedom, must_have_nrs))
                #     self.stdout.write('     p1: %s' % avail_nr1)
                #     self.stdout.write('     p2: %s' % avail_nr2)
                #     self.stdout.write('     p3: %s' % avail_nr3)
                #     self.stdout.write('     p4: %s' % avail_nr4)
            else:
                freedom = '0'

            self._count_freedom_cache[tup] = (count, freedom)

        return count, freedom, must_have_nrs

    def _count_all(self, work_nr):
        self._count_freedom_cache = dict()

        # start with the neighbours so we can quickly find a dead-end
        nrs = list(self.neighbours[work_nr])
        for nr in range(1, 64+1):
            if nr not in self.NR_IGNORE:
                if nr not in nrs:           # avoid dupes
                    nrs.append(nr)
        # for

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

                if count == 0:
                    # found a dead end
                    # self.stdout.write(' [%s] no options for %s' % (work_nr, nr))
                    return True
        # for
        return False

    def _count_important(self, work_nr, important=None):
        self._count_freedom_cache = dict()

        if not important:
            important = [
                10, 11, 12, 13, 14, 15,
                18, 23, 26, 31, 34, 39, 42, 47,
                50, 51, 52, 53, 54, 55]

        # start with the neighbours so we can quickly find a dead-end
        nrs = list(self.neighbours[work_nr])
        nrs.extend(important)
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

                if count == 0:
                    # found a dead end
                    self.stdout.write(' [%s] no options for %s' % (work_nr, nr))
                    return True
        # for
        return False

    def _document_gaps(self, sol):
        for nr in range(1, 64+1):
            if nr not in self.NR_IGNORE:
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
            base_nrs.sort()
            self.stdout.write('[ERROR] Solution has %s instead of %s base nrs: %s' % (l1, l2, repr(base_nrs)))

        # self.stdout.write('[INFO] Saving board with gap count %s' % self.board_gap_count)
        # self.stdout.write('       Used base nrs: %s' % repr(base_nrs))

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

        self.stdout.write('[INFO] Saved board %s with gap count %s' % (sol.pk, self.board_gap_count))

    def _board_free_nr(self, nr):
        p = self.board[nr]
        if p:
            if self.verbose:
                self.stdout.write('-[%s] = %s' % (nr, p.nr))
            self.board[nr] = None
            free_nrs = [nr for nr in (p.nr1, p.nr2, p.nr3, p.nr4) if nr not in ALL_HINT_NRS]
            self.board_unused_nrs.extend(free_nrs)
            self.board_gap_count += 1
            self.board_solve_order.pop(-1)

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
        self.board_solve_order.append(nr)

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

    def _iter_for_nr(self, nr):

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

        # self.stdout.write('[%s] s=%s,%s,%s,%s x=%s,%s,%s,%s p=%s,%s,%s,%s' % (
        #                       nr, s1, s2, s3, s4, x1, x2, x3, x4, p1, p2, p3, p4))

        qset = Piece2x2.objects.order_by('nr')

        reserved_nrs = list()
        for chk_nr in range(1, 64+1):
            if chk_nr != nr:
                reserved_nrs.extend(self.board_must_have[chk_nr])
        # for
        # self.stdout.write('[%s] reserved_nrs=%s' % (nr, reserved_nrs))

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

        # self.stdout.write(qset.explain())

        todo = qset.count()
        for p in qset:
            # self.stdout.write('%s[%s] %s left' % (" " * len(self.board_solve_order), nr, todo))
            yield p
            todo -= 1

    def _try_fill_nr(self, nr):
        for p in self._iter_for_nr(nr):
            self._board_fill_nr(nr, p)
            # is_dead_end = self._count_all(nr)
            is_dead_end = self._count_important(nr)
            if not is_dead_end:
                return True     # success
            self._board_free_nr(nr)
        # for
        return False            # failure

    def load_board_4x4(self, sol):
        for nr in range(1, 64+1):
            self.board[nr] = None
            self.board_criticality[nr] = 999
        # for

        # start at 65 to skip all outer border pieces?
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
        # self.all_unused_nrs = self.board_unused_nrs[:]      # copy
        self._count_freedom_cache = dict()
        self.board_solve_order = list()     # [nr, nr, ..]
        self.based_on = sol.pk

        # lst = self.board_unused_nrs[:]
        # lst.sort()
        # self.stdout.write('[DEBUG] Unused base nrs (excl. hints): %s' % ", ".join([str(nr) for nr in lst]))

        self._count_all(1)

    def _fill_quart_gaps_52_53(self):
        self._count_all(1)
        self._save_board6x6()

        for p52 in self._iter_for_nr(52):
            self._board_fill_nr(52, p52)

            for p53 in self._iter_for_nr(53):
                self._board_fill_nr(53, p53)

                # FOUND a 6x6 solution!
                self.stdout.write('[INFO] PARTY TIME!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
                self._count_all(1)
                self._save_board6x6()

                self._board_free_nr(53)
            # for

            self._board_free_nr(52)
        # for

    def _fill_quart_gaps_31_39(self):
        self._count_all(1)
        self._save_board6x6()

        for p31 in self._iter_for_nr(31):
            self._board_fill_nr(31, p31)

            for p39 in self._iter_for_nr(39):
                self._board_fill_nr(39, p39)

                # verify a solution is possible
                count52, _, _ = self._count_2x2(52, self.board_unused_nrs)
                count53, _, _ = self._count_2x2(53, self.board_unused_nrs)

                if count52 > 0 and count53 > 0:
                    self._fill_quart_gaps_52_53()

                self._board_free_nr(39)
            # for

            self._board_free_nr(31)
        # for

    def _fill_quart_gaps_26_34(self):
        self._count_all(1)
        self._save_board6x6()

        for p26 in self._iter_for_nr(26):
            self._board_fill_nr(26, p26)

            for p34 in self._iter_for_nr(34):
                self._board_fill_nr(34, p34)

                # verify a solution is possible
                count31, _, _ = self._count_2x2(31, self.board_unused_nrs)
                count39, _, _ = self._count_2x2(39, self.board_unused_nrs)
                count52, _, _ = self._count_2x2(52, self.board_unused_nrs)
                count53, _, _ = self._count_2x2(53, self.board_unused_nrs)

                if count31 > 0 and count39 > 0 and count52 > 0 and count53 > 0:
                    self._fill_quart_gaps_31_39()

                self._board_free_nr(34)
            # for

            self._board_free_nr(26)
        # for

    def _fill_quart_gaps_12_13(self):
        # self._count_all(1)
        # self._save_board6x6()

        for p12 in self._iter_for_nr(12):
            self._board_fill_nr(12, p12)

            for p13 in self._iter_for_nr(13):
                self._board_fill_nr(13, p13)

                # verify a solution is possible
                count26, _, _ = self._count_2x2(26, self.board_unused_nrs)
                count31, _, _ = self._count_2x2(31, self.board_unused_nrs)
                count34, _, _ = self._count_2x2(34, self.board_unused_nrs)
                count39, _, _ = self._count_2x2(39, self.board_unused_nrs)
                count52, _, _ = self._count_2x2(52, self.board_unused_nrs)
                count53, _, _ = self._count_2x2(53, self.board_unused_nrs)

                if count26 > 0 and count31 > 0 and count34 > 0 and count39 > 0 and count52 > 0 and count53 > 0:
                    self._fill_quart_gaps_26_34()

                self._board_free_nr(13)
                # for

            self._board_free_nr(12)
        # for

    def find_6x6(self):
        self.stdout.write('[INFO] Start solving')

        for nr in range(1, 64+1):
            self.board_must_have[nr] = list()
        # for

        self._save_board6x6()

        # iterate over the first Half6
        unused_nrs0 = [nr for nr in self.board_unused_nrs if nr > 60]       # skip borders
        unused_nrs0.append(208)
        unused_nrs = set(unused_nrs0)
        for quart1 in (Quart6
                       .objects
                       .filter(processor=self.my_processor,
                               based_on_4x4=self.based_on,
                               type=10)
                       .filter(nr1__in=unused_nrs, nr2__in=unused_nrs, nr3__in=unused_nrs, nr4__in=unused_nrs,
                               nr5__in=unused_nrs, nr6__in=unused_nrs, nr7__in=unused_nrs, nr8__in=unused_nrs,
                               nr9__in=unused_nrs, nr10__in=unused_nrs, nr11__in=unused_nrs, nr12__in=unused_nrs)):

            # print('quart1=%s' % quart1.pk)

            # place the pieces
            self._board_fill_nr(18, Piece2x2.objects.get(nr=quart1.p1))
            self._board_fill_nr(10, Piece2x2.objects.get(nr=quart1.c1))
            self._board_fill_nr(11, Piece2x2.objects.get(nr=quart1.p2))

            # verify a solution is possible
            count12, _, _ = self._count_2x2(12, self.board_unused_nrs)
            count26, _, _ = self._count_2x2(26, self.board_unused_nrs)
            if count12 > 0 and count26 > 0:

                # iterate over the second Quart6
                used_nrs1 = (quart1.nr1, quart1.nr2, quart1.nr3, quart1.nr4,
                             quart1.nr5, quart1.nr6, quart1.nr7, quart1.nr8,
                             quart1.nr9, quart1.nr10, quart1.nr11, quart1.nr12)

                unused_nrs1 = [nr for nr in unused_nrs0 if nr not in used_nrs1]
                unused_nrs1.append(255)
                unused_nrs = set(unused_nrs1)

                for quart2 in (Quart6
                               .objects
                               .filter(processor=self.my_processor,
                                       based_on_4x4=self.based_on,
                                       type=15)
                               .filter(nr1__in=unused_nrs, nr2__in=unused_nrs, nr3__in=unused_nrs, nr4__in=unused_nrs,
                                       nr5__in=unused_nrs, nr6__in=unused_nrs, nr7__in=unused_nrs, nr8__in=unused_nrs,
                                       nr9__in=unused_nrs, nr10__in=unused_nrs, nr11__in=unused_nrs, nr12__in=unused_nrs)):

                    # print('quart2=%s' % quart2.pk)

                    # place the pieces
                    self._board_fill_nr(14, Piece2x2.objects.get(nr=quart2.p1))
                    self._board_fill_nr(15, Piece2x2.objects.get(nr=quart2.c1))
                    self._board_fill_nr(23, Piece2x2.objects.get(nr=quart2.p2))

                    count12, _, _ = self._count_2x2(12, self.board_unused_nrs)
                    count13, _, _ = self._count_2x2(13, self.board_unused_nrs)
                    count26, _, _ = self._count_2x2(26, self.board_unused_nrs)
                    count31, _, _ = self._count_2x2(31, self.board_unused_nrs)
                    if count12 > 0 and count13 > 0 and count26 > 0 and count31 > 0:

                        # iterate over the third Quart6
                        used_nrs2 = (quart2.nr1, quart2.nr2, quart2.nr3, quart2.nr4,
                                     quart2.nr5, quart2.nr6, quart2.nr7, quart2.nr8,
                                     quart2.nr9, quart2.nr10, quart2.nr11, quart2.nr12)

                        unused_nrs2 = [nr for nr in unused_nrs1 if nr not in used_nrs2]
                        unused_nrs2.append(181)
                        unused_nrs = set(unused_nrs2)

                        for quart3 in (Quart6
                                       .objects
                                       .filter(processor=self.my_processor,
                                               based_on_4x4=self.based_on,
                                               type=50)
                                       .filter(nr1__in=unused_nrs, nr2__in=unused_nrs, nr3__in=unused_nrs, nr4__in=unused_nrs,
                                               nr5__in=unused_nrs, nr6__in=unused_nrs, nr7__in=unused_nrs, nr8__in=unused_nrs,
                                               nr9__in=unused_nrs, nr10__in=unused_nrs, nr11__in=unused_nrs, nr12__in=unused_nrs)):

                            # print('quart3=%s' % quart3.pk)

                            # place the pieces
                            self._board_fill_nr(51, Piece2x2.objects.get(nr=quart3.p1))
                            self._board_fill_nr(50, Piece2x2.objects.get(nr=quart3.c1))
                            self._board_fill_nr(42, Piece2x2.objects.get(nr=quart3.p2))

                            count12, _, _ = self._count_2x2(12, self.board_unused_nrs)
                            count13, _, _ = self._count_2x2(13, self.board_unused_nrs)
                            count26, _, _ = self._count_2x2(26, self.board_unused_nrs)
                            count31, _, _ = self._count_2x2(31, self.board_unused_nrs)
                            count34, _, _ = self._count_2x2(34, self.board_unused_nrs)
                            count52, _, _ = self._count_2x2(52, self.board_unused_nrs)
                            if count12 > 0 and count13 > 0 and count26 > 0 and count31 > 0 and count34 > 0 and count52 > 0:

                                # iterate over the fourth Quart6
                                used_nrs3 = (quart3.nr1, quart3.nr2, quart3.nr3, quart3.nr4,
                                             quart3.nr5, quart3.nr6, quart3.nr7, quart3.nr8,
                                             quart3.nr9, quart3.nr10, quart3.nr11, quart3.nr12)

                                unused_nrs3 = [nr for nr in unused_nrs2 if nr not in used_nrs3]
                                unused_nrs3.append(249)
                                unused_nrs = set(unused_nrs3)

                                for quart4 in (Quart6
                                               .objects
                                               .filter(processor=self.my_processor,
                                                       based_on_4x4=self.based_on,
                                                       type=55)
                                               .filter(nr1__in=unused_nrs, nr2__in=unused_nrs, nr3__in=unused_nrs, nr4__in=unused_nrs,
                                                       nr5__in=unused_nrs, nr6__in=unused_nrs, nr7__in=unused_nrs, nr8__in=unused_nrs,
                                                       nr9__in=unused_nrs, nr10__in=unused_nrs, nr11__in=unused_nrs, nr12__in=unused_nrs)):

                                    # place the pieces
                                    self._board_fill_nr(47, Piece2x2.objects.get(nr=quart4.p1))
                                    self._board_fill_nr(55, Piece2x2.objects.get(nr=quart4.c1))
                                    self._board_fill_nr(54, Piece2x2.objects.get(nr=quart4.p2))

                                    # verify a solution is possible
                                    count12, _, _ = self._count_2x2(12, self.board_unused_nrs)
                                    count13, _, _ = self._count_2x2(13, self.board_unused_nrs)
                                    count26, _, _ = self._count_2x2(26, self.board_unused_nrs)
                                    count31, _, _ = self._count_2x2(31, self.board_unused_nrs)
                                    count34, _, _ = self._count_2x2(34, self.board_unused_nrs)
                                    count39, _, _ = self._count_2x2(39, self.board_unused_nrs)
                                    count52, _, _ = self._count_2x2(52, self.board_unused_nrs)
                                    count53, _, _ = self._count_2x2(53, self.board_unused_nrs)

                                    if count12 > 0 and count13 > 0 and count26 > 0 and count31 > 0 and count34 > 0 and count39 > 0 and count52 > 0 and count53 > 0:
                                        self._fill_quart_gaps_12_13()

                                    self._board_free_nr(54)
                                    self._board_free_nr(55)
                                    self._board_free_nr(47)
                                # for

                            self._board_free_nr(42)
                            self._board_free_nr(50)
                            self._board_free_nr(51)
                        # for

                    self._board_free_nr(23)
                    self._board_free_nr(15)
                    self._board_free_nr(14)
                # for

            self._board_free_nr(11)
            self._board_free_nr(10)
            self._board_free_nr(18)
        # for

    def _generate_quart6(self, p1_nr, c_nr, p2_nr):
        count = 0
        bulk = list()
        for c1 in self._iter_for_nr(c_nr):
            self._board_fill_nr(c_nr, c1)

            for p1 in self._iter_for_nr(p1_nr):
                self._board_fill_nr(p1_nr, p1)

                for p2 in self._iter_for_nr(p2_nr):
                    self._board_fill_nr(p2_nr, p2)

                    quart = Quart6(
                                processor=self.my_processor,
                                based_on_4x4=self.based_on,
                                type=c_nr,
                                p1=p1.pk,
                                c1=c1.pk,
                                p2=p2.pk,
                                nr1=p1.nr1,
                                nr2=p1.nr2,
                                nr3=p1.nr3,
                                nr4=p1.nr4,
                                nr5=c1.nr1,
                                nr6=c1.nr2,
                                nr7=c1.nr3,
                                nr8=c1.nr4,
                                nr9=p2.nr1,
                                nr10=p2.nr2,
                                nr11=p2.nr3,
                                nr12=p2.nr4)

                    bulk.append(quart)
                    if len(bulk) >= 500:
                        count += len(bulk)
                        print('Quart6 type %s: %s' % (c_nr, count))
                        Quart6.objects.bulk_create(bulk)
                        bulk = list()

                    self._board_free_nr(p2_nr)
                # for

                self._board_free_nr(p1_nr)
            # for

            self._board_free_nr(c_nr)
        # for

        if len(bulk) > 0:
            count += len(bulk)
            print('Quart6 type %s: %s' % (c_nr, count))
            Quart6.objects.bulk_create(bulk)

    def _generate_all_quart6(self):
        self._generate_quart6(18, 10, 11)
        self._generate_quart6(14, 15, 23)
        self._generate_quart6(51, 50, 42)
        self._generate_quart6(47, 55, 54)

    def handle(self, *args, **options):

        if options['verbose']:
            self.verbose += 1

        min_4x4_pk = 1
        self.stdout.write('[INFO] my_processor is %s' % self.my_processor)

        do_quit = False
        while not do_quit:
            sol = (Solution4x4
                   .objects
                   .filter(is_processed=False,
                           processor=0,
                           pk__gte=min_4x4_pk)
                   .order_by('pk')      # lowest first
                   .first())

            if sol:
                self.stdout.write('[INFO] Loading Solution4x4 nr %s' % sol.pk)
                sol.processor = self.my_processor
                sol.save(update_fields=['processor'])

                self.load_board_4x4(sol)
                for nr in range(1, 64 + 1):
                    self.board_must_have[nr] = list()
                # for

                try:
                    self._generate_all_quart6()
                    self.find_6x6()
                except KeyboardInterrupt:
                    # warning for closed stdout!
                    sol.processor = 0
                    sol.save(update_fields=['processor'])
                else:
                    sol.is_processed = True
                    sol.save(update_fields=['is_processed'])

                # clean up
                Quart6.objects.filter(processor=self.my_processor).delete()
            else:
                self.stdout.write('[INFO] Waiting for new 4x4 (press Ctrl+C to abort)')
                time.sleep(60)
        # while

        # warning for closed stdout..
        self.stdout.write('[WARNING] Interrupted')

# end of file
