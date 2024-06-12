# -*- coding: utf-8 -*-

#  Copyright (c) 2024 Ramon van der Winkel.
#  All rights reserved.
#  Licensed under BSD-3-Clause-Clear. See LICENSE file for details.

from django.core.management.base import BaseCommand
from WorkQueue.models import ProcessorUsedPieces


class Command(BaseCommand):

    help = "Clean up boards without siblings"

    """
        A board stays when:
            - it has siblings that refer to it (created_from)
            - it is a sibling that refers to another board
    """


    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.proc: ProcessorUsedPieces | None = None

        # which locations are not yet filled?
        self.locs_free = list()

        self.loc2unused = dict()        # [loc] = [nr, nr, ..]
        self.loc2claims = dict()        # [loc] = [nr, nr, ..]
        self.segment2two_sides = dict()   # [segment] = [two_side, two_side, ..]

        self.verbose = False

    def add_arguments(self, parser):
        parser.add_argument('--verbose', action='store_true')
        parser.add_argument('--commit', action='store_true')

    def _find_boards_without_siblings(self):
        qset = ProcessorUsedPieces.objects.exclude(reached_dead_end=True).order_by('processor')

        logs = list()
        for proc in qset:
            logs.append(proc.choices)
        # for

        nrs = list()
        created_from = dict()
        levels = dict()              # [processor] = level
        level_counts = dict()        # [level] = count
        for proc in qset:
            nrs.append(proc.processor)

            level = 0
            for log in logs:
                if proc.choices.startswith(log):
                    level += 1
            # for
            levels[proc.processor] = level

            try:
                level_counts[level] += 1
            except KeyError:
                level_counts[level] = 1

            try:
                created_from[proc.created_from] += 1
            except KeyError:
                created_from[proc.created_from] = 1

            if self.verbose:
                self.stdout.write('Board %s has level %s and was created from %s' % (proc.processor,
                                                                                     level,
                                                                                     proc.created_from))
        # for

        highest_level = max(levels.values())

        for level in range(1, highest_level+1):
            self.stdout.write('Level %s has %s boards' % (level, level_counts[level]))
        # for

        remove_nrs = list()
        for nr in nrs:
            level = levels[nr]
            if level < highest_level:
                try:
                    c = created_from[nr]
                except KeyError:
                    c = 0

                if c == 0:
                    remove_nrs.append(nr)
        # for

        return remove_nrs

    def handle(self, *args, **options):

        self.verbose = options['verbose']
        commit = options['commit']

        nrs = self._find_boards_without_siblings()

        if len(nrs):
            if commit:
                self.stdout.write('[INFO] Removing %s boards' % len(nrs))
                ProcessorUsedPieces.objects.filter(processor__in=nrs).delete()
            else:
                self.stdout.write('[INFO] Can remove %s boards' % len(nrs))
                if self.verbose:
                    self.stdout.write("%s" % repr(nrs))
                self.stdout.write('[INFO] Use --commit to actually remove')
        else:
            self.stdout.write('[INFO] Found no boards to remove')

# end of file
