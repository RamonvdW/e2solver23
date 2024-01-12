# -*- coding: utf-8 -*-

#  Copyright (c) 2023-2024 Ramon van der Winkel.
#  All rights reserved.
#  Licensed under BSD-3-Clause-Clear. See LICENSE file for details.

from django.core.management.base import BaseCommand
from WorkQueue.models import Work


class Command(BaseCommand):

    help = "Remove duplicate work orders"

    def add_arguments(self, parser):
        parser.add_argument('--verbose', action='store_true')

    def handle(self, *args, **options):

        verbose = options['verbose']

        deleted = 0
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
                count_doing = qset.filter(doing=True).count()
                count_queue = qset.filter(doing=False).count()

                if verbose:
                    self.stdout.write('[INFO] Found duplicate work with processor=%s, location=%s, job_type=%s' % (
                                        processor, loc, repr(job)))
                    self.stdout.write('       of which %s ongoing and %s queued' % (count_doing, count_queue))

                if count_doing > 0:
                    # delete all queued work
                    qset.filter(doing=False).delete()
                    deleted += count_queue
                else:
                    # delete all but the oldest
                    pks = list(qset.filter(doing=False).order_by('-doing').values_list('pk', flat=True))
                    pks = pks[1:]       # keep the oldest
                    Work.objects.filter(pk__in=pks).delete()
                    deleted += len(pks)
        # for

        self.stdout.write('[INFO] Deleted %d jobs' % deleted)

# end of file
