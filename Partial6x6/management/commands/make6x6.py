# -*- coding: utf-8 -*-

#  Copyright (c) 2023 Ramon van der Winkel.
#  All rights reserved.
#  Licensed under BSD-3-Clause-Clear. See LICENSE file for details.

from django.core.management.base import BaseCommand
from BasePieces.hints import ALL_HINT_NRS
from Pieces2x2.models import TwoSides, Piece2x2
from Pieces2x2.helpers import NRS_CORNER, NRS_BORDER, NRS_HINTS, NRS_NEIGHBOURS
from Partial4x4.models import Partial4x4, NRS_PARTIAL_4X4
from Partial6x6.models import Partial6x6, Quart6, NRS_PARTIAL_6X6
import time


class Command(BaseCommand):

    help = "Partial6x6 generator using Quart6"

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
        self.board_gap_count = 0
        self.board_unused_nrs = list()
        self.board_solve_order = list()  # [nr, nr, ..]
        # self.all_unused_nrs = list()
        self.based_on = 0
        self.interval_mins = 15
        self.my_processor = int(time.time() - 946684800.0)     # seconds since Jan 1, 2000

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

    def add_arguments(self, parser):
        parser.add_argument('--verbose', action='store_true')
        parser.add_argument('--reset', action='store_true')

    def _count_2x2(self, nr):
        # get the sides
        s1, s2, s3, s4 = self._get_sides(nr)
        p1 = p2 = p3 = p4 = None
        x1 = x2 = x3 = x4 = None

        if nr in NRS_CORNER:
            if nr == 1:
                s1 = s4 = self.rev_border
            elif nr == 8:
                s1 = s2 = self.rev_border
            elif nr == 57:
                s3 = s4 = self.rev_border
            else:
                s2 = s3 = self.rev_border

        elif nr in NRS_BORDER:
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

            if nr in NRS_HINTS:
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

        unused_nrs = self.board_unused_nrs
        must_have_nrs = list()

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
        else:
            freedom = '0'

        return count, freedom, must_have_nrs

    def _document_gaps(self, sol):
        for nr in range(1, 64+1):
            if nr not in NRS_PARTIAL_6X6:
                count, freedom, must_have_nrs = self._count_2x2(nr)

                note = "%s %s" % (count, freedom)
                note = note[:30]        # avoid database errors

                field_note = 'note%s' % nr
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

        sol = Partial6x6(
                based_on_4x4=self.based_on)

        for nr in range(1, 64+1):
            if nr in NRS_PARTIAL_6X6:
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
        nr1, nr2, nr3, nr4 = NRS_NEIGHBOURS[nr]

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

    def _iter_for_nr_no_borders(self, nr, print_todo=False):

        # get the sides
        s1, s2, s3, s4 = self._get_sides(nr)
        x1 = x2 = x3 = x4 = self.rev_border
        p1 = p2 = p3 = p4 = None

        if nr in NRS_HINTS:
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

        qset = Piece2x2.objects.order_by('nr')

        # skip outer borders
        unused_nrs = [nr for nr in self.board_unused_nrs if nr > 60]

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

        if print_todo:
            todo = qset.count()
        else:
            todo = 0

        for p in qset:
            if print_todo:
                self.stdout.write('[%s] %s left' % (nr, todo))
                todo -= 1

            yield p
        # for

    def load_partial4x4(self, sol):
        for nr in range(1, 64+1):
            self.board[nr] = None
        # for

        self.board_unused_nrs = [nr for nr in range(1, 256+1) if nr not in ALL_HINT_NRS]

        for nr in NRS_PARTIAL_4X4:
            field_nr = 'nr%s' % nr
            p_nr = getattr(sol, field_nr)
            p = Piece2x2.objects.get(nr=p_nr)
            self._board_fill_nr(nr, p)
        # for

        self.board_gap_count = 64 - 16
        self.board_solve_order = list()     # [nr, nr, ..]
        self.based_on = sol.pk

    def _can_fill_nrs_no_borders(self, nrs):

        unused_nrs = [nr for nr in self.board_unused_nrs if nr > 60]  # skip borders

        qset = Piece2x2.objects.all()
        qset = qset.filter(nr1__in=unused_nrs, nr2__in=unused_nrs, nr3__in=unused_nrs, nr4__in=unused_nrs)

        for nr in nrs:
            if nr:
                s1, s2, s3, s4 = self._get_sides(nr)
                qset2 = qset

                if s1 and s2 and not s3 and not s4:
                    # s1-s2
                    qset2 = qset2.filter(side1=s1, side2=s2)

                elif not s1 and s2 and s3 and not s4:
                    # s2-s3
                    qset2 = qset2.filter(side2=s2, side3=s3)

                elif not s1 and not s2 and s3 and s4:
                    # s3-s4
                    qset2 = qset2.filter(side3=s3, side4=s4)

                elif s1 and not s2 and not s3 and s4:
                    # s4-s1
                    qset2 = qset2.filter(side4=s4, side1=s1)

                else:
                    if s1:
                        qset2 = qset2.filter(side1=s1)
                    if s2:
                        qset2 = qset2.filter(side2=s2)
                    if s3:
                        qset2 = qset2.filter(side3=s3)
                    if s4:
                        qset2 = qset2.filter(side4=s4)

                first = qset2.first()
                if first is None:
                    return False
        # for
        return True

    def _fill_quart(self, hint_nr, nr_p1, nr_c, nr_p2, nr_m1, nr_m2, nr_chk1, nr_chk2):
        unused_nrs = [nr for nr in self.board_unused_nrs if nr > 60]       # skip borders
        unused_nrs.append(hint_nr)
        unused_nrs = set(unused_nrs)

        # iterate over the first Half6
        for quart in (Quart6
                      .objects
                      .filter(processor=self.my_processor,
                              based_on_4x4=self.based_on,
                              type=nr_c)
                      .filter(nr1__in=unused_nrs, nr2__in=unused_nrs, nr3__in=unused_nrs, nr4__in=unused_nrs,
                              nr5__in=unused_nrs, nr6__in=unused_nrs, nr7__in=unused_nrs, nr8__in=unused_nrs,
                              nr9__in=unused_nrs, nr10__in=unused_nrs, nr11__in=unused_nrs, nr12__in=unused_nrs)):

            # place the pieces
            self._board_fill_nr(nr_p1, Piece2x2.objects.get(nr=quart.p1))
            self._board_fill_nr(nr_c,  Piece2x2.objects.get(nr=quart.c1))
            self._board_fill_nr(nr_p2, Piece2x2.objects.get(nr=quart.p2))

            # cement the piece in place
            for m1 in self._iter_for_nr_no_borders(nr_m1):
                self._board_fill_nr(nr_m1, m1)

                for m2 in self._iter_for_nr_no_borders(nr_m2):
                    self._board_fill_nr(nr_m2, m2)

                    if self._can_fill_nrs_no_borders((nr_chk1, nr_chk2)):
                        yield quart

                    self._board_free_nr(nr_m2)
                # for

                self._board_free_nr(nr_m1)
            # for

            self._board_free_nr(nr_p2)
            self._board_free_nr(nr_c)
            self._board_free_nr(nr_p1)
        # for

    def find_6x6(self):
        self.stdout.write('[INFO] Start solving')
        count = 0

        # gap count: 48
        for _ in self._fill_quart(208, 18, 10, 11, 26, 12, 13, 34):
            # gap count: 43
            for _ in self._fill_quart(255, 14, 15, 23, 13, 31, 34, 39):
                # gap count: 38
                for _ in self._fill_quart(249, 47, 55, 54, 39, 53, 52, 34):
                    # gap count: 33
                    for _ in self._fill_quart(181, 51, 50, 42, 34, 52, None, None):
                        # gap count: 28

                        # complete 6x6
                        self._save_board6x6()
                        count += 1

                    # for
                # for
            # for
        # for

        self.stdout.write('[INFO] Done solving, found %s Partial6x6' % count)

    def _can_fill_nrs_border(self, nr_c):
        # verify one-site match with opposite side being a border

        """
                      side2
                    +---+---+  <-- border
                    |   |   |
                +---+---+---+
                |   | c | p |
          side1 +---+---+---+
                |   | p |
                +---+---+

        """

        if nr_c == 10:
            p18 = self.board[18]
            p10 = self.board[10]
            p11 = self.board[11]
            sides1 = (p18.exp_s4, p10.exp_s4)
            sides2 = (p10.exp_s1, p11.exp_s1)

        elif nr_c == 15:
            p14 = self.board[14]
            p15 = self.board[15]
            p23 = self.board[23]
            sides1 = (p14.exp_s1, p15.exp_s1)
            sides2 = (p15.exp_s2, p23.exp_s2)

        elif nr_c == 50:
            p51 = self.board[51]
            p50 = self.board[50]
            p42 = self.board[42]
            sides1 = (p51.exp_s3, p50.exp_s3)
            sides2 = (p50.exp_s4, p42.exp_s4)

        elif nr_c == 55:
            p47 = self.board[47]
            p55 = self.board[55]
            p54 = self.board[54]
            sides1 = (p47.exp_s2, p55.exp_s2)
            sides2 = (p55.exp_s3, p54.exp_s3)

        else:
            return False

        unused_nrs = self.board_unused_nrs

        qset = Piece2x2.objects.filter(side1=self.rev_border)
        qset = qset.filter(nr1__in=unused_nrs, nr2__in=unused_nrs, nr3__in=unused_nrs, nr4__in=unused_nrs)

        """
                side1=border        
             +---+---+
             |   |   |  side2
             +---+---+
                side3
             
        """

        for p1 in qset.filter(side3=sides1[0]):
            exp_s4 = self.side_nr2reverse[p1.side2]
            p2 = qset.filter(side3=sides1[1], side4=exp_s4).first()
            if not p2:
                return False
            # found at least 1
            break
        # for

        for p3 in qset.filter(side3=sides2[0]):
            exp_s4 = self.side_nr2reverse[p3.side2]
            p4 = qset.filter(side3=sides2[1], side4=exp_s4).first()
            if not p4:
                return False
            # found at least 1
            break
        # for

        return True

    def _iter_border(self, nr, **kwargs):
        unused = self.board_unused_nrs[:]
        for p in Piece2x2.objects.filter(nr1__in=unused, nr2__in=unused, nr3__in=unused, nr4__in=unused, **kwargs):
            self._board_fill_nr(nr, p)
            p2 = self.board[nr]     # contains exp_s*
            yield p2
            self._board_free_nr(nr)
        # for

    def _iter_no_border(self, nr, **kwargs):
        unused = [nr for nr in self.board_unused_nrs if nr > 60]
        for p in Piece2x2.objects.filter(nr1__in=unused, nr2__in=unused, nr3__in=unused, nr4__in=unused, **kwargs):
            self._board_fill_nr(nr, p)
            p2 = self.board[nr]     # contains exp_s*
            yield p2
            self._board_free_nr(nr)
        # for

    def _get_nrs(self, **kwargs):
        unused = self.board_unused_nrs[:]
        qset = Piece2x2.objects.filter(nr1__in=unused, nr2__in=unused, nr3__in=unused, nr4__in=unused, **kwargs)
        return list(qset.values_list('nr', flat=True))

    def _get_candidates_p11(self):
        nrs = list()
        p10 = self.board[10]
        p19 = self.board[19]
        for p11 in self._iter_no_border(11, side4=p10.exp_s4, side3=p19.exp_s3):
            done = False
            for p2 in self._iter_border(2, side1=self.rev_border, side3=p10.exp_s3):
                for _ in self._iter_border(3, side1=self.rev_border, side4=p2.exp_s4, side3=p11.exp_s3):
                    nrs.append(p11.nr)
                    done = True
                    break
                # for
                if done:
                    break
            # for
        # for
        return set(nrs)

    def _get_candidates_p14(self):
        nrs = list()
        p15 = self.board[15]
        p22 = self.board[22]
        for p14 in self._iter_no_border(14, side2=p15.exp_s2, side3=p22.exp_s3):
            done = False
            for p7 in self._iter_border(7, side1=self.rev_border, side3=p15.exp_s3):
                for _ in self._iter_border(6, side1=self.rev_border, side2=p7.exp_s2, side3=p14.exp_s3):
                    nrs.append(p14.nr)
                    done = True
                    break
                # for
                if done:
                    break
            # for
        # for
        return set(nrs)

    def _get_candidates_p18(self):
        nrs = list()
        p10 = self.board[10]
        p19 = self.board[19]
        for p18 in self._iter_no_border(18, side1=p10.exp_s1, side2=p19.exp_s2):
            done = False
            for p9 in self._iter_border(9, side4=self.rev_border, side2=p10.exp_s2):
                for _ in self._iter_border(17, side4=self.rev_border, side1=p9.exp_s1, side2=p18.exp_s2):
                    nrs.append(p18.nr)
                    done = True
                    break
                # for
                if done:
                    break
            # for
        # for
        return set(nrs)

    def _get_candidates_p23(self):
        nrs = list()
        p15 = self.board[15]
        p22 = self.board[22]
        for p23 in self._iter_no_border(23, side1=p15.exp_s1, side4=p22.exp_s4):
            done = False
            for p16 in self._iter_border(16, side2=self.rev_border, side4=p15.exp_s4):
                for _ in self._iter_border(24, side2=self.rev_border, side1=p16.exp_s1, side4=p23.exp_s4):
                    nrs.append(p23.nr)
                    done = True
                    break
                # for
                if done:
                    break
            # for
        # for
        return set(nrs)

    def _get_candidates_p42(self):
        nrs = list()
        p50 = self.board[50]
        p43 = self.board[43]
        for p42 in self._iter_no_border(42, side3=p50.exp_s3, side2=p43.exp_s2):
            done = False
            for p49 in self._iter_border(49, side4=self.rev_border, side2=p50.exp_s2):
                for _ in self._iter_border(41, side4=self.rev_border, side3=p49.exp_s3, side2=p42.exp_s2):
                    nrs.append(p42.nr)
                    done = True
                    break
                # for
                if done:
                    break
            # for
        # for
        return set(nrs)

    def _get_candidates_p47(self):
        nrs = list()
        p55 = self.board[55]
        p46 = self.board[46]
        for p47 in self._iter_no_border(47, side3=p55.exp_s3, side4=p46.exp_s4):
            done = False
            for p56 in self._iter_border(56, side2=self.rev_border, side4=p55.exp_s4):
                for _ in self._iter_border(48, side2=self.rev_border, side3=p56.exp_s3, side4=p47.exp_s4):
                    nrs.append(p47.nr)
                    done = True
                    break
                # for
                if done:
                    break
            # for
        # for
        return set(nrs)

    def _get_candidates_p51(self):
        nrs = list()
        p50 = self.board[50]
        p43 = self.board[43]
        for p51 in self._iter_no_border(51, side4=p50.exp_s4, side1=p43.exp_s1):
            done = False
            for p58 in self._iter_border(58, side3=self.rev_border, side1=p50.exp_s1):
                for _ in self._iter_border(59, side3=self.rev_border, side4=p58.exp_s4, side1=p51.exp_s3):
                    nrs.append(p51.nr)
                    done = True
                    break
                # for
                if done:
                    break
            # for
        # for
        return set(nrs)

    def _get_candidates_p54(self):
        nrs = list()
        p55 = self.board[55]
        p46 = self.board[46]
        for p54 in self._iter_no_border(54, side2=p55.exp_s2, side1=p46.exp_s1):
            done = False
            for p63 in self._iter_border(63, side3=self.rev_border, side1=p55.exp_s1):
                for _ in self._iter_border(62, side3=self.rev_border, side2=p63.exp_s2, side1=p54.exp_s1):
                    nrs.append(p54.nr)
                    done = True
                    break
                # for
                if done:
                    break
            # for
        # for
        return set(nrs)

    def _get_candidates_p1(self, nr_c):
        if nr_c == 10:
            return self._get_candidates_p18()
        elif nr_c == 15:
            return self._get_candidates_p14()
        elif nr_c == 55:
            return self._get_candidates_p47()
        return self._get_candidates_p51()

    def _get_candidates_p2(self, nr_c):
        if nr_c == 10:
            return self._get_candidates_p11()
        elif nr_c == 15:
            return self._get_candidates_p23()
        elif nr_c == 55:
            return self._get_candidates_p54()
        return self._get_candidates_p42()

    def _iter_nrs_no_borders(self, nrs):
        unused = [nr for nr in self.board_unused_nrs if nr > 60]      # no borders
        qset = Piece2x2.objects.filter(nr1__in=unused, nr2__in=unused, nr3__in=unused, nr4__in=unused, nr__in=nrs)
        for p in qset:
            yield p
        # for

    def _generate_quart6(self, nr_p1, nr_c, nr_p2, nrs_chk):
        count = 0
        reject1_count = reject2_count = 0
        bulk = list()
        for c1 in self._iter_for_nr_no_borders(nr_c):
            self._board_fill_nr(nr_c, c1)

            nrs_p1 = self._get_candidates_p1(nr_c)
            if len(nrs_p1) == 0:
                continue

            nrs_p2 = self._get_candidates_p2(nr_c)
            if len(nrs_p2) == 0:
                continue

            todo = len(nrs_p1) * len(nrs_p2)
            done1 = 0
            print_perc = 1.0

            for p1 in self._iter_nrs_no_borders(nrs_p1):
                self._board_fill_nr(nr_p1, p1)

                done2 = done1
                for p2 in self._iter_nrs_no_borders(nrs_p2):
                    self._board_fill_nr(nr_p2, p2)

                    if self._can_fill_nrs_no_borders(nrs_chk):

                        if self._can_fill_nrs_border(nr_c):

                            quart = Quart6(
                                        processor=self.my_processor,
                                        based_on_4x4=self.based_on,
                                        type=nr_c,
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
                            if len(bulk) >= 25:
                                count += len(bulk)
                                print('Quart6 type %s: %s (reject1 %s, reject2 %s) done1=%s, done2=%s, todo=%s' % (nr_c, count, reject1_count, reject2_count, done1, done2, todo))
                                Quart6.objects.bulk_create(bulk)
                                bulk = list()
                        else:
                            reject1_count += 1

                    else:
                        reject2_count += 1

                    done2 += 1
                    perc = (done2 * 100) / todo
                    if perc >= print_perc:
                        print("%.0f%% done" % perc)
                        print_perc += 1.0

                    self._board_free_nr(nr_p2)
                # for

                done1 += len(nrs_p2)
                self._board_free_nr(nr_p1)
            # for

            self._board_free_nr(nr_c)
        # for

        if len(bulk) > 0:
            count += len(bulk)
            print('Quart6 type %s: %s (reject1 %s, reject2 %s)' % (nr_c, count, reject1_count, reject2_count))
            Quart6.objects.bulk_create(bulk)

    def _generate_all_quart6(self):
        self._generate_quart6(18, 10, 11, (26, 12))
        self._generate_quart6(14, 15, 23, (13, 31))
        self._generate_quart6(51, 50, 42, (34, 52))
        self._generate_quart6(47, 55, 54, (39, 53))

    def handle(self, *args, **options):

        if options['verbose']:
            self.verbose += 1

        if options['reset']:
            self.stdout.write('[WARNING] Resetting Partial4x4s and deleting all Quart6')
            Partial4x4.objects.exclude(processor=0).update(processor=0)
            Partial4x4.objects.filter(is_processed=True).update(is_processed=False)
            Quart6.objects.all().delete()

        self.stdout.write('[INFO] my_processor is %s' % self.my_processor)

        do_quit = False
        while not do_quit:
            sol16 = (Partial4x4
                     .objects
                     .filter(is_processed=False,
                             processor=0)
                     .order_by('pk')      # lowest first
                     .first())

            if sol16:
                self.stdout.write('[INFO] Loading Partial4x4 nr %s' % sol16.pk)
                sol16.processor = self.my_processor
                sol16.save(update_fields=['processor'])

                self.load_partial4x4(sol16)

                try:
                    self._generate_all_quart6()
                    self.find_6x6()
                except KeyboardInterrupt:
                    # warning for closed stdout!
                    sol16.processor = 0
                    sol16.save(update_fields=['processor'])
                    do_quit = True
                else:
                    sol16.is_processed = True
                    sol16.save(update_fields=['is_processed'])

                # clean up
                Quart6.objects.filter(processor=self.my_processor).delete()
            else:
                self.stdout.write('[INFO] Waiting for new 4x4 (press Ctrl+C to abort)')
                time.sleep(60)
        # while

        # warning for closed stdout..
        self.stdout.write('[WARNING] Interrupted')

# end of file
