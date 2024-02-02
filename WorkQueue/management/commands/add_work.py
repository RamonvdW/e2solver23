# -*- coding: utf-8 -*-

#  Copyright (c) 2024 Ramon van der Winkel.
#  All rights reserved.
#  Licensed under BSD-3-Clause-Clear. See LICENSE file for details.

from django.core.management.base import BaseCommand
from WorkQueue.models import Work


class Command(BaseCommand):

    help = "Add job definition to the work queue"

    supported_job_types = ('eval_loc_1', 'eval_loc_4', 'eval_loc_9', 'eval_loc_16', 'eval_line1', 'eval_line2',
                           'eval_claims', 'scan1')

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def add_arguments(self, parser):
        parser.add_argument('processor', type=int, help='For which processor instance?')
        parser.add_argument('job', type=str, help='Job type: eval_loc_1/4/9/16, eval_line, eval_claims')
        parser.add_argument('priority', type=int, help='Priority (lower numbers are handled first)')
        parser.add_argument('location', type=int, help='Location (1..64) / side (1..4)')
        parser.add_argument('--limit', default=0, type=int, help='Optional limit (1..289)')

    def handle(self, *args, **options):
        processor = options['processor']
        job_type = options['job']
        priority = options['priority']
        location = options['location']
        limit = options['limit']

        if job_type not in self.supported_job_types:
            self.stderr.write('[ERROR] Unsupported job_type %s' % repr(job_type))
            self.stdout.write('[INFO] Please choose from: %s' % repr(self.supported_job_types))
            return

        if job_type == 'scan1':
            job_type = 'eval_loc_1'
            self.stdout.write('[INFO] Adding work: %s %s %s {1..64}' % (processor, job_type, priority))

            bulk = list()
            for loc in range(1, 64+1):
                bulk.append(Work(processor=processor, job_type=job_type, priority=priority, location=loc))
            # for

            Work.objects.bulk_create(bulk)
        else:
            limit_str = ''
            if limit > 0:
                limit_str = ' --limit %s' % limit
            self.stdout.write(
                '[INFO] Adding work: %s %s %s %s%s' % (processor, job_type, priority, location, limit_str))

            Work(processor=processor, job_type=job_type, priority=priority, location=location, limit=limit).save()


# end of file
