# -*- coding: utf-8 -*-

#  Copyright (c) 2023-2024 Ramon van der Winkel.
#  All rights reserved.
#  Licensed under BSD-3-Clause-Clear. See LICENSE file for details.

from django.core.management.base import BaseCommand
from Pieces2x2.models import TwoSideOptions, EvalProgress
from WorkQueue.models import Work, ProcessorUsedPieces


class Command(BaseCommand):

    help = "Drop the a specific TwoSideOptions set"

    def add_arguments(self, parser):
        parser.add_argument('processor', type=int, nargs='+', help='Processor number(s) to drop')

    def handle(self, *args, **options):

        for processor in options['processor']:
            qset = TwoSideOptions.objects.filter(processor=processor)
            count = qset.count()

            if count == 0:
                self.stderr.write('[ERROR] Processor %s not found' % processor)
            else:
                self.stdout.write('[INFO] Deleting %s TwoSide records' % count)
                qset.delete()

                count = Work.objects.filter(processor=processor).count()
                Work.objects.filter(processor=processor).delete()
                self.stdout.write('[INFO] Deleted %s jobs for processor %s from work queue' % (count, processor))

            try:
                ProcessorUsedPieces.objects.filter(processor=processor).delete()
            except ProcessorUsedPieces.DoesNotExist:
                pass

            try:
                EvalProgress.objects.filter(processor=processor).delete()
            except EvalProgress.DoesNotExist:
                pass
        # for

# end of file
