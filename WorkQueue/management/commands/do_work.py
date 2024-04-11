# -*- coding: utf-8 -*-

#  Copyright (c) 2023-2024 Ramon van der Winkel.
#  All rights reserved.
#  Licensed under BSD-3-Clause-Clear. See LICENSE file for details.

from django.db import transaction
from django.core import management
from django.utils import timezone
from django.core.management.base import BaseCommand
from Pieces2x2.models import EvalProgress
from WorkQueue.models import Work, ProcessorUsedPieces
import datetime
import time
import io


class Command(BaseCommand):

    help = "Execute work from the work queue"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def add_arguments(self, parser):
        parser.add_argument('worker_nr', type=int, help='Instance number')

    @staticmethod
    def _get_stamp():
        return timezone.localtime(timezone.now()).strftime('%Y-%m-%d %H:%M:%S')

    def _run_command(self, *args):

        args = [arg for arg in args if arg is not None]

        self.stdout.write('[INFO] Running command %s' % " ".join(args))

        f1 = io.StringIO()
        f2 = io.StringIO()

        bad = False
        try:
            management.call_command(*args, stderr=f1, stdout=f2)
        except SystemExit as exc:
            self.stdout.write('[WARNING] %s for command %s' % (str(exc), repr(args)))
            bad = True

        msg = f2.getvalue() + '\n' + f1.getvalue()
        for line in msg.split('\n'):
            if line:
                self.stdout.write('  ' + line)
        # for

        return bad

    def _do_work(self, work):
        self.stdout.write('[INFO] Start on work pk=%s at %s' % (work.pk, self._get_stamp()))

        bad = True
        do_later = False
        nop = None
        if work.nop:
            nop = '--nop'

        if work.job_type == 'eval_loc_1':
            bad = self._run_command('eval_loc_1', str(work.processor), str(work.location), nop)

        elif work.job_type == 'eval_loc_4':
            bad = self._run_command('eval_loc_4', str(work.processor), str(work.location), nop)

        elif work.job_type == 'eval_loc_9':
            limit_arg = None
            if work.limit:
                limit_arg = '--limit=%s' % work.limit
            bad = self._run_command('eval_loc_9', str(work.processor), str(work.location), limit_arg, nop)

        elif work.job_type == 'eval_loc_16':
            bad = self._run_command('eval_loc_16', str(work.processor), str(work.location), nop)

        elif work.job_type == 'eval_line1':
            bad = self._run_command('eval_line1', str(work.processor), str(work.location), nop)

        elif work.job_type == 'eval_line2':
            bad = self._run_command('eval_line2', str(work.processor), str(work.location), nop)

        elif work.job_type == 'eval_line3':
            bad = self._run_command('eval_line3', str(work.processor), str(work.location), nop)

        elif work.job_type == 'eval_claims':
            bad = self._run_command('eval_claims', str(work.processor))

        elif work.job_type == 'make_ring2':
            bad = self._run_command('make_ring2', str(work.processor))

        else:
            self.stdout.write('[ERROR] Unsupported job_type %s in work pk=%s' % (repr(work.job_type), work.pk))

        if do_later:
            self.stdout.write('[INFO] Delaying work pk=%s with 5 minutes' % work.pk)
            work.start_after = timezone.now() + datetime.timedelta(minutes=5)
            work.doing = False
            work.save(update_fields=['start_after', 'doing'])

        elif bad:
            self.stdout.write('[WARNING] Failed to perform work pk=%s' % work.pk)
            # leave doing=True to prevent immediate repeat pick-up

        else:
            self.stdout.write('[INFO] Finished on work pk=%s at %s' % (work.pk, self._get_stamp()))
            work.doing = False
            work.done = True
            work.when_done = timezone.now()
            work.save()

    def _find_work(self, only_eval_loc_1, no_eval_loc_4):
        # find some work to pick up
        now = timezone.now()
        do_work = None

        with transaction.atomic():
            qset = (Work
                    .objects
                    .select_for_update()
                    .filter(done=False,
                            doing=False)
                    .exclude(start_after__gt=now)
                    .order_by('priority',       # lowest first = highest priority
                              'when_added'))    # oldest first

            if only_eval_loc_1:
                # avoid concurrent claiming by serializing eval_loc_1 on one worker
                qset = qset.filter(job_type='eval_loc_1')
            else:
                qset = qset.exclude(job_type='eval_loc_1')

            if no_eval_loc_4:
                qset = qset.exclude(job_type='eval_loc_4')

            for work in qset.all():
                used = ProcessorUsedPieces.objects.filter(processor=work.processor).first()
                if used:
                    if used.reached_dead_end:
                        work.delete()
                        continue    # next job

                if work.job_type == 'make_ring2':
                    if Work.objects.filter(processor=work.processor, done=False).count() > 1:
                        self.stdout.write('[WARNING] Not starting make_ring2 due to other work')
                        continue    # next job

                if work:
                    work.doing = True
                    work.save(update_fields=['doing'])
                    do_work = work
                    break   # from the for
            # for
        # atomic

        if do_work:
            self._do_work(work)
        else:
            self.stdout.write('[INFO] Waiting for more work')
            if only_eval_loc_1:
                time.sleep(2)
            else:
                time.sleep(10)

    def handle(self, *args, **options):
        worker_nr = options['worker_nr']
        self.stdout.write('[INFO] Worker number: %s' % worker_nr)

        if worker_nr == 0:
            # restart all ongoing work
            Work.objects.filter(done=False, doing=True).update(doing=False)
            EvalProgress.objects.all().delete()
            return

        # keep one worker available for small tasks
        only_eval_loc_1 = worker_nr == 1
        no_eval_loc_4 = worker_nr > 10

        while worker_nr:
            self._find_work(only_eval_loc_1, no_eval_loc_4)
            time.sleep(0.1)
        # while

# end of file
