# -*- coding: utf-8 -*-

#  Copyright (c) 2024 Ramon van der Winkel.
#  All rights reserved.
#  Licensed under BSD-3-Clause-Clear. See LICENSE file for details.

from django.utils import timezone
from django.core.management.base import BaseCommand
from BasePieces.hints import ALL_HINT_NRS
from BasePieces.models import BasePiece
from Pieces2x2.helpers import calc_segment
from Pieces2x2.models import Piece2x2, TwoSide, TwoSideOptions, EvalProgress
from Solutions.models import Solution8x8
import time


class Command(BaseCommand):

    help = "ZigZag generator"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.path = (57,
                     49, 58, -50,
                     50, 59, -51, 41, -42,
                     33, 42, -34, 51, -43, 60, -52,
                     25, 34, -26, 43, -35, 52, -44, 61, -53,
                     17, 26, -18, 35, -27, 44, -36, 53, -45, 62, -54,
                     9, 18, -10, 27, -19, 36, -28, 45, -37, 54, -46, 63, -55,
                     1, 10, -2, 19, -11, 28, -20, 37, -29, 46, -38, 55, -47, 64, -56,
                     2, 11, -3, 20, -12, 29, -21, 38, -30, 47, -39, 56, -48,
                     3, 12, -4, 21, -13, 30, -22, 39, -31, 48, -40,
                     4, 13, -5, 22, -14, 31, -23, 40, -32,
                     5, 14, -6, 23, -15, 32, -24,
                     6, 15, -7, 24, -16,
                     7, 16, -8,
                     8)

        self.exp_side3 = dict()     # [loc] = side3
        self.exp_side4 = dict()     # [loc] = side4

        self.exp_sides1 = dict()    # [loc] = sides1
        self.exp_sides2 = dict()    # [loc] = sides2
        self.exp_sides3 = dict()    # [loc] = sides3
        self.exp_sides4 = dict()    # [loc] = sides4

        self.left = dict()          # [loc] = count

        self.border = TwoSide.objects.get(two_sides='XX').nr

        self.nr2base = dict()
        for p1x1 in BasePiece.objects.all():
            self.nr2base[p1x1.nr] = p1x1
        # for

        self.solution = Solution8x8(based_on_6x6=0)
        for loc in range(1, 64+1):
            loc_str = 'nr%s' % loc
            setattr(self.solution, loc_str, 0)
        # for

        # 1..60 = borders + corners
        self.unused = list(range(1, 256+1))
        for nr in ALL_HINT_NRS:
            self.unused.remove(nr)
        # for

        self.used = []
        self.progress = None
        self.prev_tick = time.monotonic()

    def add_arguments(self, parser):
        parser.add_argument('--clean', action='store_true')

    def _load_options(self, processor_nr):
        # get the segment limitations for some key locations
        qset = TwoSideOptions.objects.filter(processor=processor_nr)

        seg = calc_segment(10, 4)
        options = list(qset.filter(segment=seg).values_list('two_side', flat=True))
        self.exp_sides2[9] = options

        seg = calc_segment(10, 3)
        options = list(qset.filter(segment=seg).values_list('two_side', flat=True))
        self.exp_sides1[18] = options

        seg = calc_segment(15, 4)
        options = list(qset.filter(segment=seg).values_list('two_side', flat=True))
        self.exp_sides2[14] = options

        seg = calc_segment(15, 3)
        options = list(qset.filter(segment=seg).values_list('two_side', flat=True))
        self.exp_sides1[23] = options

        seg = calc_segment(50, 3)
        options = list(qset.filter(segment=seg).values_list('two_side', flat=True))
        self.exp_sides1[58] = options

        seg = calc_segment(50, 4)
        options = list(qset.filter(segment=seg).values_list('two_side', flat=True))
        self.exp_sides2[49] = options

        seg = calc_segment(55, 3)
        options = list(qset.filter(segment=seg).values_list('two_side', flat=True))
        self.exp_sides1[63] = options

        seg = calc_segment(55, 4)
        options = list(qset.filter(segment=seg).values_list('two_side', flat=True))
        self.exp_sides2[54] = options

    def _make_used(self, p_nrs: tuple | list):
        for nr in p_nrs:
            self.unused.remove(nr)
        # for
        self.used.extend(p_nrs)

    def _make_unused(self, p_nrs: tuple | list):
        for nr in p_nrs:
            self.used.remove(nr)
        # for
        self.unused.extend(p_nrs)

    def _save_solution(self):
        self.solution.pk = None
        self.solution.save()
        self.stdout.write('[INFO] Saved Solution8x8 with pk=%s' % self.solution.pk)
        import sys
        sys.exit(1)

    def _make_qset(self, loc):
        qset = Piece2x2.objects.all()

        if loc == 10:
            qset = qset.filter(nr1=208)
        else:
            qset = qset.filter(nr1__in=self.unused)

        if loc in (15, 36):
            if loc == 15:
                qset = qset.filter(nr2=255)
            else:
                qset = qset.filter(nr2=139)
        else:
            qset = qset.filter(nr2__in=self.unused)

        if loc == 50:
            qset = qset.filter(nr3=181)
        else:
            qset = qset.filter(nr3__in=self.unused)

        if loc == 55:
            qset = qset.filter(nr4=249)
        else:
            qset = qset.filter(nr4__in=self.unused)

        if loc <= 8:
            # print('loc %s: side1=%s' % (loc, self.border))
            qset = qset.filter(side1=self.border)
        else:
            try:
                sides1 = self.exp_sides1[loc]
            except KeyError:
                pass
            else:
                # print('loc %s: sides1 in %s' % (loc, len(sides1)))
                qset = qset.filter(side1__in=sides1)

        if loc % 8 == 0:
            # print('loc %s: side2=%s' % (loc, self.border))
            qset = qset.filter(side2=self.border)
        else:
            try:
                sides2 = self.exp_sides2[loc]
            except KeyError:
                pass
            else:
                # print('loc %s: sides2 in %s' % (loc, len(sides2)))
                qset = qset.filter(side2__in=sides2)

        if loc >= 57:
            # print('loc %s: side3=%s' % (loc, self.border))
            qset = qset.filter(side3=self.border)
        else:
            try:
                side3 = self.exp_side3[loc]
            except KeyError:
                try:
                    sides3 = self.exp_sides3[loc]
                except KeyError:
                    pass
                else:
                    # print('loc %s: sides3 in %s' % (loc, len(sides3)))
                    qset = qset.filter(side3__in=sides3)
            else:
                # print('loc %s: side3=%s' % (loc, side3))
                qset = qset.filter(side3=side3)

        if loc % 8 == 1:
            # print('loc %s: side4=%s' % (loc, self.border))
            qset = qset.filter(side4=self.border)
        else:
            try:
                side4 = self.exp_side4[loc]
            except KeyError:
                try:
                    sides4 = self.exp_sides4[loc]
                except KeyError:
                    pass
                else:
                    # print('loc %s: sides4 in %s' % (loc, len(sides4)))
                    qset = qset.filter(side4__in=sides4)
            else:
                # print('loc %s: side4=%s' % (loc, side4))
                qset = qset.filter(side4=side4)

        return qset

    def _iter(self, loc):
        qset = self._make_qset(loc)
        self.left[loc] = qset.count()
        for p in qset.iterator(chunk_size=1000):
            self.left[loc] -= 1
            p_nrs = [nr
                     for nr in (p.nr1, p.nr2, p.nr3, p.nr4)
                     if nr not in ALL_HINT_NRS]
            yield p, p_nrs
        # for

    def _can_solve(self, loc):
        qset = self._make_qset(loc)
        first = qset.first()
        return first is not None

    def _find_path(self, nr):
        if nr >= len(self.path):
            self._save_solution()
            return

        loc = self.path[nr]
        if loc < 0:
            if self._can_solve(-loc):
                self._find_path(nr + 1)
            return

        tick = time.monotonic()
        if tick > self.prev_tick + 5:
            self.prev_tick = tick
            self.stdout.write('[INFO] path %s (loc %s)' % (nr, loc))
            for nr2 in range(nr):
                loc2 = self.path[nr2]
                if loc2 > 0:
                    self.stdout.write('  loc %s: left %s' % (loc2, self.left[loc2]))

        loc_str = 'nr%s' % loc
        for p, p_nrs in self._iter(loc):
            # self.stdout.write('[INFO] Loc %s = %s' % (loc, p.nr))
            setattr(self.solution, loc_str, p.nr)

            if loc - 8 >= 1:
                # self.stdout.write('loc %s.side1 --> loc %s.side3' % (loc, loc-8))
                self.exp_side3[loc - 8] = p.side1
            if loc % 8 > 0:
                # self.stdout.write('loc %s.side2 --> loc %s.side4' % (loc, loc+1))
                self.exp_side4[loc + 1] = p.side2

            self._make_used(p_nrs)
            if loc == 60:
                self._save_solution()

            self._find_path(nr + 1)
            self._make_unused(p_nrs)
        # for

        setattr(self.solution, loc_str, 0)

    def handle(self, *args, **options):

        if options['clean']:
            self.stdout.write('[WARNING] Deleting all Solution8x8')
            Solution8x8.objects.all().delete()
            return

        self._load_options(0)

        self.progress = EvalProgress(
                            eval_size=64,
                            eval_loc=1,
                            processor=0,
                            segment=0,
                            todo_count=0,
                            left_count=0,
                            solve_order="",
                            updated=timezone.now())
        self.progress.save()

        try:
            self._find_path(0)
        except KeyboardInterrupt:
            pass

        self.progress.delete()

# end of file
