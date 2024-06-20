# -*- coding: utf-8 -*-

#  Copyright (c) 2023-2024 Ramon van der Winkel.
#  All rights reserved.
#  Licensed under BSD-3-Clause-Clear. See LICENSE file for details.

from django.core.management.base import BaseCommand
from Pieces2x2.models import TwoSideOptions
from Pieces2x2.helpers import calc_segment
from WorkQueue.operations import propagate_segment_reduction, request_eval_claims, used_note_add


class Command(BaseCommand):

    help = "Fix one of the locations to one of possible Piece2x2"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def add_arguments(self, parser):
        parser.add_argument('processor', type=int, help='Processor number to use')
        parser.add_argument('loc', type=int, help='Location on the board (1..64)')
        parser.add_argument('side', type=int, help='Location side (1..4)')
        parser.add_argument('index', type=int, help='i-th segment to use')
        parser.add_argument('--nop', action='store_true', help='Do not propagate')
        parser.add_argument('--commit', action='store_true')

    @staticmethod
    def _get_side_options(processor, segment):
        options = (TwoSideOptions
                   .objects
                   .filter(processor=processor,
                           segment=segment)
                   .values_list('two_side', flat=True))
        return list(options)

    def handle(self, *args, **options):

        nop = options['nop']
        loc = options['loc']
        side = options['side']
        index = options['index']
        do_commit = options['commit']
        processor = options['processor']

        segment = calc_segment(loc, side)
        self.stdout.write('[INFO] Processor=%s; Segment: %s' % (processor, segment))

        options = (TwoSideOptions
                   .objects
                   .filter(processor=processor,
                           segment=segment)
                   .values_list('two_side', flat=True))
        options = list(options)

        self.stdout.write('[INFO] Selecting %s / %s' % (index, len(options)))
        if 0 <= index < len(options):
            keep = options[index]
        else:
            self.stderr.write('[ERROR] Invalid index')
            return

        qset = TwoSideOptions.objects.filter(processor=processor, segment=segment).exclude(two_side=keep)
        self.stdout.write('[INFO] Reductions: %s' % qset.count())

        if do_commit:
            qset.delete()

            msg = 'fix_seg %s %s' % (segment, index)
            used_note_add(processor, msg)

            if not nop:
                propagate_segment_reduction(processor, segment)

            request_eval_claims(processor)
        else:
            self.stdout.write('[WARNING] Use --commit to keep')


# end of file
