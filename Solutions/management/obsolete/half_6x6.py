# -*- coding: utf-8 -*-

#  Copyright (c) 2023 Ramon van der Winkel.
#  All rights reserved.
#  Licensed under BSD-3-Clause-Clear. See LICENSE file for details.

from django.core.management.base import BaseCommand
from Pieces2x2.models import TwoSides, Piece2x2, Block2x8
from Solutions.models import Solution4x4, Solution6x6, Half6, P_CORNER, P_BORDER, P_HINTS, ALL_HINT_NRS
import time


"""
    Experimental solver that uses 2x4 blocks.
"""


class Command(BaseCommand):

    help = "Half6 generator"

    NR_IGNORE = (1, 2, 3, 4, 5, 6, 7, 8,
                 9, 16, 17, 24, 25, 32, 33, 40, 41, 48, 49, 56,
                 57, 58, 59, 60, 61, 62, 63, 64)

    NRS_4X4_SIDE1 = (19, 20, 21, 22)
    NRS_4X4_SIDE2 = (22, 30, 38, 46)
    NRS_4X4_SIDE3 = (46, 45, 44, 43)
    NRS_4X4_SIDE4 = (43, 35, 27, 19)

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

        # self.stdout.write('[%s] s=%s,%s,%s,%s x=%s,%s,%s,%s p=%s,%s,%s,%s' % (
        #                       nr, s1, s2, s3, s4, x1, x2, x3, x4, p1, p2, p3, p4))

        qset = Piece2x2.objects.filter(nr__gt=greater_than).order_by('nr')

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

    def _try_fill_nr(self, nr, greater_than):
        for p in self._iter_for_nr(nr, greater_than):
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

    def _count_6x6_block4(self):
        big_side = [self.side_nr2reverse[self.board[nr].side4] for nr in self.NRS_4X4_SIDE4]
        unused_nrs0 = self.board_unused_nrs[:]
        unused_nrs = set(unused_nrs0)
        count = (Block2x8
                 .objects
                 .filter(processor=self.my_processor,
                         type=4,
                         b1=big_side[0], b2=big_side[1], b3=big_side[2], b4=big_side[3])
                 .filter(nr1__in=unused_nrs, nr2__in=unused_nrs, nr3__in=unused_nrs, nr4__in=unused_nrs,
                         nr5__in=unused_nrs, nr6__in=unused_nrs, nr7__in=unused_nrs, nr8__in=unused_nrs,
                         nr9__in=unused_nrs, nr10__in=unused_nrs, nr11__in=unused_nrs, nr12__in=unused_nrs,
                         nr13__in=unused_nrs, nr14__in=unused_nrs, nr15__in=unused_nrs, nr16__in=unused_nrs)
                 .count())
        return count

    def _find_6x6_block4(self, sides_todo, blocks_todo):
        # iterate through the Block2x8 for side4
        big_side = [self.side_nr2reverse[self.board[nr].side4] for nr in self.NRS_4X4_SIDE4]
        unused_nrs0 = self.board_unused_nrs[:]
        unused_nrs = set(unused_nrs0)
        for block2 in (Block2x8
                       .objects
                       .filter(processor=self.my_processor,
                               type=4,
                               b1=big_side[0], b2=big_side[1], b3=big_side[2], b4=big_side[3])
                       .filter(nr1__in=unused_nrs, nr2__in=unused_nrs, nr3__in=unused_nrs, nr4__in=unused_nrs,
                               nr5__in=unused_nrs, nr6__in=unused_nrs, nr7__in=unused_nrs, nr8__in=unused_nrs,
                               nr9__in=unused_nrs, nr10__in=unused_nrs, nr11__in=unused_nrs, nr12__in=unused_nrs,
                               nr13__in=unused_nrs, nr14__in=unused_nrs, nr15__in=unused_nrs, nr16__in=unused_nrs)):

            # place the 4 pieces
            self._board_fill_nr(42, Piece2x2.objects.get(nr=block2.p1))
            self._board_fill_nr(34, Piece2x2.objects.get(nr=block2.p2))
            self._board_fill_nr(26, Piece2x2.objects.get(nr=block2.p3))
            self._board_fill_nr(18, Piece2x2.objects.get(nr=block2.p4))

            is_dead_end = self._count_important(42)
            if not is_dead_end:
                if blocks_todo > 0:
                    self.stdout.write('block1: %s left' % blocks_todo)
                self._find_6x6_next(sides_todo)

            blocks_todo -= 1

            self._board_free_nr(18)
            self._board_free_nr(26)
            self._board_free_nr(34)
            self._board_free_nr(42)
        # for

    def _count_6x6_block3(self):
        big_side = [self.side_nr2reverse[self.board[nr].side3] for nr in self.NRS_4X4_SIDE3]
        unused_nrs0 = self.board_unused_nrs[:]
        unused_nrs = set(unused_nrs0)
        count = (Block2x8
                 .objects
                 .filter(processor=self.my_processor,
                         type=3,
                         b1=big_side[0], b2=big_side[1], b3=big_side[2], b4=big_side[3])
                 .filter(nr1__in=unused_nrs, nr2__in=unused_nrs, nr3__in=unused_nrs, nr4__in=unused_nrs,
                         nr5__in=unused_nrs, nr6__in=unused_nrs, nr7__in=unused_nrs, nr8__in=unused_nrs,
                         nr9__in=unused_nrs, nr10__in=unused_nrs, nr11__in=unused_nrs, nr12__in=unused_nrs,
                         nr13__in=unused_nrs, nr14__in=unused_nrs, nr15__in=unused_nrs, nr16__in=unused_nrs)
                 .count())
        return count

    def _find_6x6_block3(self, sides_todo, blocks_todo):
        # iterate through the Block2x8 for side3
        big_side = [self.side_nr2reverse[self.board[nr].side3] for nr in self.NRS_4X4_SIDE3]
        unused_nrs0 = self.board_unused_nrs[:]
        unused_nrs = set(unused_nrs0)
        for block2 in (Block2x8
                       .objects
                       .filter(processor=self.my_processor,
                               type=3,
                               b1=big_side[0], b2=big_side[1], b3=big_side[2], b4=big_side[3])
                       .filter(nr1__in=unused_nrs, nr2__in=unused_nrs, nr3__in=unused_nrs, nr4__in=unused_nrs,
                               nr5__in=unused_nrs, nr6__in=unused_nrs, nr7__in=unused_nrs, nr8__in=unused_nrs,
                               nr9__in=unused_nrs, nr10__in=unused_nrs, nr11__in=unused_nrs, nr12__in=unused_nrs,
                               nr13__in=unused_nrs, nr14__in=unused_nrs, nr15__in=unused_nrs, nr16__in=unused_nrs)):

            # place the 4 pieces
            self._board_fill_nr(54, Piece2x2.objects.get(nr=block2.p1))
            self._board_fill_nr(53, Piece2x2.objects.get(nr=block2.p2))
            self._board_fill_nr(52, Piece2x2.objects.get(nr=block2.p3))
            self._board_fill_nr(51, Piece2x2.objects.get(nr=block2.p4))

            is_dead_end = self._count_important(54)
            if not is_dead_end:
                if blocks_todo > 0:
                    self.stdout.write('block1: %s left' % blocks_todo)
                self._find_6x6_next(sides_todo)

            blocks_todo -= 1

            self._board_free_nr(51)
            self._board_free_nr(52)
            self._board_free_nr(53)
            self._board_free_nr(54)
        # for

    def _count_6x6_block2(self):
        big_side = [self.side_nr2reverse[self.board[nr].side2] for nr in self.NRS_4X4_SIDE2]
        unused_nrs0 = self.board_unused_nrs[:]
        unused_nrs = set(unused_nrs0)
        count = (Block2x8
                 .objects
                 .filter(processor=self.my_processor,
                         type=2,
                         b1=big_side[0], b2=big_side[1], b3=big_side[2], b4=big_side[3])
                 .filter(nr1__in=unused_nrs, nr2__in=unused_nrs, nr3__in=unused_nrs, nr4__in=unused_nrs,
                         nr5__in=unused_nrs, nr6__in=unused_nrs, nr7__in=unused_nrs, nr8__in=unused_nrs,
                         nr9__in=unused_nrs, nr10__in=unused_nrs, nr11__in=unused_nrs, nr12__in=unused_nrs,
                         nr13__in=unused_nrs, nr14__in=unused_nrs, nr15__in=unused_nrs, nr16__in=unused_nrs)
                 .count())
        return count

    def _find_6x6_block2(self, sides_todo, blocks_todo):
        # iterate through the Block2x8 for side2
        big_side = [self.side_nr2reverse[self.board[nr].side2] for nr in self.NRS_4X4_SIDE2]
        unused_nrs0 = self.board_unused_nrs[:]
        unused_nrs = set(unused_nrs0)
        for block2 in (Block2x8
                       .objects
                       .filter(processor=self.my_processor,
                               type=2,
                               b1=big_side[0], b2=big_side[1], b3=big_side[2], b4=big_side[3])
                       .filter(nr1__in=unused_nrs, nr2__in=unused_nrs, nr3__in=unused_nrs, nr4__in=unused_nrs,
                               nr5__in=unused_nrs, nr6__in=unused_nrs, nr7__in=unused_nrs, nr8__in=unused_nrs,
                               nr9__in=unused_nrs, nr10__in=unused_nrs, nr11__in=unused_nrs, nr12__in=unused_nrs,
                               nr13__in=unused_nrs, nr14__in=unused_nrs, nr15__in=unused_nrs, nr16__in=unused_nrs)):

            # place the 4 pieces
            self._board_fill_nr(23, Piece2x2.objects.get(nr=block2.p1))
            self._board_fill_nr(31, Piece2x2.objects.get(nr=block2.p2))
            self._board_fill_nr(39, Piece2x2.objects.get(nr=block2.p3))
            self._board_fill_nr(47, Piece2x2.objects.get(nr=block2.p4))

            is_dead_end = self._count_important(23)
            if not is_dead_end:
                if blocks_todo > 0:
                    self.stdout.write('block2: %s left' % blocks_todo)
                self._find_6x6_next(sides_todo)

            blocks_todo -= 1

            self._board_free_nr(47)
            self._board_free_nr(39)
            self._board_free_nr(31)
            self._board_free_nr(23)
        # for

    def _count_6x6_block1(self):
        big_side = [self.side_nr2reverse[self.board[nr].side1] for nr in self.NRS_4X4_SIDE1]
        unused_nrs0 = self.board_unused_nrs[:]
        unused_nrs = set(unused_nrs0)
        count = (Block2x8
                 .objects
                 .filter(processor=self.my_processor,
                         type=1,
                         b1=big_side[0], b2=big_side[1], b3=big_side[2], b4=big_side[3])
                 .filter(nr1__in=unused_nrs, nr2__in=unused_nrs, nr3__in=unused_nrs, nr4__in=unused_nrs,
                         nr5__in=unused_nrs, nr6__in=unused_nrs, nr7__in=unused_nrs, nr8__in=unused_nrs,
                         nr9__in=unused_nrs, nr10__in=unused_nrs, nr11__in=unused_nrs, nr12__in=unused_nrs,
                         nr13__in=unused_nrs, nr14__in=unused_nrs, nr15__in=unused_nrs, nr16__in=unused_nrs)
                 .count())
        return count

    def _find_6x6_block1(self, sides_todo, blocks_todo):
        # iterate through the Block2x8 for each side, then add corners
        big_side = [self.side_nr2reverse[self.board[nr].side1] for nr in self.NRS_4X4_SIDE1]
        unused_nrs0 = self.board_unused_nrs[:]
        unused_nrs = set(unused_nrs0)
        for block1 in (Block2x8
                       .objects
                       .filter(processor=self.my_processor,
                               type=1,
                               b1=big_side[0], b2=big_side[1], b3=big_side[2], b4=big_side[3])
                       .filter(nr1__in=unused_nrs, nr2__in=unused_nrs, nr3__in=unused_nrs, nr4__in=unused_nrs,
                               nr5__in=unused_nrs, nr6__in=unused_nrs, nr7__in=unused_nrs, nr8__in=unused_nrs,
                               nr9__in=unused_nrs, nr10__in=unused_nrs, nr11__in=unused_nrs, nr12__in=unused_nrs,
                               nr13__in=unused_nrs, nr14__in=unused_nrs, nr15__in=unused_nrs, nr16__in=unused_nrs)):

            # place the 4 pieces
            self._board_fill_nr(11, Piece2x2.objects.get(nr=block1.p1))
            self._board_fill_nr(12, Piece2x2.objects.get(nr=block1.p2))
            self._board_fill_nr(13, Piece2x2.objects.get(nr=block1.p3))
            self._board_fill_nr(14, Piece2x2.objects.get(nr=block1.p4))

            is_dead_end = self._count_important(11)
            if not is_dead_end:
                if blocks_todo > 0:
                    self.stdout.write('block1: %s left' % blocks_todo)
                self._find_6x6_next(sides_todo)

            blocks_todo -= 1

            self._board_free_nr(14)
            self._board_free_nr(13)
            self._board_free_nr(12)
            self._board_free_nr(11)
        # for

    def _count_block_n(self, n):
        if n == 1:
            count = self._count_6x6_block1()
        elif n == 2:
            count = self._count_6x6_block2()
        elif n == 3:
            count = self._count_6x6_block3()
        else:
            count = self._count_6x6_block4()
        return count

    def _find_6x6_corners(self):

        for p1 in self._iter_for_nr(10, 0):
            self._board_fill_nr(10, p1)
            is_dead_end = self._count_important(10)
            if not is_dead_end:
                self._save_board6x6()

                for p2 in self._iter_for_nr(15, 0):
                    self._board_fill_nr(15, p2)
                    is_dead_end = self._count_important(15)
                    if not is_dead_end:
                        self._save_board6x6()

                        for p3 in self._iter_for_nr(50, 0):
                            self._board_fill_nr(50, p3)
                            is_dead_end = self._count_important(50)
                            if not is_dead_end:
                                self._save_board6x6()

                                for p4 in self._iter_for_nr(55, 0):
                                    self._board_fill_nr(55, p4)
                                    is_dead_end = self._count_important(55)
                                    if not is_dead_end:
                                        self._save_board6x6()

                                    self._board_free_nr(55)
                                # for

                            self._board_free_nr(50)
                        # for

                    self._board_free_nr(15)
                # for

            self._board_free_nr(10)
        # for

        # while True:
        #     nr = self.get_next_nr()     # can return 0 to trigger backtracking
        #
        #     greater_than = 0
        #     placed_piece = False
        #     while not placed_piece:
        #         if nr > 0 and self._try_fill_nr(nr, greater_than):
        #             # success
        #             placed_piece = True
        #             if self.board_gap_count < best:
        #                 self._save_board6x6()
        #                 next_time = datetime.datetime.now() + datetime.timedelta(minutes=self.interval_mins)
        #                 best = self.board_gap_count
        #         else:
        #             # backtrack and continue with next option in previous spot
        #             if len(self.board_solve_order) == 0:
        #                 self.stdout.write('[INFO] Reached the end')
        #                 return
        #
        #             p = self.board[nr]
        #             if not p:
        #                 self.stderr.write('[DEBUG] No p2x2 at nr %s !!' % nr)
        #                 return
        #             greater_than = p.nr
        #             # self.stdout.write('[INFO] Backtracked to nr %s with greater_than %s' % (nr, greater_than))
        #             self._board_free_nr(nr)
        #             self._count_important(nr)      # update the criticality stats
        #     # while
        #
        #     if len(self.board_solve_order) == 36:
        #         self._save_board6x6()
        #
        #     if datetime.datetime.now() > next_time:
        #         next_time = datetime.datetime.now() + datetime.timedelta(minutes=self.interval_mins)
        #         # self.stdout.write('[INFO] Progress milestone')
        #         # self._save_board6x6()
        #         best = 999      # allow a few progress reports
        # # while

    def _find_6x6_next(self, sides_todo):
        if len(sides_todo) == 0:
            self._save_board6x6()
            self._find_6x6_corners()
            return

        # progress
        if len(sides_todo) <= 1:
            self._save_board6x6()

        order = list()
        for s in sides_todo:
            tup = (self._count_block_n(s), s)
            order.append(tup)
        # for
        order.sort()        # smallest first
        count, s = order[0]

        if count == 0:
            # out of options on one side
            if len(sides_todo) == 4:
                print('[INFO] Out of options for side %s from %s' % (s, repr(order)))
            return

        print('[INFO] Selected side %s from %s' % (s, repr(order)))

        remaining_sides = [side for side in sides_todo if side != s]
        if len(remaining_sides) <= 2:
            count = 0

        if s == 1:
            self._find_6x6_block1(remaining_sides, count)
        elif s == 2:
            self._find_6x6_block2(remaining_sides, count)
        elif s == 3:
            self._find_6x6_block3(remaining_sides, count)
        elif s == 4:
            self._find_6x6_block4(remaining_sides, count)

    def find_6x6(self):
        self.stdout.write('[INFO] Start solving')

        for nr in range(1, 64+1):
            self.board_must_have[nr] = list()
        # for

        self._save_board6x6()

        # iterate over the first Half6
        unused_nrs0 = [nr for nr in self.board_unused_nrs if nr > 60]       # skip borders
        unused_nrs0.append(255)     # hint for [15]
        unused_nrs = set(unused_nrs0)
        for half1 in (Half6
                      .objects
                      .filter(processor=self.my_processor,
                              based_on_4x4=self.based_on,
                              type=12)
                      .filter(nr1__in=unused_nrs, nr2__in=unused_nrs, nr3__in=unused_nrs, nr4__in=unused_nrs,
                              nr5__in=unused_nrs, nr6__in=unused_nrs, nr7__in=unused_nrs, nr8__in=unused_nrs,
                              nr9__in=unused_nrs, nr10__in=unused_nrs, nr11__in=unused_nrs, nr12__in=unused_nrs,
                              nr13__in=unused_nrs, nr14__in=unused_nrs, nr15__in=unused_nrs, nr16__in=unused_nrs,
                              nr17__in=unused_nrs, nr18__in=unused_nrs, nr19__in=unused_nrs, nr20__in=unused_nrs,
                              nr21__in=unused_nrs, nr22__in=unused_nrs, nr23__in=unused_nrs, nr24__in=unused_nrs,
                              nr25__in=unused_nrs, nr26__in=unused_nrs, nr27__in=unused_nrs, nr28__in=unused_nrs,
                              nr29__in=unused_nrs, nr30__in=unused_nrs, nr31__in=unused_nrs, nr32__in=unused_nrs,
                              nr33__in=unused_nrs, nr34__in=unused_nrs, nr35__in=unused_nrs, nr36__in=unused_nrs)):

            # print('half1=%s' % half1.pk)

            # iterate over de second Half6
            used_nrs1 = (half1.nr1, half1.nr2, half1.nr3, half1.nr4, half1.nr5, half1.nr6, half1.nr7, half1.nr8,
                         half1.nr9, half1.nr10, half1.nr11, half1.nr12, half1.nr13, half1.nr14, half1.nr15, half1.nr16,
                         half1.nr17, half1.nr18, half1.nr19, half1.nr20, half1.nr21, half1.nr22, half1.nr23,
                         half1.nr24, half1.nr25, half1.nr26, half1.nr27, half1.nr28, half1.nr29, half1.nr30,
                         half1.nr31, half1.nr32, half1.nr33, half1.nr34, half1.nr35, half1.nr36)

            unused_nrs1 = [nr for nr in unused_nrs0 if nr not in used_nrs1]
            unused_nrs1.append(181)     # hint for [50]
            unused_nrs = set(unused_nrs1)

            for half2 in (Half6
                          .objects
                          .filter(processor=self.my_processor,
                                  based_on_4x4=self.based_on,
                                  type=34)
                          .filter(nr1__in=unused_nrs, nr2__in=unused_nrs, nr3__in=unused_nrs, nr4__in=unused_nrs,
                                  nr5__in=unused_nrs, nr6__in=unused_nrs, nr7__in=unused_nrs, nr8__in=unused_nrs,
                                  nr9__in=unused_nrs, nr10__in=unused_nrs, nr11__in=unused_nrs, nr12__in=unused_nrs,
                                  nr13__in=unused_nrs, nr14__in=unused_nrs, nr15__in=unused_nrs, nr16__in=unused_nrs,
                                  nr17__in=unused_nrs, nr18__in=unused_nrs, nr19__in=unused_nrs, nr20__in=unused_nrs,
                                  nr21__in=unused_nrs, nr22__in=unused_nrs, nr23__in=unused_nrs, nr24__in=unused_nrs,
                                  nr25__in=unused_nrs, nr26__in=unused_nrs, nr27__in=unused_nrs, nr28__in=unused_nrs,
                                  nr29__in=unused_nrs, nr30__in=unused_nrs, nr31__in=unused_nrs, nr32__in=unused_nrs,
                                  nr33__in=unused_nrs, nr34__in=unused_nrs, nr35__in=unused_nrs, nr36__in=unused_nrs)):

                # print('half2=%s' % half2.pk)

                block1 = Block2x8.objects.get(pk=half1.p1)
                block2 = Block2x8.objects.get(pk=half1.p2)
                block3 = Block2x8.objects.get(pk=half2.p1)
                block4 = Block2x8.objects.get(pk=half2.p2)

                # place all pieces for half1 and half2
                self._board_fill_nr(11, Piece2x2.objects.get(nr=block1.p1))
                self._board_fill_nr(12, Piece2x2.objects.get(nr=block1.p2))
                self._board_fill_nr(13, Piece2x2.objects.get(nr=block1.p3))
                self._board_fill_nr(14, Piece2x2.objects.get(nr=block1.p4))
                self._board_fill_nr(15, Piece2x2.objects.get(nr=half1.c1))
                self._board_fill_nr(23, Piece2x2.objects.get(nr=block2.p1))
                self._board_fill_nr(31, Piece2x2.objects.get(nr=block2.p2))
                self._board_fill_nr(39, Piece2x2.objects.get(nr=block2.p3))
                self._board_fill_nr(47, Piece2x2.objects.get(nr=block2.p4))

                self._board_fill_nr(54, Piece2x2.objects.get(nr=block3.p1))
                self._board_fill_nr(53, Piece2x2.objects.get(nr=block3.p2))
                self._board_fill_nr(52, Piece2x2.objects.get(nr=block3.p3))
                self._board_fill_nr(51, Piece2x2.objects.get(nr=block3.p4))
                self._board_fill_nr(50, Piece2x2.objects.get(nr=half2.c1))
                self._board_fill_nr(42, Piece2x2.objects.get(nr=block4.p1))
                self._board_fill_nr(34, Piece2x2.objects.get(nr=block4.p2))
                self._board_fill_nr(26, Piece2x2.objects.get(nr=block4.p3))
                self._board_fill_nr(18, Piece2x2.objects.get(nr=block4.p4))

                # verify a solution is possible for positions 10 and 55
                count10, _, _ = self._count_2x2(10, self.board_unused_nrs)
                count55, _, _ = self._count_2x2(55, self.board_unused_nrs)

                if count10 > 0 and count55 > 0:
                    self._count_all(1)
                    self._save_board6x6()

                for nr in (11, 12, 13, 14, 15, 23, 31, 39, 47, 54, 53, 52, 51, 50, 42, 34, 26, 18):
                    self._board_free_nr(nr)
                # for
            # for
        # for

        # find the final corners

    def _generate_2x8_side1(self, avoid_nrs):
        # side4 must match a potential nr10 piece side2
        exp_side4 = [self.side_nr2reverse[side]
                     for side in Piece2x2.objects.filter(nr1=208).distinct('side2').values_list('side2', flat=True)]
        # side2 must match a potential nr15 piece side4
        exp_side2 = [self.side_nr2reverse[side]
                     for side in Piece2x2.objects.filter(nr2=255).distinct('side4').values_list('side4', flat=True)]
        big_side = [self.side_nr2reverse[self.board[nr].side1] for nr in self.NRS_4X4_SIDE1]
        always = {nr: 0 for nr in range(1, 256+1)}
        count = 0
        bulk = list()
        unused_nrs0 = [nr for nr in self.board_unused_nrs if nr > 60]       # skip borders
        unused_nrs0 = [nr for nr in unused_nrs0 if nr not in avoid_nrs]
        unused_nrs = set(unused_nrs0)
        # query all Piece2x2 needed
        p2x2s = list(Piece2x2.objects.filter(side3__in=big_side, nr1__in=unused_nrs, nr2__in=unused_nrs,
                                             nr3__in=unused_nrs, nr4__in=unused_nrs))

        for p1 in p2x2s:
            if p1.side3 == big_side[0] and p1.side4 in exp_side4:
                unused_nrs1 = [nr for nr in unused_nrs0 if nr not in (p1.nr1, p1.nr2, p1.nr3, p1.nr4)]
                unused_nrs = set(unused_nrs1)
                p2_exp_s4 = self.side_nr2reverse[p1.side2]

                for p2 in p2x2s:
                    if (p2.side3 == big_side[1] and p2.side4 == p2_exp_s4 and p2.nr1 in unused_nrs
                            and p2.nr2 in unused_nrs and p2.nr3 in unused_nrs and p2.nr4 in unused_nrs):

                        unused_nrs2 = [nr for nr in unused_nrs1 if nr not in (p2.nr1, p2.nr2, p2.nr3, p2.nr4)]
                        unused_nrs = set(unused_nrs2)
                        p3_exp_s4 = self.side_nr2reverse[p2.side2]

                        for p3 in p2x2s:
                            if (p3.side3 == big_side[2] and p3.side4 == p3_exp_s4 and p3.nr1 in unused_nrs
                                    and p3.nr2 in unused_nrs and p3.nr3 in unused_nrs and p3.nr4 in unused_nrs):

                                unused_nrs3 = [nr for nr in unused_nrs2 if nr not in (p3.nr1, p3.nr2, p3.nr3, p3.nr4)]
                                unused_nrs = set(unused_nrs3)
                                p4_exp_s4 = self.side_nr2reverse[p3.side2]

                                for p4 in p2x2s:
                                    if (p4.side3 == big_side[3] and p4.side4 == p4_exp_s4 and p4.side2 in exp_side2
                                            and p4.nr1 in unused_nrs and p4.nr2 in unused_nrs and p4.nr3 in unused_nrs
                                            and p4.nr4 in unused_nrs):

                                        block = Block2x8(
                                                        processor=self.my_processor,
                                                        type=1,
                                                        p1=p1.nr, p2=p2.nr, p3=p3.nr, p4=p4.nr,
                                                        b1=big_side[0], b2=big_side[1], b3=big_side[2], b4=big_side[3],
                                                        nr1=p1.nr1, nr2=p1.nr2, nr3=p1.nr3, nr4=p1.nr4,
                                                        nr5=p2.nr1, nr6=p2.nr2, nr7=p2.nr3, nr8=p2.nr4,
                                                        nr9=p3.nr1, nr10=p3.nr2, nr11=p3.nr3, nr12=p3.nr4,
                                                        nr13=p4.nr1, nr14=p4.nr2, nr15=p4.nr3, nr16=p4.nr4,
                                                        side1=0,
                                                        side2=p4.side2,
                                                        side3=0,            # big side
                                                        side4=p1.side4)
                                        bulk.append(block)

                                        chk = (p1.nr1, p1.nr2, p1.nr3, p1.nr4,
                                               p2.nr1, p2.nr2, p2.nr3, p2.nr4,
                                               p3.nr1, p3.nr2, p3.nr3, p3.nr4,
                                               p4.nr1, p4.nr2, p4.nr3, p4.nr4)
                                        if len(set(chk)) != 16:
                                            self.stdout.write(
                                                '[ERROR] Block2x8 does not consist of 16 base pieces: %s' % repr(chk))
                                        for p in chk:
                                            always[p] += 1
                                        # for

                                        count += 1
                                        # if count % 5000 == 0:
                                        #     self.stdout.write("%s" % count)

                                        if len(bulk) >= 1000:
                                            Block2x8.objects.bulk_create(bulk)
                                            bulk = list()
                                # for
                        # for
                # for
        # for

        if len(bulk) > 0:
            Block2x8.objects.bulk_create(bulk)

        paxat = [p for p, v in always.items() if v == count and count > 0]

        return count, paxat

    def _generate_2x8_side2(self, avoid_nrs):
        # side1 must match a potential nr15 piece side3
        exp_side1 = [self.side_nr2reverse[side]
                     for side in Piece2x2.objects.filter(nr2=255).distinct('side3').values_list('side3', flat=True)]
        # side3 must match a potential nr55 piece side1
        exp_side3 = [self.side_nr2reverse[side]
                     for side in Piece2x2.objects.filter(nr4=249).distinct('side1').values_list('side1', flat=True)]
        big_side = [self.side_nr2reverse[self.board[nr].side2] for nr in self.NRS_4X4_SIDE2]
        always = {nr: 0 for nr in range(1, 256+1)}
        count = 0
        bulk = list()
        unused_nrs0 = [nr for nr in self.board_unused_nrs if nr > 60]       # skip borders
        unused_nrs0 = [nr for nr in unused_nrs0 if nr not in avoid_nrs]
        unused_nrs = set(unused_nrs0)
        # query all Piece2x2 needed
        p2x2s = list(Piece2x2.objects.filter(side4__in=big_side,
                                             nr1__in=unused_nrs, nr2__in=unused_nrs,
                                             nr3__in=unused_nrs, nr4__in=unused_nrs))

        for p1 in p2x2s:
            if p1.side4 == big_side[0] and p1.side1 in exp_side1:

                unused_nrs1 = [nr for nr in unused_nrs0 if nr not in (p1.nr1, p1.nr2, p1.nr3, p1.nr4)]
                unused_nrs = set(unused_nrs1)
                p2_exp_s1 = self.side_nr2reverse[p1.side3]

                for p2 in p2x2s:
                    if (p2.side4 == big_side[1] and p2.side1 == p2_exp_s1 and p2.nr1 in unused_nrs
                            and p2.nr2 in unused_nrs and p2.nr3 in unused_nrs and p2.nr4 in unused_nrs):

                        unused_nrs2 = [nr for nr in unused_nrs1 if nr not in (p2.nr1, p2.nr2, p2.nr3, p2.nr4)]
                        unused_nrs = set(unused_nrs2)
                        p3_exp_s1 = self.side_nr2reverse[p2.side3]

                        for p3 in p2x2s:
                            if (p3.side4 == big_side[2] and p3.side1 == p3_exp_s1 and p3.nr1 in unused_nrs
                                    and p3.nr2 in unused_nrs and p3.nr3 in unused_nrs and p3.nr4 in unused_nrs):

                                unused_nrs3 = [nr for nr in unused_nrs2 if nr not in (p3.nr1, p3.nr2, p3.nr3, p3.nr4)]
                                unused_nrs = set(unused_nrs3)
                                p4_exp_s1 = self.side_nr2reverse[p3.side3]

                                for p4 in p2x2s:
                                    if (p4.side4 == big_side[3] and p4.side1 == p4_exp_s1 and p4.side3 in exp_side3
                                            and p4.nr1 in unused_nrs and p4.nr2 in unused_nrs and p4.nr3 in unused_nrs
                                            and p4.nr4 in unused_nrs):

                                        block = Block2x8(
                                                        processor=self.my_processor,
                                                        type=2,
                                                        p1=p1.nr, p2=p2.nr, p3=p3.nr, p4=p4.nr,
                                                        b1=big_side[0], b2=big_side[1], b3=big_side[2], b4=big_side[3],
                                                        nr1=p1.nr1, nr2=p1.nr2, nr3=p1.nr3, nr4=p1.nr4,
                                                        nr5=p2.nr1, nr6=p2.nr2, nr7=p2.nr3, nr8=p2.nr4,
                                                        nr9=p3.nr1, nr10=p3.nr2, nr11=p3.nr3, nr12=p3.nr4,
                                                        nr13=p4.nr1, nr14=p4.nr2, nr15=p4.nr3, nr16=p4.nr4,
                                                        side1=p1.side1,
                                                        side2=0,
                                                        side3=p4.side3,
                                                        side4=0)            # big side
                                        bulk.append(block)

                                        chk = (p1.nr1, p1.nr2, p1.nr3, p1.nr4,
                                               p2.nr1, p2.nr2, p2.nr3, p2.nr4,
                                               p3.nr1, p3.nr2, p3.nr3, p3.nr4,
                                               p4.nr1, p4.nr2, p4.nr3, p4.nr4)
                                        if len(set(chk)) != 16:
                                            self.stdout.write(
                                                '[ERROR] Block2x8 does not consist of 16 base pieces: %s' % repr(chk))
                                        for p in chk:
                                            always[p] += 1
                                        # for

                                        count += 1
                                        # if count % 5000 == 0:
                                        #     self.stdout.write("%s" % count)

                                        if len(bulk) >= 1000:
                                            Block2x8.objects.bulk_create(bulk)
                                            bulk = list()
                                # for
                        # for
                # for
        # for

        if len(bulk) > 0:
            Block2x8.objects.bulk_create(bulk)

        paxat = [p for p, v in always.items() if v == count and count > 0]

        return count, paxat

    def _generate_2x8_side3(self, avoid_nrs):
        # side2 must match a potential nr55 piece side4
        exp_side2 = [self.side_nr2reverse[side]
                     for side in Piece2x2.objects.filter(nr4=249).distinct('side4').values_list('side4', flat=True)]
        # side4 must match a potential nr50 piece side2
        exp_side4 = [self.side_nr2reverse[side]
                     for side in Piece2x2.objects.filter(nr3=181).distinct('side2').values_list('side2', flat=True)]
        big_side = [self.side_nr2reverse[self.board[nr].side3] for nr in self.NRS_4X4_SIDE3]
        always = {nr: 0 for nr in range(1, 256+1)}
        count = 0
        bulk = list()
        unused_nrs0 = [nr for nr in self.board_unused_nrs if nr > 60]       # skip borders
        unused_nrs0 = [nr for nr in unused_nrs0 if nr not in avoid_nrs]
        unused_nrs = set(unused_nrs0)
        # query all Piece2x2 needed
        p2x2s = list(Piece2x2.objects.filter(side1__in=big_side,
                                             nr1__in=unused_nrs, nr2__in=unused_nrs,
                                             nr3__in=unused_nrs, nr4__in=unused_nrs))

        for p1 in p2x2s:
            if p1.side1 == big_side[0] and p1.side2 in exp_side2:

                unused_nrs1 = [nr for nr in unused_nrs0 if nr not in (p1.nr1, p1.nr2, p1.nr3, p1.nr4)]
                unused_nrs = set(unused_nrs1)
                p2_exp_s2 = self.side_nr2reverse[p1.side4]

                for p2 in p2x2s:
                    if (p2.side1 == big_side[1] and p2.side2 == p2_exp_s2 and p2.nr1 in unused_nrs
                            and p2.nr2 in unused_nrs and p2.nr3 in unused_nrs and p2.nr4 in unused_nrs):

                        unused_nrs2 = [nr for nr in unused_nrs1 if nr not in (p2.nr1, p2.nr2, p2.nr3, p2.nr4)]
                        unused_nrs = set(unused_nrs2)
                        p3_exp_s2 = self.side_nr2reverse[p2.side4]

                        for p3 in p2x2s:
                            if (p3.side1 == big_side[2] and p3.side2 == p3_exp_s2 and p3.nr1 in unused_nrs
                                    and p3.nr2 in unused_nrs and p3.nr3 in unused_nrs and p3.nr4 in unused_nrs):

                                unused_nrs3 = [nr for nr in unused_nrs2 if nr not in (p3.nr1, p3.nr2, p3.nr3, p3.nr4)]
                                unused_nrs = set(unused_nrs3)
                                p4_exp_s2 = self.side_nr2reverse[p3.side4]

                                for p4 in p2x2s:
                                    if (p4.side1 == big_side[3] and p4.side2 == p4_exp_s2 and p4.side4 in exp_side4
                                            and p4.nr1 in unused_nrs and p4.nr2 in unused_nrs and p4.nr3 in unused_nrs
                                            and p4.nr4 in unused_nrs):

                                        block = Block2x8(
                                                        processor=self.my_processor,
                                                        type=3,
                                                        p1=p1.nr, p2=p2.nr, p3=p3.nr, p4=p4.nr,
                                                        b1=big_side[0], b2=big_side[1], b3=big_side[2], b4=big_side[3],
                                                        nr1=p1.nr1, nr2=p1.nr2, nr3=p1.nr3, nr4=p1.nr4,
                                                        nr5=p2.nr1, nr6=p2.nr2, nr7=p2.nr3, nr8=p2.nr4,
                                                        nr9=p3.nr1, nr10=p3.nr2, nr11=p3.nr3, nr12=p3.nr4,
                                                        nr13=p4.nr1, nr14=p4.nr2, nr15=p4.nr3, nr16=p4.nr4,
                                                        side1=0,            # big side
                                                        side2=p1.side2,
                                                        side3=0,
                                                        side4=p4.side4)
                                        bulk.append(block)

                                        chk = (p1.nr1, p1.nr2, p1.nr3, p1.nr4,
                                               p2.nr1, p2.nr2, p2.nr3, p2.nr4,
                                               p3.nr1, p3.nr2, p3.nr3, p3.nr4,
                                               p4.nr1, p4.nr2, p4.nr3, p4.nr4)
                                        if len(set(chk)) != 16:
                                            self.stdout.write(
                                                '[ERROR] Block2x8 does not consist of 16 base pieces: %s' % repr(chk))
                                        for p in chk:
                                            always[p] += 1
                                        # for

                                        count += 1
                                        # if count % 5000 == 0:
                                        #     self.stdout.write("%s" % count)

                                        if len(bulk) >= 1000:
                                            Block2x8.objects.bulk_create(bulk)
                                            bulk = list()
                                # for
                        # for
                # for
        # for

        if len(bulk) > 0:
            Block2x8.objects.bulk_create(bulk)

        paxat = [p for p, v in always.items() if v == count and count > 0]

        return count, paxat

    def _generate_2x8_side4(self, avoid_nrs):
        # side1 must match a potential nr10 piece side3
        exp_side1 = [self.side_nr2reverse[side]
                     for side in Piece2x2.objects.filter(nr1=208).distinct('side3').values_list('side3', flat=True)]
        # side3 must match a potential nr50 piece side1
        exp_side3 = [self.side_nr2reverse[side]
                     for side in Piece2x2.objects.filter(nr3=181).distinct('side1').values_list('side1', flat=True)]
        big_side = [self.side_nr2reverse[self.board[nr].side4] for nr in self.NRS_4X4_SIDE4]
        always = {nr: 0 for nr in range(1, 256+1)}
        count = 0
        bulk = list()
        unused_nrs0 = [nr for nr in self.board_unused_nrs if nr > 60]       # skip borders
        unused_nrs0 = [nr for nr in unused_nrs0 if nr not in avoid_nrs]
        unused_nrs = set(unused_nrs0)
        # query all Piece2x2 needed
        p2x2s = list(Piece2x2.objects.filter(side2__in=big_side, nr1__in=unused_nrs, nr2__in=unused_nrs,
                                             nr3__in=unused_nrs, nr4__in=unused_nrs))

        for p1 in p2x2s:
            if p1.side2 == big_side[0] and p1.side3 in exp_side3:

                unused_nrs1 = [nr for nr in unused_nrs0 if nr not in (p1.nr1, p1.nr2, p1.nr3, p1.nr4)]
                unused_nrs = set(unused_nrs1)
                p2_exp_s3 = self.side_nr2reverse[p1.side1]

                for p2 in p2x2s:
                    if (p2.side2 == big_side[1] and p2.side3 == p2_exp_s3 and p2.nr1 in unused_nrs
                            and p2.nr2 in unused_nrs and p2.nr3 in unused_nrs and p2.nr4 in unused_nrs):

                        unused_nrs2 = [nr for nr in unused_nrs1 if nr not in (p2.nr1, p2.nr2, p2.nr3, p2.nr4)]
                        unused_nrs = set(unused_nrs2)
                        p3_exp_s3 = self.side_nr2reverse[p2.side1]

                        for p3 in p2x2s:
                            if (p3.side2 == big_side[2] and p3.side3 == p3_exp_s3 and p3.nr1 in unused_nrs
                                    and p3.nr2 in unused_nrs and p3.nr3 in unused_nrs and p3.nr4 in unused_nrs):

                                unused_nrs3 = [nr for nr in unused_nrs2 if nr not in (p3.nr1, p3.nr2, p3.nr3, p3.nr4)]
                                unused_nrs = set(unused_nrs3)
                                p4_exp_s3 = self.side_nr2reverse[p3.side1]

                                for p4 in p2x2s:
                                    if (p4.side2 == big_side[3] and p4.side3 == p4_exp_s3 and p4.side1 in exp_side1
                                            and p4.nr1 in unused_nrs and p4.nr2 in unused_nrs and p4.nr3 in unused_nrs
                                            and p4.nr4 in unused_nrs):

                                        block = Block2x8(
                                                        processor=self.my_processor,
                                                        type=4,
                                                        p1=p1.nr, p2=p2.nr, p3=p3.nr, p4=p4.nr,
                                                        b1=big_side[0], b2=big_side[1], b3=big_side[2], b4=big_side[3],
                                                        nr1=p1.nr1, nr2=p1.nr2, nr3=p1.nr3, nr4=p1.nr4,
                                                        nr5=p2.nr1, nr6=p2.nr2, nr7=p2.nr3, nr8=p2.nr4,
                                                        nr9=p3.nr1, nr10=p3.nr2, nr11=p3.nr3, nr12=p3.nr4,
                                                        nr13=p4.nr1, nr14=p4.nr2, nr15=p4.nr3, nr16=p4.nr4,
                                                        side1=p4.side1,
                                                        side2=0,            # big side
                                                        side3=p1.side3,
                                                        side4=0)
                                        bulk.append(block)

                                        chk = (p1.nr1, p1.nr2, p1.nr3, p1.nr4,
                                               p2.nr1, p2.nr2, p2.nr3, p2.nr4,
                                               p3.nr1, p3.nr2, p3.nr3, p3.nr4,
                                               p4.nr1, p4.nr2, p4.nr3, p4.nr4)
                                        if len(set(chk)) != 16:
                                            self.stdout.write(
                                                '[ERROR] Block2x8 does not consist of 16 base pieces: %s' % repr(chk))
                                        for p in chk:
                                            always[p] += 1
                                        # for

                                        count += 1
                                        # if count % 5000 == 0:
                                        #     self.stdout.write("%s" % count)

                                        if len(bulk) >= 1000:
                                            Block2x8.objects.bulk_create(bulk)
                                            bulk = list()
                                # for
                        # for
                # for
        # for

        if len(bulk) > 0:
            Block2x8.objects.bulk_create(bulk)

        paxat = [p for p, v in always.items() if v == count and count > 0]

        return count, paxat

    def _generate_2x8_blocks(self):
        self.stdout.write('[INFO] Generating Block2x8')

        avoid_nrs2 = list()
        avoid_nrs3 = list()
        avoid_nrs4 = list()
        prev_count = 0
        new_count = 999

        while new_count != prev_count:

            if prev_count > 0:
                print('New count %s --> another round!' % new_count)

            Block2x8.objects.filter(processor=self.my_processor).delete()

            options, avoid_nrs1 = self._generate_2x8_side1(avoid_nrs2 + avoid_nrs3 + avoid_nrs4)
            self.stdout.write('[INFO] Blocks for side1: %s; paxat: %s' % (options, repr(avoid_nrs1)))
            if options == 0:
                return False

            options, avoid_nrs2 = self._generate_2x8_side2(avoid_nrs1 + avoid_nrs3 + avoid_nrs4)
            self.stdout.write('[INFO] Blocks for side2: %s; paxat: %s' % (options, repr(avoid_nrs2)))
            if options == 0:
                return False

            options, avoid_nrs3 = self._generate_2x8_side3(avoid_nrs1 + avoid_nrs2 + avoid_nrs4)
            self.stdout.write('[INFO] Blocks for side3: %s; paxat: %s' % (options, repr(avoid_nrs3)))
            if options == 0:
                return False

            options, avoid_nrs4 = self._generate_2x8_side4(avoid_nrs1 + avoid_nrs2 + avoid_nrs3)
            self.stdout.write('[INFO] Blocks for side4: %s; paxat: %s' % (options, repr(avoid_nrs4)))
            if options == 0:
                return False

            if new_count == 999:
                # optimization: avoid second round when avoid_nrs1 is not empty, since it will be considered
                prev_count = len(avoid_nrs1)
            else:
                prev_count = new_count

            new_count = len(avoid_nrs1) + len(avoid_nrs2) + len(avoid_nrs3) + len(avoid_nrs4)
        # while

        return True

    def _generate_half6_c12(self):
        # find combinations + add corner
        self.stdout.write('[INFO] Starting search for Half6 1-2')
        found = 0

        # iterate through the Block2x8 for each side, then add corners
        big_side1 = [self.side_nr2reverse[self.board[nr].side1] for nr in self.NRS_4X4_SIDE1]
        big_side2 = [self.side_nr2reverse[self.board[nr].side2] for nr in self.NRS_4X4_SIDE2]

        for c1 in self._iter_for_nr(15, 0):
            self._board_fill_nr(15, c1)

            block1_exp_s2 = self.side_nr2reverse[c1.side4]
            block2_exp_s1 = self.side_nr2reverse[c1.side3]

            unused_nrs0 = [nr for nr in self.board_unused_nrs[:] if nr > 60]        # skip borders
            unused_nrs = set(unused_nrs0)
            for block1 in (Block2x8
                           .objects
                           .filter(processor=self.my_processor,
                                   type=1,
                                   side2=block1_exp_s2,
                                   b1=big_side1[0], b2=big_side1[1], b3=big_side1[2], b4=big_side1[3])
                           .filter(nr1__in=unused_nrs, nr2__in=unused_nrs, nr3__in=unused_nrs, nr4__in=unused_nrs,
                                   nr5__in=unused_nrs, nr6__in=unused_nrs, nr7__in=unused_nrs, nr8__in=unused_nrs,
                                   nr9__in=unused_nrs, nr10__in=unused_nrs, nr11__in=unused_nrs, nr12__in=unused_nrs,
                                   nr13__in=unused_nrs, nr14__in=unused_nrs, nr15__in=unused_nrs, nr16__in=unused_nrs)):

                # place the 4 pieces
                self._board_fill_nr(11, Piece2x2.objects.get(nr=block1.p1))
                self._board_fill_nr(12, Piece2x2.objects.get(nr=block1.p2))
                self._board_fill_nr(13, Piece2x2.objects.get(nr=block1.p3))
                self._board_fill_nr(14, Piece2x2.objects.get(nr=block1.p4))

                # iterate through the Block2x8 for side2
                unused_nrs1 = [nr for nr in self.board_unused_nrs[:] if nr > 60]  # skip borders
                unused_nrs = set(unused_nrs1)
                for block2 in (Block2x8
                               .objects
                               .filter(processor=self.my_processor,
                                       type=2,
                                       side1=block2_exp_s1,
                                       b1=big_side2[0], b2=big_side2[1], b3=big_side2[2], b4=big_side2[3])
                               .filter(nr1__in=unused_nrs, nr2__in=unused_nrs, nr3__in=unused_nrs, nr4__in=unused_nrs,
                                       nr5__in=unused_nrs, nr6__in=unused_nrs, nr7__in=unused_nrs, nr8__in=unused_nrs,
                                       nr9__in=unused_nrs, nr10__in=unused_nrs, nr11__in=unused_nrs,
                                       nr12__in=unused_nrs, nr13__in=unused_nrs, nr14__in=unused_nrs,
                                       nr15__in=unused_nrs, nr16__in=unused_nrs)):

                    # place the 4 pieces
                    self._board_fill_nr(23, Piece2x2.objects.get(nr=block2.p1))
                    self._board_fill_nr(31, Piece2x2.objects.get(nr=block2.p2))
                    self._board_fill_nr(39, Piece2x2.objects.get(nr=block2.p3))
                    self._board_fill_nr(47, Piece2x2.objects.get(nr=block2.p4))

                    # verify a solution is possible for positions 10 and 55
                    count10, _, _ = self._count_2x2(10, self.board_unused_nrs)
                    count55, _, _ = self._count_2x2(55, self.board_unused_nrs)

                    if count10 > 0 and count55 > 0:
                        half = Half6(
                                    processor=self.my_processor,
                                    based_on_4x4=self.based_on,
                                    type=12,
                                    b1=big_side1[0], b2=big_side1[1], b3=big_side1[2], b4=big_side1[3],
                                    b5=big_side2[0], b6=big_side2[1], b7=big_side2[2], b8=big_side2[3],
                                    p1=block1.pk,
                                    p2=block2.pk,
                                    c1=c1.nr,
                                    nr1=block1.nr1, nr2=block1.nr2, nr3=block1.nr3, nr4=block1.nr4,
                                    nr5=block1.nr5, nr6=block1.nr6, nr7=block1.nr7, nr8=block1.nr8,
                                    nr9=block1.nr9, nr10=block1.nr10, nr11=block1.nr11, nr12=block1.nr12,
                                    nr13=block1.nr13, nr14=block1.nr14, nr15=block1.nr15, nr16=block1.nr16,
                                    nr17=block2.nr1, nr18=block2.nr2, nr19=block2.nr3, nr20=block2.nr4,
                                    nr21=block2.nr5, nr22=block2.nr6, nr23=block2.nr7, nr24=block2.nr8,
                                    nr25=block2.nr9, nr26=block2.nr10, nr27=block2.nr11, nr28=block2.nr12,
                                    nr29=block2.nr13, nr30=block2.nr14, nr31=block2.nr15, nr32=block2.nr16,
                                    nr33=c1.nr1, nr34=c1.nr2, nr35=c1.nr3, nr36=c1.nr4)     # nr34 = hint (255)
                        half.save()
                        found += 1
                        if found % 100 == 0:
                            print(found)

                    self._board_free_nr(47)
                    self._board_free_nr(39)
                    self._board_free_nr(31)
                    self._board_free_nr(23)

                    # if found > 500:
                    #     break
                # for

                self._board_free_nr(14)
                self._board_free_nr(13)
                self._board_free_nr(12)
                self._board_free_nr(11)

                # if found > 500:
                #     break
            # for

            self._board_free_nr(15)

            # if found > 500:
            #     break
        # for

        print('[INFO] Found %s' % found)

    def _generate_half6_c34(self):
        # find combinations + add corner
        self.stdout.write('[INFO] Starting search for Half6 3-4')
        found = 0

        # iterate through the Block2x8 for each side, then add corners
        big_side3 = [self.side_nr2reverse[self.board[nr].side3] for nr in self.NRS_4X4_SIDE3]
        big_side4 = [self.side_nr2reverse[self.board[nr].side4] for nr in self.NRS_4X4_SIDE4]

        # start with the corner on position 50
        for c1 in self._iter_for_nr(50, 0):
            self._board_fill_nr(50, c1)

            block2_exp_s3 = self.side_nr2reverse[c1.side1]
            block1_exp_s4 = self.side_nr2reverse[c1.side2]

            # iterate through the Block2x8 for side3
            unused_nrs0 = [nr for nr in self.board_unused_nrs[:] if nr > 60]        # skip borders
            unused_nrs = set(unused_nrs0)
            for block1 in (Block2x8
                           .objects
                           .filter(processor=self.my_processor,
                                   type=3,
                                   side4=block1_exp_s4,
                                   b1=big_side3[0], b2=big_side3[1], b3=big_side3[2], b4=big_side3[3])
                           .filter(nr1__in=unused_nrs, nr2__in=unused_nrs, nr3__in=unused_nrs, nr4__in=unused_nrs,
                                   nr5__in=unused_nrs, nr6__in=unused_nrs, nr7__in=unused_nrs, nr8__in=unused_nrs,
                                   nr9__in=unused_nrs, nr10__in=unused_nrs, nr11__in=unused_nrs, nr12__in=unused_nrs,
                                   nr13__in=unused_nrs, nr14__in=unused_nrs, nr15__in=unused_nrs, nr16__in=unused_nrs)):

                # place the 4 pieces
                self._board_fill_nr(54, Piece2x2.objects.get(nr=block1.p1))
                self._board_fill_nr(53, Piece2x2.objects.get(nr=block1.p2))
                self._board_fill_nr(52, Piece2x2.objects.get(nr=block1.p3))
                self._board_fill_nr(51, Piece2x2.objects.get(nr=block1.p4))

                # iterate through the Block2x8 for side4
                unused_nrs1 = [nr for nr in self.board_unused_nrs[:] if nr > 60]  # skip borders
                unused_nrs = set(unused_nrs1)
                for block2 in (Block2x8
                               .objects
                               .filter(processor=self.my_processor,
                                       type=4,
                                       side3=block2_exp_s3,
                                       b1=big_side4[0], b2=big_side4[1], b3=big_side4[2], b4=big_side4[3])
                               .filter(nr1__in=unused_nrs, nr2__in=unused_nrs, nr3__in=unused_nrs, nr4__in=unused_nrs,
                                       nr5__in=unused_nrs, nr6__in=unused_nrs, nr7__in=unused_nrs, nr8__in=unused_nrs,
                                       nr9__in=unused_nrs, nr10__in=unused_nrs, nr11__in=unused_nrs,
                                       nr12__in=unused_nrs, nr13__in=unused_nrs, nr14__in=unused_nrs,
                                       nr15__in=unused_nrs, nr16__in=unused_nrs)):

                    # place the 4 pieces
                    self._board_fill_nr(42, Piece2x2.objects.get(nr=block2.p1))
                    self._board_fill_nr(34, Piece2x2.objects.get(nr=block2.p2))
                    self._board_fill_nr(26, Piece2x2.objects.get(nr=block2.p3))
                    self._board_fill_nr(18, Piece2x2.objects.get(nr=block2.p4))

                    # verify a solution is possible for positions 10 and 55
                    count10, _, _ = self._count_2x2(10, self.board_unused_nrs)
                    count55, _, _ = self._count_2x2(55, self.board_unused_nrs)

                    if count10 > 0 and count55 > 0:
                        half = Half6(
                                    processor=self.my_processor,
                                    based_on_4x4=self.based_on,
                                    type=34,
                                    b1=big_side3[0], b2=big_side3[1], b3=big_side3[2], b4=big_side3[3],
                                    b5=big_side4[0], b6=big_side4[1], b7=big_side4[2], b8=big_side4[3],
                                    p1=block1.pk,
                                    p2=block2.pk,
                                    c1=c1.nr,
                                    nr1=block1.nr1, nr2=block1.nr2, nr3=block1.nr3, nr4=block1.nr4,
                                    nr5=block1.nr5, nr6=block1.nr6, nr7=block1.nr7, nr8=block1.nr8,
                                    nr9=block1.nr9, nr10=block1.nr10, nr11=block1.nr11, nr12=block1.nr12,
                                    nr13=block1.nr13, nr14=block1.nr14, nr15=block1.nr15, nr16=block1.nr16,
                                    nr17=block2.nr1, nr18=block2.nr2, nr19=block2.nr3, nr20=block2.nr4,
                                    nr21=block2.nr5, nr22=block2.nr6, nr23=block2.nr7, nr24=block2.nr8,
                                    nr25=block2.nr9, nr26=block2.nr10, nr27=block2.nr11, nr28=block2.nr12,
                                    nr29=block2.nr13, nr30=block2.nr14, nr31=block2.nr15, nr32=block2.nr16,
                                    nr33=c1.nr1, nr34=c1.nr2, nr35=c1.nr3, nr36=c1.nr4)     # nr35 = hint: 181
                        half.save()
                        found += 1
                        if found % 100 == 0:
                            print(found)

                    self._board_free_nr(18)
                    self._board_free_nr(26)
                    self._board_free_nr(34)
                    self._board_free_nr(42)

                    # if found > 500:
                    #     break
                # for

                self._board_free_nr(51)
                self._board_free_nr(52)
                self._board_free_nr(53)
                self._board_free_nr(54)

                # if found > 500:
                #     break
            # for

            self._board_free_nr(50)

            # if found > 500:
            #     break
        # for

        print('[INFO] Found %s' % found)

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
                    if self._generate_2x8_blocks():
                        self._generate_half6_c12()
                        self._generate_half6_c34()
                        self.find_6x6()
                except KeyboardInterrupt:
                    # warning for closed stdout!
                    sol.processor = 0
                    sol.save(update_fields=['processor'])
                    do_quit = True
                else:
                    sol.is_processed = True
                    sol.save(update_fields=['is_processed'])

                # clean up
                Half6.objects.filter(processor=self.my_processor).delete()
                Block2x8.objects.filter(processor=self.my_processor).delete()
            else:
                self.stdout.write('[INFO] Waiting for new 4x4 (press Ctrl+C to abort)')
                time.sleep(60)
        # while

        # warning for closed stdout..
        self.stdout.write('[WARNING] Interrupted')

# end of file
