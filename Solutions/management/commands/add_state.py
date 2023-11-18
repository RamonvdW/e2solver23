# -*- coding: utf-8 -*-

#  Copyright (c) 2023 Ramon van der Winkel.
#  All rights reserved.
#  Licensed under BSD-3-Clause-Clear. See LICENSE file for details.

from django.core.management.base import BaseCommand
from Solutions.models import State
import time


class Command(BaseCommand):

    help = "Add more state for random evictions"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def handle(self, *args, **options):

        self.stdout.write('[INFO] Adding 1M state records')

        state = State.objects.order_by('-pk').first()      # get highest
        if state:
            next_nr = state.pk + 1
        else:
            next_nr = 1
        todo = 1000000

        bulk = list()
        while todo > 0:
            todo -= 1

            ns = time.time_ns()
            evict = 1 + (ns & 63)

            bulk.append(State(nr=next_nr, evict=evict))
            next_nr += 1

            if len(bulk) >= 10000:
                State.objects.bulk_create(bulk)
                bulk = list()
                self.stdout.write('[INFO} To do: %s' % todo)
        # while

        if len(bulk) > 0:
            State.objects.bulk_create(bulk)

        self.stdout.write('[INFO] Done')

# end of file
