# -*- coding: utf-8 -*-

#  Copyright (c) 2023-2024 Ramon van der Winkel.
#  All rights reserved.
#  Licensed under BSD-3-Clause-Clear. See LICENSE file for details.

from django.core.management.base import BaseCommand
from WorkQueue.models import Work


class Command(BaseCommand):

    help = "Remove duplicate work orders"

    def handle(self, *args, **options):

        for prio, loc, job in Work.objects.filter(done=False, doing=False).distinct('priority', 'location', 'job_type').values_list('priority', 'location', 'job_type'):
            count = Work.objects.filter(done=False, doing=False, priority=prio, location=loc, job_type=job).count()
            if count > 1:
                self.stdout.write('[INFO] Found duplicates with priority=%s, location=%s, job_type=%s' % (prio, loc, repr(job)))
        # for

# end of file
