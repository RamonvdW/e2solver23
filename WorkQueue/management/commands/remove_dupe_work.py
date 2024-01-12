# -*- coding: utf-8 -*-

#  Copyright (c) 2023-2024 Ramon van der Winkel.
#  All rights reserved.
#  Licensed under BSD-3-Clause-Clear. See LICENSE file for details.

from django.core.management.base import BaseCommand
from WorkQueue.models import Work


class Command(BaseCommand):

    help = "Remove duplicate work orders"

    def handle(self, *args, **options):

        for processor, loc, job in (Work
                                    .objects
                                    .filter(done=False)
                                    .distinct('processor',
                                              'location',
                                              'job_type')
                                    .values_list('processor', 'location', 'job_type')):

            qset = Work.objects.filter(done=False, processor=processor, location=loc, job_type=job)

            count = qset.count()

            if count > 1:
                self.stdout.write('[INFO] Found duplicate work with processor=%s, location=%s, job_type=%s' % (
                                    processor, loc, repr(job)))

                count_doing = qset.filter(doing=True).count()
                count_queue = qset.filter(doing=False).count()

                self.stdout.write('       of which %s ongoing and %s queued' % (count_doing, count_queue))
        # for

# end of file
