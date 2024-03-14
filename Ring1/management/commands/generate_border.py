# -*- coding: utf-8 -*-

#  Copyright (c) 2024 Ramon van der Winkel.
#  All rights reserved.
#  Licensed under BSD-3-Clause-Clear. See LICENSE file for details.

from django.core.management.base import BaseCommand
from BasePieces.border import GenerateBorder


class Command(BaseCommand):

    help = "Generate solutions for the outer border ring"

    def add_arguments(self, parser):
        parser.add_argument('seed', type=int, help='Randomization seed')

    def handle(self, *args, **options):
        seed = options['seed']
        gen = GenerateBorder(seed)
        for sol in gen.iter_solutions():
            print('solution: %s' % repr(sol))

# end of file
