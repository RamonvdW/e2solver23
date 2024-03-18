# -*- coding: utf-8 -*-

#  Copyright (c) 2024 Ramon van der Winkel.
#  All rights reserved.
#  Licensed under BSD-3-Clause-Clear. See LICENSE file for details.

from django.core.management.base import BaseCommand
from WorkQueue.models import Work, ProcessorUsedPieces


class Command(BaseCommand):

    help = "Count how many concurrent processors are being worked on"

    def handle(self, *args, **options):

        # delete Work records for completed processors
        processors = ProcessorUsedPieces.objects.filter(reached_dead_end=True).values('processor')
        Work.objects.filter(processor__in=processors).delete()

        count = ProcessorUsedPieces.objects.exclude(reached_dead_end=True).count()
        self.stdout.write('%s' % count)


# end of file
