# -*- coding: utf-8 -*-

#  Copyright (c) 2024 Ramon van der Winkel.
#  All rights reserved.
#  Licensed under BSD-3-Clause-Clear. See LICENSE file for details.

from django.core.management.base import BaseCommand
from Ring1.models import Corner1, Corner2, Corner3, Corner4, Corner12, Corner34


class Command(BaseCommand):

    help = "Delete all pieces related to a seed"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def add_arguments(self, parser):
        parser.add_argument('seed', type=int, help='Randomization seed')

    def handle(self, *args, **options):

        seed = options['seed']

        self.stdout.write('[INFO] Deleting all Corner1 with seed=%s' % seed)
        Corner1.objects.filter(seed=seed).delete()

        self.stdout.write('[INFO] Deleting all Corner2 with seed=%s' % seed)
        Corner2.objects.filter(seed=seed).delete()

        self.stdout.write('[INFO] Deleting all Corner3 with seed=%s' % seed)
        Corner3.objects.filter(seed=seed).delete()

        self.stdout.write('[INFO] Deleting all Corner4 with seed=%s' % seed)
        Corner4.objects.filter(seed=seed).delete()

        self.stdout.write('[INFO] Deleting all Corner12 with seed=%s' % seed)
        Corner12.objects.filter(seed=seed).delete()

        self.stdout.write('[INFO] Deleting all Corner34 with seed=%s' % seed)
        Corner34.objects.filter(seed=seed).delete()


# end of file
