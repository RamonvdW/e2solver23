# -*- coding: utf-8 -*-

#  Copyright (c) 2024 Ramon van der Winkel.
#  All rights reserved.
#  Licensed under BSD-3-Clause-Clear. See LICENSE file for details.

from django.core.management.base import BaseCommand
from WorkQueue.models import Work


class Command(BaseCommand):

    help = "Add job definition to the work queue"

    supported_job_types = ('eval_loc_1', 'eval_loc_4', 'eval_loc_9', 'eval_loc_16', 'eval_line', 'eval_claims')

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def add_arguments(self, parser):
        parser.add_argument('processor', nargs=1, type=int, help='For which processor instance?')
        parser.add_argument('job', nargs=1, type=str, help='Job type: eval_loc_1/4/9/16, eval_line, eval_claims')
        parser.add_argument('priority', nargs=1, type=int, help='Priority (lower numbers are handled first)')
        parser.add_argument('location', nargs=1, type=int, help='Location (1..64) / side (1..4)')

    def handle(self, *args, **options):
        processor = options['processor'][0]
        job_type = options['job'][0]
        priority = options['priority'][0]
        location = options['location'][0]

        if job_type not in self.supported_job_types:
            self.stderr.write('[ERROR] Unsupported job_type %s' % repr(job_type))
            self.stdout.write('[INFO] Please choose from: %s' % repr(self.supported_job_types))
            return

        self.stdout.write('[INFO] Adding work: %s %s %s %s' % (processor, job_type, priority, location))

        Work(processor=processor, job_type=job_type, priority=priority, location=location).save()


# end of file
