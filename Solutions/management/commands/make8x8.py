# -*- coding: utf-8 -*-

#  Copyright (c) 2023 Ramon van der Winkel.
#  All rights reserved.
#  Licensed under BSD-3-Clause-Clear. See LICENSE file for details.

from django.core.management.base import BaseCommand
from Pieces2x2.models import TwoSide, Piece2x2
from Partial6x6.models import Partial6x6, NRS_PARTIAL_6X6
from Solutions.models import Solution8x8, NRS_ADDED_IN_8X8
import time


P_CORNER = (1, 8, 57, 64)
P_BORDER = (2, 3, 4, 5, 6, 7,  16, 24, 32, 40, 48, 56,  9, 17, 25, 33, 41, 49,  58, 59, 60, 61, 62, 63)


class Command(BaseCommand):

    help = "Generate 8x8 from Partial6x6"

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
        self.board_freedom = dict()         # [nr] = "statement"
        self.board_gap_count = 0
        self.board_unused_nrs = list()
        self.neighbours = dict()            # [nr] = (side 1, 2, 3, 4 neighbour nrs)
        self._count_freedom_cache = dict()
        self.board_solve_order = list()     # [nr, nr, ..]
        # self.all_unused_nrs = list()
        self.based_on = 0
        self.interval_mins = 15
        self.my_processor = int(time.time() - 946684800.0)     # seconds since Jan 1, 2000

        self._calc_neighbours()

        self.twoside_border = TwoSide.objects.get(two_sides='XX').nr
        self.side_nr2reverse = dict()
        two2nr = dict()
        for two in TwoSide.objects.all():
            two2nr[two.two_sides] = two.nr
        # for
        for two_sides, nr in two2nr.items():
            two_rev = two_sides[1] + two_sides[0]
            rev_nr = two2nr[two_rev]
            self.side_nr2reverse[nr] = rev_nr
        # for

    def _calc_neighbours(self):
        # order of the entries: side 1, 2, 3, 4
        for nr in range(1, 64+1):
            n = list()

            # side 1
            if nr > 8:
                n.append(nr - 8)
            else:
                n.append(0)

            # side 2
            if nr < 64:
                n.append(nr + 1)
            else:
                n.append(0)

            # side 3
            if nr < 57:
                n.append(nr + 8)
            else:
                n.append(0)

            # side 4
            if nr > 1:
                n.append(nr - 1)
            else:
                n.append(0)

            self.neighbours[nr] = tuple(n)
        # for

    def add_arguments(self, parser):
        parser.add_argument('--verbose', action='store_true')
        parser.add_argument('--restart', action='store_true')
        parser.add_argument('--start', nargs=1, help='Start with this Partial8x8 number')

    def _count_2x2(self, nr, unused_nrs):
        # get the sides
        s1, s2, s3, s4 = self._get_sides(nr)
        x1 = x2 = x3 = x4 = None

        if nr in P_CORNER:
            if nr == 1:
                s1 = s4 = self.twoside_border
            elif nr == 8:
                s1 = s2 = self.twoside_border
            elif nr == 57:
                s3 = s4 = self.twoside_border
            else:
                s2 = s3 = self.twoside_border

        elif nr in P_BORDER:
            if nr < 9:
                s1 = self.twoside_border
                x2 = self.twoside_border
                x4 = self.twoside_border

            elif nr > 57:
                x2 = self.twoside_border
                s3 = self.twoside_border
                x4 = self.twoside_border

            elif nr & 1 == 1:
                x1 = self.twoside_border
                x3 = self.twoside_border
                s4 = self.twoside_border

            else:
                x1 = self.twoside_border
                s2 = self.twoside_border
                x3 = self.twoside_border

        else:
            x1 = x2 = x3 = x4 = self.twoside_border

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

        qset = qset.filter(nr1__in=unused_nrs,
                           nr2__in=unused_nrs,
                           nr3__in=unused_nrs,
                           nr4__in=unused_nrs)

        if nr == 60:
            print('[60] s1..4=%s,%s,%s,%s, x1..4=%s,%s,%s,%s' % (s1, s2, s3, s4, x1, x2, x3, x4))

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
            freedom = ""

        return count, freedom, must_have_nrs

    def _count_all(self, work_nr, min_options):
        # start with the neighbours so we can quickly find a dead-end
        nrs = list(self.neighbours[work_nr])
        for nr in NRS_ADDED_IN_8X8:
            if nr not in nrs:           # avoid dupes
                nrs.append(nr)
        # for

        # print('unused_nrs=%s' % repr(self.board_unused_nrs))

        for nr in nrs:
            if nr > 0 and self.board[nr] is None:
                # empty spot on the board
                count, freedom, must_have_nrs = self._count_2x2(nr, self.board_unused_nrs)
                self.board_options[nr] = count
                self.board_freedom[nr] = freedom
                self.board_must_have[nr] = must_have_nrs

                if count < min_options:
                    # found a dead end
                    self.stdout.write(' [%s] less than %s options for %s' % (work_nr, min_options, nr))
                    return True
        # for
        return False

    def _document_gaps(self, sol):
        for nr in range(1, 64+1):
            if nr in NRS_ADDED_IN_8X8:
                p = self.board[nr]
                if not p:
                    # gap

                    # could the number of Piece2x2 that could fit here, not considered unused_nrs
                    count = self.board_options[nr]
                    freedom = self.board_freedom[nr]
                    note = "%s %s" % (count, freedom)
                    note = note[:30]        # avoid database errors

                    field_note = 'note%s' % nr
                    setattr(sol, field_note, note)
        # for

    def _save_board8x8(self):
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

        self.stdout.write('[INFO] Saving board with gap count %s' % self.board_gap_count)

        sol = Solution8x8(
                based_on_6x6=self.based_on)

        for nr in range(1, 64+1):
            field_nr = 'nr%s' % nr
            setattr(sol, field_nr, nrs[nr])
        # for

        self._count_all(1, 0)
        self._document_gaps(sol)

        sol.save()

        self.stdout.write('[INFO] Saved board %s' % sol.pk)

    def _board_free_nr(self, nr):
        p = self.board[nr]
        if p:
            if self.verbose:
                self.stdout.write('-[%s] = %s' % (nr, p.nr))
            self.board[nr] = None
            free_nrs = [nr for nr in (p.nr1, p.nr2, p.nr3, p.nr4)]
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
        x1 = x2 = x3 = x4 = None

        if nr in P_CORNER:
            if nr == 1:
                s1 = s4 = self.twoside_border
            elif nr == 8:
                s1 = s2 = self.twoside_border
            elif nr == 57:
                s3 = s4 = self.twoside_border
            else:
                s2 = s3 = self.twoside_border

        elif nr in P_BORDER:
            if nr < 9:
                s1 = self.twoside_border
                x2 = self.twoside_border
                x4 = self.twoside_border

            elif nr > 57:
                x2 = self.twoside_border
                s3 = self.twoside_border
                x4 = self.twoside_border

            elif nr & 1 == 1:
                x1 = self.twoside_border
                x3 = self.twoside_border
                s4 = self.twoside_border

            else:
                x1 = self.twoside_border
                s2 = self.twoside_border
                x3 = self.twoside_border

        else:
            x1 = x2 = x3 = x4 = self.twoside_border

        qset = Piece2x2.objects.filter(nr__gt=greater_than).order_by('nr')

        reserved_nrs = list()
        for chk_nr in NRS_ADDED_IN_8X8:
            if chk_nr != nr:
                reserved_nrs.extend(self.board_must_have[chk_nr])
        # for

        # skip outer borders
        # skip base pieces reserved for certain positions on the board
        unused_nrs = [nr for nr in self.board_unused_nrs]

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

        qset = qset.filter(nr1__in=unused_nrs,
                           nr2__in=unused_nrs,
                           nr3__in=unused_nrs,
                           nr4__in=unused_nrs)

        # print(qset.explain())

        todo = qset.count()
        for p in qset:
            # print('%s[%s] %s left' % (" " * len(self.board_solve_order), nr, todo))
            yield p
            todo -= 1

    def _try_fill_nr(self, nr, greater_than, min_options):
        for p in self._iter_for_nr(nr, greater_than):
            self._board_fill_nr(nr, p)
            is_dead_end = self._count_all(nr, min_options)
            if not is_dead_end:
                return True     # success
            self._board_free_nr(nr)
        # for
        return False            # failure

    def load_partial6x6(self, sol36):
        for nr in range(1, 64+1):
            self.board[nr] = None
        # for

        self.board_unused_nrs = [nr for nr in range(1, 256+1)]

        for nr in NRS_PARTIAL_6X6:
            field_nr = 'nr%s' % nr
            p_nr = getattr(sol36, field_nr)
            p = Piece2x2.objects.get(nr=p_nr)
            self._board_fill_nr(nr, p)
        # for

        self.board_gap_count = 64 - 36
        self.board_solve_order = list()     # [nr, nr, ..]
        self.based_on = sol36.pk

    def _find_most_critical_nr(self):
        least_count = 0
        least_nr = 0
        for nr in NRS_ADDED_IN_8X8:
            if self.board[nr] is None:
                count = self.board_options[nr]
                if least_nr == 0 or count < least_count:
                    least_count = count
                    least_nr = nr
        # for
        return least_nr, least_count

    def _recurse_find_8x8(self):
        nr, count = self._find_most_critical_nr()
        if count == 0:
            self.stdout.write('[INFO] No solution for nr = %s' % nr)
            return

        self.stdout.write('[DEBUG] Selected [%s] with %s options' % (nr, count))

        for p in self._iter_for_nr(nr, 0):
            self._board_fill_nr(nr, p)
            self._save_board8x8()

            is_dead_end = self._count_all(nr, 1)
            #if not is_dead_end:
            self._recurse_find_8x8()

            self._board_free_nr(nr)
        # for

        self.stdout.write('[INFO] Done with [%s]' % nr)

    def find_8x8(self):
        self._count_all(1, 0)
        self._save_board8x8()
        self._recurse_find_8x8()

    def handle(self, *args, **options):

        if options['verbose']:
            self.verbose += 1

        self.stdout.write('[INFO] my_processor is %s' % self.my_processor)

        if options['restart']:
            self.stdout.write('[WARNING] Restarting processed flags; deleting previous Solution8x8s')
            Solution8x8.objects.all().delete()
            Partial6x6.objects.filter(is_processed=True).update(is_processed=False)
            Partial6x6.objects.exclude(processor=0).update(processor=0)

        if options['start']:
            start = int(options['start'][0])
        else:
            start = 0

        do_quit = False
        while not do_quit:
            sol36 = (Partial6x6
                     .objects
                     .filter(is_processed=False,
                             processor=0,
                             pk__gte=start)
                     .order_by('pk')      # lowest first
                     .first())

            if sol36:
                self.stdout.write('[INFO] Loading Partial6x6 nr %s' % sol36.pk)
                sol36.processor = self.my_processor
                sol36.save(update_fields=['processor'])

                self.load_partial6x6(sol36)

                try:
                    self.find_8x8()
                except KeyboardInterrupt:
                    # warning for closed stdout!
                    sol36.processor = 0
                    sol36.save(update_fields=['processor'])
                    do_quit = True
                else:
                    #sol36.is_processed = True
                    #sol36.save(update_fields=['is_processed'])
                    sol36.processor = 0
                    sol36.save(update_fields=['processor'])
                    do_quit = True

            else:
                self.stdout.write('[INFO] Waiting for new 6x6 (press Ctrl+C to abort)')
                time.sleep(60)
        # while


# end of file
