# -*- coding: utf-8 -*-

#  Copyright (c) 2023-2024 Ramon van der Winkel.
#  All rights reserved.
#  Licensed under BSD-3-Clause-Clear. See LICENSE file for details.

from django.db import transaction
from django.core import management
from django.utils import timezone
from django.core.management.base import BaseCommand
from WorkQueue.models import Work
import time
import io


class Command(BaseCommand):

    help = "Execute work from the work queue"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def add_arguments(self, parser):
        parser.add_argument('worker_nr', nargs=1, type=int, help='Instance number')

    def _run_command(self, *args):
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
        self.stdout.write('[INFO] Start on work pk=%s' % work.pk)

        bad = True

        if work.job_type == 'eval_loc_1':
            bad = self._run_command('eval_loc_1', str(work.processor), str(work.location))

        elif work.job_type == 'eval_loc_4':
            bad = self._run_command('eval_loc_4', str(work.processor), str(work.location))

        elif work.job_type == 'eval_loc_9':
            bad = self._run_command('eval_loc_9', str(work.processor), str(work.location))

        elif work.job_type == 'eval_loc_16':
            bad = self._run_command('eval_loc_16', str(work.processor), str(work.location))

        else:
            self.stdout.write('[ERROR] Unsupported job_type %s in work pk=%s' % (repr(work.job_type), work.pk))

        if bad:
            self.stdout.write('[WARNING] Failed to perform work pk=%s' % work.pk)
            # leave doing=True to prevent immediate repeat pick-up
        else:
            self.stdout.write('[INFO] Finished on work pk=%s' % work.pk)
            work.doing = False
            work.done = True
            work.when_done = timezone.now()
            work.save()

    def _find_work(self):
        # find some work to pick up
        with transaction.atomic():                  # avoid concurrent update
            work = Work.objects.filter(done=False, doing=False).order_by('priority').first()
            if not work:
                self.stdout.write('[INFO] Waiting for more work')
                time.sleep(10)
                return

            work.doing = True
            work.save(update_fields=['doing'])
        # atomic

        self._do_work(work)

    def handle(self, *args, **options):
        worker_nr = options['worker_nr'][0]
        self.stdout.write('[INFO] Worker number: %s' % worker_nr)

        if worker_nr == 1:
            # restart all ongoing work
            Work.objects.filter(done=False, doing=True).update(doing=False)
        else:
            # allow a few seconds for the worker 1 to start and reset all ongoing work
            time.sleep(5)

        while worker_nr:
            self._find_work()
            time.sleep(0.1)

# end of file
