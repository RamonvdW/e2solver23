# -*- coding: utf-8 -*-

#  Copyright (c) 2024 Ramon van der Winkel.
#  All rights reserved.
#  Licensed under BSD-3-Clause-Clear. See LICENSE file for details.

from django.utils import timezone
from django.core.management.base import BaseCommand
from BasePieces.hints import ALL_HINT_NRS
from BasePieces.models import BasePiece
from Pieces2x2.helpers import calc_segment
from Pieces2x2.models import Piece2x2, EvalProgress, TwoSideOptions
from Ring3.models import Ring3
from WorkQueue.models import ProcessorUsedPieces
from WorkQueue.operations import used_note_add
import time


class Command(BaseCommand):

    help = "Generate a Ring3"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.nr2base = dict()
        for p1x1 in BasePiece.objects.all():
            self.nr2base[p1x1.nr] = p1x1
        # for

        self.ring3 = Ring3()
        self.ring3_count = 0

        # 1..60 = borders + corners
        self.unused = list(range(61, 256+1))
        for nr in ALL_HINT_NRS:
            self.unused.remove(nr)
        # for

        self.used = []
        self.progress = None
        self.prev_tick = time.monotonic()

    def add_arguments(self, parser):
        parser.add_argument('processor', type=int, help='Processor to use')
        parser.add_argument('--clean', action='store_true')

    def _load_options(self, processor_nr):
        # get the segment limitations for some key locations
        qset = TwoSideOptions.objects.filter(processor=processor_nr)

        seg = calc_segment(36, 1)
        options = list(qset.filter(segment=seg).values_list('two_side', flat=True))
        self.exp_loc36_sides1 = options
        self.exp_loc28_sides3 = options

        seg = calc_segment(36, 2)
        options = list(qset.filter(segment=seg).values_list('two_side', flat=True))
        self.exp_loc36_sides2 = options
        self.exp_loc37_sides4 = options

        seg = calc_segment(36, 3)
        options = list(qset.filter(segment=seg).values_list('two_side', flat=True))
        self.exp_loc44_sides1 = options

        seg = calc_segment(36, 4)
        options = list(qset.filter(segment=seg).values_list('two_side', flat=True))
        self.exp_loc35_sides2 = options

        seg = calc_segment(10, 2)
        options = list(qset.filter(segment=seg).values_list('two_side', flat=True))
        self.exp_loc11_sides4 = options

        seg = calc_segment(10, 3)
        options = list(qset.filter(segment=seg).values_list('two_side', flat=True))
        self.exp_loc18_sides1 = options

        seg = calc_segment(15, 3)
        options = list(qset.filter(segment=seg).values_list('two_side', flat=True))
        self.exp_loc23_sides1 = options

        seg = calc_segment(15, 4)
        options = list(qset.filter(segment=seg).values_list('two_side', flat=True))
        self.exp_loc14_sides2 = options

        seg = calc_segment(50, 1)
        options = list(qset.filter(segment=seg).values_list('two_side', flat=True))
        self.exp_loc42_sides3 = options

        seg = calc_segment(50, 2)
        options = list(qset.filter(segment=seg).values_list('two_side', flat=True))
        self.exp_loc51_sides4 = options

        seg = calc_segment(55, 1)
        options = list(qset.filter(segment=seg).values_list('two_side', flat=True))
        self.exp_loc47_sides3 = options

        seg = calc_segment(55, 4)
        options = list(qset.filter(segment=seg).values_list('two_side', flat=True))
        self.exp_loc54_sides2 = options

    def _find_best(self):
        if self.ring3.loc22 > 0:
            return 12
        if self.ring3.loc30 > 0:
            return 11
        if self.ring3.loc21 > 0:
            return 10
        if self.ring3.loc38 > 0:
            return 9
        if self.ring3.loc20 > 0:
            return 8
        if self.ring3.loc46 > 0:
            return 7
        if self.ring3.loc19 > 0:
            return 6
        if self.ring3.loc45 > 0:
            return 5
        if self.ring3.loc27 > 0:
            return 4
        if self.ring3.loc44 > 0:
            return 3
        if self.ring3.loc35 > 0:
            return 2
        if self.ring3.loc43 > 0:
            return 1
        return 0

    def _report_progress(self):
        tick = time.monotonic()
        if tick - self.prev_tick > 60:
            self.prev_tick = tick
            msg = 'Best: %s / 12' % self._find_best()
            self.progress.solve_order = msg
            self.progress.save(update_fields=['solve_order'])
            self.stdout.write(msg)

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

    def _save_ring3(self):
        self.ring3.pk = None
        self.ring3.save()
        self.ring3_count += 1
        self.stdout.write('[INFO] Saved Ring3 with pk=%s' % self.ring3.pk)

    def _find_loc20(self):
        print('loc20: hoi!')
        self._save_ring3()
        import sys
        sys.exit(1)

    def _check_loc47b(self):
        qset = Piece2x2.objects.filter(has_hint=False,
                                       nr1__in=self.unused, nr2__in=self.unused,
                                       nr3__in=self.unused, nr4__in=self.unused,
                                       side3__in=self.exp_loc47b_sides3,
                                       side4=self.exp_loc47_s4)
        if qset.first() is None:
            return False

        self.exp_loc39_sides3 = list(qset.values_list('side1', flat=True))
        return True

    def _check_loc53b(self):
        qset = Piece2x2.objects.filter(has_hint=False,
                                       nr1__in=self.unused, nr2__in=self.unused,
                                       nr3__in=self.unused, nr4__in=self.unused,
                                       side1=self.exp_loc53_s1,
                                       side2__in=self.exp_loc53b_sides2,
                                       side4__in=self.exp_loc53_sides4)
        if qset.first() is None:
            return False

        return True

    def _check_loc54b(self):
        qset = Piece2x2.objects.filter(has_hint=False,
                                       nr1__in=self.unused, nr2__in=self.unused,
                                       nr3__in=self.unused, nr4__in=self.unused,
                                       side1=self.exp_loc54_s1,
                                       side2__in=self.exp_loc54b_sides2,
                                       side4__in=self.exp_loc54_sides4)
        if qset.first() is None:
            return False

        self.exp_loc53b_sides2 = list(qset.values_list('side4', flat=True))
        return True

    def _check_loc55(self):
        qset = Piece2x2.objects.filter(has_hint=True,
                                       nr1__in=self.unused,
                                       nr2__in=self.unused,
                                       nr3__in=self.unused,
                                       nr4=249,
                                       side1__in=self.exp_loc55_sides1,
                                       side4__in=self.exp_loc55_sides4)
        if qset.first() is None:
            return False

        self.exp_loc47b_sides3 = list(qset.values_list('side1', flat=True))
        self.exp_loc54b_sides2 = list(qset.values_list('side4', flat=True))
        return True

    def _check_loc47a(self):
        qset = Piece2x2.objects.filter(has_hint=False,
                                       nr1__in=self.unused, nr2__in=self.unused,
                                       nr3__in=self.unused, nr4__in=self.unused,
                                       side3__in=self.exp_loc47_sides3,
                                       side4=self.exp_loc47_s4)
        if qset.first() is None:
            return False

        self.exp_loc55_sides1 = list(qset.values_list('side3', flat=True))
        return True

    def _check_loc54a(self):
        qset = Piece2x2.objects.filter(has_hint=False,
                                       nr1__in=self.unused, nr2__in=self.unused,
                                       nr3__in=self.unused, nr4__in=self.unused,
                                       side1=self.exp_loc54_s1,
                                       side2__in=self.exp_loc54_sides2,
                                       side4__in=self.exp_loc54_sides4)
        if qset.first() is None:
            return False

        self.exp_loc55_sides4 = list(qset.values_list('side2', flat=True))
        return True

    def _find_loc46(self):
        qset = Piece2x2.objects.filter(has_hint=False,
                                       nr1__in=self.unused, nr2__in=self.unused,
                                       nr3__in=self.unused, nr4__in=self.unused,
                                       side4=self.exp_loc46_s4)
        for p in qset.iterator(chunk_size=100):
            self.ring3.loc46 = p.nr
            self.exp_loc38_s3 = p.side1
            self.exp_loc47_s4 = p.side2
            self.exp_loc54_s1 = p.side3
            p_nrs = (p.nr1, p.nr2, p.nr3, p.nr4)
            self._make_used(p_nrs)
            if self._check_loc54a() and self._check_loc47a() and self._check_loc55():
                if self._check_loc54b() and self._check_loc53b() and self._check_loc47b():
                    self._find_loc20()
            self._make_unused(p_nrs)
        # for

    def _check_loc11b(self):
        qset = Piece2x2.objects.filter(has_hint=False,
                                       nr1__in=self.unused, nr2__in=self.unused,
                                       nr3__in=self.unused, nr4__in=self.unused,
                                       side3=self.exp_loc11_s3,
                                       side4__in=self.exp_loc11b_sides4)
        if qset.first() is None:
            return False

        self.exp_loc12_sides4 = list(qset.values_list('side2', flat=True))
        return True

    def _check_loc10(self):
        qset = Piece2x2.objects.filter(has_hint=True,
                                       nr1=208,
                                       nr2__in=self.unused,
                                       nr3__in=self.unused,
                                       nr4__in=self.unused,
                                       side1__in=self.exp_loc10_sides3,
                                       side2__in=self.exp_loc10_sides4)
        if qset.first() is None:
            return False

        self.exp_loc11b_sides4 = list(qset.values_list('side2', flat=True))
        return True

    def _check_loc11a(self):
        qset = Piece2x2.objects.filter(has_hint=False,
                                       nr1__in=self.unused, nr2__in=self.unused,
                                       nr3__in=self.unused, nr4__in=self.unused,
                                       side3=self.exp_loc11_s3,
                                       side4__in=self.exp_loc11_sides4)
        if qset.first() is None:
            return False

        self.exp_loc10_sides4 = list(qset.values_list('side2', flat=True))
        return True

    def _check_loc26b(self):
        qset = Piece2x2.objects.filter(has_hint=False,
                                       nr1__in=self.unused, nr2__in=self.unused,
                                       nr3__in=self.unused, nr4__in=self.unused,
                                       side1__in=self.exp_loc26b_sides1,
                                       side2=self.exp_loc26_s2,
                                       side3__in=self.exp_loc26_sides3)
        return qset.first() is not None

    def _check_loc18(self):
        qset = Piece2x2.objects.filter(has_hint=False,
                                       nr1__in=self.unused, nr2__in=self.unused,
                                       nr3__in=self.unused, nr4__in=self.unused,
                                       side1__in=self.exp_loc18_sides1,
                                       side2=self.exp_loc18_s2,
                                       side3__in=self.exp_loc18_sides3)
        if qset.first() is None:
            return False

        self.exp_loc10_sides3 = list(qset.values_list('side1', flat=True))
        self.exp_loc26b_sides1 = list(qset.values_list('side3', flat=True))
        return True

    def _find_loc19(self):
        qset = Piece2x2.objects.filter(has_hint=False,
                                       nr1__in=self.unused, nr2__in=self.unused,
                                       nr3__in=self.unused, nr4__in=self.unused,
                                       side3=self.exp_loc19_s3)
        for p in qset.iterator(chunk_size=100):
            self.ring3.loc19 = p.nr
            self.exp_loc11_s3 = p.side1
            self.exp_loc20_s4 = p.side2
            self.exp_loc18_s2 = p.side4
            p_nrs = (p.nr1, p.nr2, p.nr3, p.nr4)
            self._make_used(p_nrs)
            if self._check_loc18() and self._check_loc26b() and self._check_loc11a() and self._check_loc10():
                if self._check_loc11b():
                    self._find_loc46()
            self._make_unused(p_nrs)
        # for

    def _check_loc36c(self):
        qset = Piece2x2.objects.filter(has_hint=False,
                                       nr1__in=self.unused, nr2__in=self.unused,
                                       nr3__in=self.unused, nr4__in=self.unused,
                                       side1__in=self.exp_loc36_sides1,
                                       side2__in=self.exp_loc36c_sides2,
                                       side3=self.exp_loc36b_s3,
                                       side4=self.exp_loc36_s4)
        if qset.first() is None:
            return False

        self.exp_loc28_sides3 = list(qset.values_list('side1', flat=True))
        self.exp_loc37_sides4 = list(qset.values_list('side2', flat=True))
        return True

    def _check_loc37a(self):
        qset = Piece2x2.objects.filter(has_hint=False,
                                       nr1__in=self.unused, nr2__in=self.unused,
                                       nr3__in=self.unused, nr4__in=self.unused,
                                       side3=self.exp_loc37_s3,
                                       side4__in=self.exp_loc37_sides4)
        if qset.first() is None:
            return False

        self.exp_loc38_sides4 = list(qset.values_list('side2', flat=True))
        self.exp_loc36c_sides2 = list(qset.values_list('side4', flat=True))
        return True

    def _check_loc53a(self):
        qset = Piece2x2.objects.filter(has_hint=False,
                                       nr1__in=self.unused, nr2__in=self.unused,
                                       nr3__in=self.unused, nr4__in=self.unused,
                                       side1=self.exp_loc53_s1,
                                       side4__in=self.exp_loc53_sides4)
        if qset.first() is None:
            return False

        self.exp_loc54_sides4 = list(qset.values_list('side2', flat=True))
        return True

    def _find_loc45(self):
        qset = Piece2x2.objects.filter(has_hint=False,
                                       nr1__in=self.unused, nr2__in=self.unused,
                                       nr3__in=self.unused, nr4__in=self.unused,
                                       side4=self.exp_loc45_s4)
        for p in qset.iterator(chunk_size=100):
            self.ring3.loc45 = p.nr
            self.exp_loc37_s3 = p.side1
            self.exp_loc46_s4 = p.side2
            self.exp_loc53_s1 = p.side3
            p_nrs = (p.nr1, p.nr2, p.nr3, p.nr4)
            self._make_used(p_nrs)
            if self._check_loc53a() and self._check_loc37a() and self._check_loc36c():
                self._find_loc19()
            self._make_unused(p_nrs)
        # for

    def _check_loc28a(self):
        qset = Piece2x2.objects.filter(has_hint=False,
                                       nr1__in=self.unused, nr2__in=self.unused,
                                       nr3__in=self.unused, nr4__in=self.unused,
                                       side3__in=self.exp_loc28_sides3,
                                       side4=self.exp_loc28_s4)
        if qset.first() is None:
            return False

        self.exp_loc20_sides3 = list(qset.values_list('side1', flat=True))
        self.exp_loc29_sides4 = list(qset.values_list('side2', flat=True))
        self.exp_loc36c_sides1 = list(qset.values_list('side3', flat=True))
        return True

    def _check_loc26a(self):
        qset = Piece2x2.objects.filter(has_hint=False,
                                       nr1__in=self.unused, nr2__in=self.unused,
                                       nr3__in=self.unused, nr4__in=self.unused,
                                       side2=self.exp_loc26_s2,
                                       side3__in=self.exp_loc26_sides3)
        if qset.first() is None:
            return False

        self.exp_loc18_sides3 = list(qset.values_list('side1', flat=True))
        return True

    def _find_loc27(self):
        qset = Piece2x2.objects.filter(has_hint=False,
                                       nr1__in=self.unused, nr2__in=self.unused,
                                       nr3__in=self.unused, nr4__in=self.unused,
                                       side3=self.exp_loc27_s3)
        for p in qset.iterator(chunk_size=100):
            self.ring3.loc27 = p.nr
            self.exp_loc19_s3 = p.side1
            self.exp_loc28_s4 = p.side2
            self.exp_loc26_s2 = p.side4
            p_nrs = (p.nr1, p.nr2, p.nr3, p.nr4)
            self._make_used(p_nrs)
            if self._check_loc28a() and self._check_loc26a():
                self._find_loc45()
            self._make_unused(p_nrs)
        # for

    def _check_loc36b(self):
        qset = Piece2x2.objects.filter(has_hint=False,
                                       nr1__in=self.unused, nr2__in=self.unused,
                                       nr3__in=self.unused, nr4__in=self.unused,
                                       side1__in=self.exp_loc36_sides1,
                                       side2__in=self.exp_loc36_sides2,
                                       side3=self.exp_loc36b_s3,
                                       side4=self.exp_loc36_s4)
        if qset.first() is None:
            return False

        self.exp_loc28_sides3 = list(qset.values_list('side1', flat=True))
        self.exp_loc37_sides4 = list(qset.values_list('side2', flat=True))
        return True

    def _check_loc52(self):
        qset = Piece2x2.objects.filter(has_hint=False,
                                       nr1__in=self.unused, nr2__in=self.unused,
                                       nr3__in=self.unused, nr4__in=self.unused,
                                       side1=self.exp_loc52_s1,
                                       side4__in=self.exp_loc52_sides4)
        if qset.first() is None:
            return False

        self.exp_loc53_sides4 = list(qset.values_list('side2', flat=True))
        return True

    def _find_loc44(self):
        qset = Piece2x2.objects.filter(has_hint=False,
                                       nr1__in=self.unused, nr2__in=self.unused,
                                       nr3__in=self.unused, nr4__in=self.unused,
                                       side1__in=self.exp_loc44_sides1,
                                       side4=self.exp_loc44_s4)
        for p in qset.iterator(chunk_size=100):
            self.ring3.loc44 = p.nr
            self.exp_loc36b_s3 = p.side1
            self.exp_loc45_s4 = p.side2
            self.exp_loc52_s1 = p.side3
            p_nrs = (p.nr1, p.nr2, p.nr3, p.nr4)
            self._make_used(p_nrs)
            if self._check_loc36b() and self._check_loc52():
                self._find_loc27()
            self._make_unused(p_nrs)
        # for

    def _check_loc34(self):
        qset = Piece2x2.objects.filter(has_hint=False,
                                       nr1__in=self.unused, nr2__in=self.unused,
                                       nr3__in=self.unused, nr4__in=self.unused,
                                       side2=self.exp_loc34_s2,
                                       side3__in=self.exp_loc34_sides3)
        if qset.first() is None:
            return False

        self.exp_loc26_sides3 = list(qset.values_list('side1', flat=True))
        return True

    def _check_loc36a(self):
        qset = Piece2x2.objects.filter(has_hint=False,
                                       nr1__in=self.unused, nr2__in=self.unused,
                                       nr3__in=self.unused, nr4__in=self.unused,
                                       side1__in=self.exp_loc36_sides1,
                                       side2__in=self.exp_loc36_sides2,
                                       side4=self.exp_loc36_s4)
        if qset.first() is None:
            return False

        self.exp_loc44_sides1 = list(qset.values_list('side3', flat=True))
        return True

    def _find_loc35(self):
        qset = Piece2x2.objects.filter(has_hint=False,
                                       nr1__in=self.unused, nr2__in=self.unused,
                                       nr3__in=self.unused, nr4__in=self.unused,
                                       side2__in=self.exp_loc35_sides2,
                                       side3=self.exp_loc35_s3)
        for p in qset.iterator(chunk_size=100):
            self.ring3.loc35 = p.nr
            self.exp_loc27_s3 = p.side1
            self.exp_loc36_s4 = p.side2
            self.exp_loc34_s2 = p.side4
            p_nrs = (p.nr1, p.nr2, p.nr3, p.nr4)
            self._make_used(p_nrs)
            if self._check_loc36a() and self._check_loc34():
                self._find_loc44()
            self._make_unused(p_nrs)
        # for

    def _check_loc42(self):
        qset = Piece2x2.objects.filter(has_hint=False,
                                       nr1__in=self.unused, nr2__in=self.unused,
                                       nr3__in=self.unused, nr4__in=self.unused,
                                       side2=self.exp_loc42_s2,
                                       side3__in=self.exp_loc42_sides3)
        if qset.first() is None:
            return False

        self.exp_loc34_sides3 = list(qset.values_list('side1', flat=True))
        self.exp_loc50_sides1 = list(qset.values_list('side3', flat=True))
        return True

    def _check_loc51(self):
        qset = Piece2x2.objects.filter(has_hint=False,
                                       nr1__in=self.unused, nr2__in=self.unused,
                                       nr3__in=self.unused, nr4__in=self.unused,
                                       side1=self.exp_loc51_s1,
                                       side4__in=self.exp_loc51_sides4)
        if qset.first() is None:
            return False

        self.exp_loc52_sides4 = list(qset.values_list('side2', flat=True))
        self.exp_loc50_sides2 = list(qset.values_list('side4', flat=True))
        return True

    def _check_loc50(self):
        p = Piece2x2.objects.filter(has_hint=True,
                                    nr1__in=self.unused,
                                    nr2__in=self.unused,
                                    nr3=181,
                                    nr4__in=self.unused,
                                    side1__in=self.exp_loc50_sides1,
                                    side2__in=self.exp_loc50_sides2).first()
        return p is not None

    def _find_loc43(self):
        qset = Piece2x2.objects.filter(has_hint=False,
                                       nr1__in=self.unused, nr2__in=self.unused,
                                       nr3__in=self.unused, nr4__in=self.unused)
        left = qset.count()
        for p in qset.iterator(chunk_size=100):
            self.stdout.write('loc43: %s left' % left)
            left -= 1
            self.progress.left_count = min(left, 32767)
            self.progress.updated = timezone.now()
            self.progress.save(update_fields=['left_count', 'updated'])

            self.ring3.loc43 = p.nr
            self.exp_loc35_s3 = p.side1
            self.exp_loc44_s4 = p.side2
            self.exp_loc51_s1 = p.side3
            self.exp_loc42_s2 = p.side4
            p_nrs = (p.nr1, p.nr2, p.nr3, p.nr4)
            self._make_used(p_nrs)
            if self._check_loc42() and self._check_loc51() and self._check_loc50():
                self._find_loc35()
            self._make_unused(p_nrs)
        # for

    def handle(self, *args, **options):

        if options['clean']:
            self.stdout.write('[WARNING] Deleting all Ring3')
            Ring3.objects.all().delete()
            return

        processor_nr = options['processor']
        try:
            processor = ProcessorUsedPieces.objects.get(processor=processor_nr)
        except ProcessorUsedPieces.DoesNotExist:
            self.stderr.write('[ERROR] Could not find processor %s' % processor_nr)
            return

        self._load_options(processor_nr)

        self.progress = EvalProgress(
                            eval_size=12,
                            eval_loc=43,
                            processor=processor_nr,
                            segment=0,
                            todo_count=0,
                            left_count=0,
                            solve_order="",
                            updated=timezone.now())
        self.progress.save()

        try:
            self._find_loc43()
        except KeyboardInterrupt:
            pass
        else:
            if self.ring3_count > 0:
                self.stdout.write('[INFO] Generated %s Ring2' % self.ring3_count)
                used_note_add(processor_nr, "Generated %s Ring2" % self.ring3_count)
            else:
                used_note_add(processor_nr, 'No Ring3 (best: %s / 12)' % self._find_best())
                processor.reached_dead_end = True
                processor.save(update_fields=['reached_dead_end'])

            print('[INFO] Best: %s / 12' % self._find_best())

        self.progress.delete()


# end of file
