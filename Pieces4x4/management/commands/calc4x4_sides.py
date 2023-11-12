# -*- coding: utf-8 -*-

#  Copyright (c) 2023 Ramon van der Winkel.
#  All rights reserved.
#  Licensed under BSD-3-Clause-Clear. See LICENSE file for details.

from django.core.management.base import BaseCommand
from BasePieces.models import BasePiece
from Pieces2x2.models import TwoSides, Piece2x2
from Pieces4x4.models import Piece4x4

USE_CACHE = True
DO_STORE = True


class Command(BaseCommand):

    help = "Calculate side2 and side3 for all Piece4x4"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.nr2base = dict()   # [nr] = BasePiece

        for base in BasePiece.objects.all():
            self.nr2base[base.nr] = base
        # for

    def handle(self, *args, **options):

        done = 0
        print_done = 10000
        for p in Piece4x4.objects.all().iterator(chunk_size=10000):

            side2 = self.nr2base[p.nr4].get_side(2, p.rot4)
            side2 += self.nr2base[p.nr8].get_side(2, p.rot8)
            side2 += self.nr2base[p.nr12].get_side(2, p.rot12)
            side2 += self.nr2base[p.nr16].get_side(2, p.rot16)

            side3 = self.nr2base[p.nr16].get_side(3, p.rot16)
            side3 += self.nr2base[p.nr15].get_side(3, p.rot15)
            side3 += self.nr2base[p.nr14].get_side(3, p.rot14)
            side3 += self.nr2base[p.nr13].get_side(3, p.rot13)

            p.side2 = side2
            p.side3 = side3

            p.save(update_fields=['side2', 'side3'])
            done += 1
            if done >= print_done:
                self.stdout.write('%s done' % done)
                print_done += 10000
        # for

# end of file
