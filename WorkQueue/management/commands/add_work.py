# -*- coding: utf-8 -*-

#  Copyright (c) 2024 Ramon van der Winkel.
#  All rights reserved.
#  Licensed under BSD-3-Clause-Clear. See LICENSE file for details.

from django.core.management.base import BaseCommand
from WorkQueue.models import Work, ProcessorUsedPieces


class Command(BaseCommand):

    help = "Add job definition to the work queue"

    supported_job_types = ('eval_loc_1', 'eval_loc_4', 'eval_loc_9', 'eval_loc_16',
                           'eval_line1', 'eval_line2', 'eval_line3',
                           'eval_claims',
                           'scan1', 'scan9', 'delayed_scan1',
                           'make_ring2')

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def add_arguments(self, parser):
        parser.add_argument('processor', type=int, help='For which processor instance?')
        parser.add_argument('job', type=str, help='Job type: eval_loc_1/4/9/16, eval_line, eval_claims')
        parser.add_argument('prio_seed', type=int, help='Priority (lower numbers are handled first) or seed')
        parser.add_argument('location', type=int, help='Location (1..64) / side (1..4)')
        parser.add_argument('--limit', default=0, type=int, help='Optional limit (1..289)')
        parser.add_argument('--nop', action='store_true', help='Do not propagate')

    def handle(self, *args, **options):
        processor = options['processor']
        job_type = options['job']
        prio_seed = options['prio_seed']
        location = options['location']
        limit = options['limit']
        nop = options['nop']

        if job_type not in self.supported_job_types:
            self.stderr.write('[ERROR] Unsupported job_type %s' % repr(job_type))
            self.stdout.write('[INFO] Please choose from: %s' % repr(self.supported_job_types))
            return

        if job_type == 'scan1':
            job_type = 'eval_loc_1'
            self.stdout.write('[INFO] Adding work: %s %s %s {1..64}' % (processor, job_type, prio_seed))

            try:
                used = ProcessorUsedPieces.objects.get(processor=processor)
            except ProcessorUsedPieces.DoesNotExist:
                used = ProcessorUsedPieces()

            bulk = []
            for loc in range(1, 64+1):
                loc_str = 'loc%s' % loc
                if getattr(used, loc_str) == 0:
                    work = Work(processor=processor, job_type=job_type, priority=prio_seed,
                                location=loc, nop=nop)
                    bulk.append(work)
            # for
            Work.objects.bulk_create(bulk)
            self.stdout.write('[INFO] Added %s jobs' % len(bulk))

        elif job_type == 'scan9':
            job_type = 'eval_loc_9'
            self.stdout.write(
                '[INFO] Adding work: %s %s %s {1 2 3 4 5 6 14 22 30 38 46 9 17 25 33 41 42 43 44 45}' % (
                    processor, job_type, prio_seed))

            bulk = []
            for loc in (1, 2, 3, 4, 5, 6, 14, 22, 30, 38, 46, 9, 17, 25, 33, 41, 42, 43, 44, 45):
                work = Work(processor=processor, job_type=job_type, priority=prio_seed,
                            location=loc, nop=nop)
                bulk.append(work)
            # for
            Work.objects.bulk_create(bulk)
            self.stdout.write('[INFO] Added %s jobs' % len(bulk))

        elif job_type == 'make_ring2':
            self.stdout.write('[INFO] Adding work: %s %s %s' % (processor, job_type, prio_seed))
            work = Work(processor=processor, job_type=job_type, priority=prio_seed, nop=nop)
            work.save()

        else:
            limit_str = ''
            if limit > 0:
                limit_str = ' --limit %s' % limit
            self.stdout.write(
                '[INFO] Adding work: %s %s %s %s%s' % (processor, job_type, prio_seed, location, limit_str))
            work = Work(processor=processor, job_type=job_type, priority=prio_seed,
                        location=location, limit=limit, nop=nop)
            work.save()


# end of file
