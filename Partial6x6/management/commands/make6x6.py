# -*- coding: utf-8 -*-

#  Copyright (c) 2023 Ramon van der Winkel.
#  All rights reserved.
#  Licensed under BSD-3-Clause-Clear. See LICENSE file for details.

from django.core.management.base import BaseCommand
from BasePieces.hints import ALL_HINT_NRS
from Pieces2x2.models import TwoSides, Piece2x2
from Partial4x4.models import Partial4x4
from Partial6x6.models import Partial6x6, Quart6, P_CORNER, P_BORDER, P_HINTS, NRS_PARTIAL_6X6
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
        self.neighbours = dict()  # [nr] = (side 1, 2, 3, 4 neighbour nrs)
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
                count, freedom, must_have_nrs = self._count_2x2(nr, self.board_unused_nrs)

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

        # skip outer borders
        # skip base pieces reserved for certain positions on the board
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

        todo = qset.count()
        for p in qset:
            # self.stdout.write('%s[%s] %s left' % (" " * len(self.board_solve_order), nr, todo))
            yield p
            todo -= 1

    def load_partial4x4(self, sol):
        for nr in range(1, 64+1):
            self.board[nr] = None
        # for

        # start at 65 to skip all outer border pieces?
        self.board_unused_nrs = [nr for nr in range(1, 256+1) if nr not in ALL_HINT_NRS]

        for nr in (19, 20, 21, 22,
                   27, 28, 29, 30,
                   35, 36, 37, 38,
                   43, 44, 45, 46):

            field_nr = 'nr%s' % nr
            p_nr = getattr(sol, field_nr)
            p = Piece2x2.objects.get(nr=p_nr)
            self._board_fill_nr(nr, p)
        # for

        self.board_gap_count = 64 - 16
        self.board_solve_order = list()     # [nr, nr, ..]
        self.based_on = sol.pk

    def _can_fill_nrs(self, unused_nrs, nrs):
        qset = Piece2x2.objects.all()
        qset = qset.filter(nr1__in=unused_nrs).filter(nr2__in=unused_nrs).filter(nr3__in=unused_nrs).filter(nr4__in=unused_nrs)

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
            for m1 in self._iter_for_nr(nr_m1):
                self._board_fill_nr(nr_m1, m1)

                for m2 in self._iter_for_nr(nr_m2):
                    self._board_fill_nr(nr_m2, m2)

                    unused_nrs = [nr for nr in self.board_unused_nrs if nr > 60]  # skip borders
                    if self._can_fill_nrs(unused_nrs, (nr_chk1, nr_chk2)):
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

        # gap count: 48

        for q1 in self._fill_quart(208, 18, 10, 11, 26, 12, 13, 34):
            # gap count: 43

            for q2 in self._fill_quart(255, 14, 15, 23, 13, 31, 34, 39):
                # gap count: 38

                for q3 in self._fill_quart(249, 47, 55, 54, 39, 53, 52, 34):
                    # gap count: 33

                    for q4 in self._fill_quart(181, 51, 50, 42, 34, 52, None, None):
                        # gap count: 28
                        # complete 6x6
                        self._save_board6x6()
                    # for
                # for
            # for
        # for

    def _generate_quart6(self, nr_p1, nr_c, nr_p2, nr_m1, nr_m2):
        count = 0
        bulk = list()
        for c1 in self._iter_for_nr(nr_c):
            self._board_fill_nr(nr_c, c1)

            for p1 in self._iter_for_nr(nr_p1):
                self._board_fill_nr(nr_p1, p1)

                for p2 in self._iter_for_nr(nr_p2):
                    self._board_fill_nr(nr_p2, p2)

                    if self._can_fill_nrs(self.board_unused_nrs, (nr_m1, nr_m2)):
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
                        if len(bulk) >= 250:
                            count += len(bulk)
                            print('Quart6 type %s: %s' % (nr_c, count))
                            Quart6.objects.bulk_create(bulk)
                            bulk = list()

                    self._board_free_nr(nr_p2)
                # for

                self._board_free_nr(nr_p1)
            # for

            self._board_free_nr(nr_c)
        # for

        if len(bulk) > 0:
            count += len(bulk)
            print('Quart6 type %s: %s' % (nr_c, count))
            Quart6.objects.bulk_create(bulk)

    def _generate_all_quart6(self):
        self._generate_quart6(18, 10, 11, 26, 12)
        self._generate_quart6(14, 15, 23, 13, 31)
        self._generate_quart6(51, 50, 42, 34, 52)
        self._generate_quart6(47, 55, 54, 39, 53)

    def handle(self, *args, **options):

        if options['verbose']:
            self.verbose += 1

        min_4x4_pk = 1
        self.stdout.write('[INFO] my_processor is %s' % self.my_processor)

        do_quit = False
        while not do_quit:
            sol = (Partial4x4
                   .objects
                   .filter(is_processed=False,
                           processor=0,
                           pk__gte=min_4x4_pk)
                   .order_by('pk')      # lowest first
                   .first())

            if sol:
                self.stdout.write('[INFO] Loading Partial4x4 nr %s' % sol.pk)
                sol.processor = self.my_processor
                sol.save(update_fields=['processor'])

                self.load_partial4x4(sol)

                self._save_board6x6()
                sol.processor = 0
                sol.save(update_fields=['processor'])
                do_quit = True

                # try:
                #     self._generate_all_quart6()
                #     self.find_6x6()
                # except KeyboardInterrupt:
                #     # warning for closed stdout!
                #     sol.processor = 0
                #     sol.save(update_fields=['processor'])
                #     do_quit = True
                # else:
                #     sol.is_processed = True
                #     sol.save(update_fields=['is_processed'])

                # clean up
                Quart6.objects.filter(processor=self.my_processor).delete()
            else:
                self.stdout.write('[INFO] Waiting for new 4x4 (press Ctrl+C to abort)')
                time.sleep(60)
        # while

        # warning for closed stdout..
        self.stdout.write('[WARNING] Interrupted')

# end of file
