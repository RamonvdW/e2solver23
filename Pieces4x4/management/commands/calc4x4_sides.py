# -*- coding: utf-8 -*-

#  Copyright (c) 2023 Ramon van der Winkel.
#  All rights reserved.
#  Licensed under BSD-3-Clause-Clear. See LICENSE file for details.

from django.core.management.base import BaseCommand
from BasePieces.models import BasePiece
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

        # find a piece without a side
        p = Piece4x4.objects.filter(side2='', side3='').first()
        while p:

            # calculate the sides
            side2 = self.nr2base[p.nr4].get_side(2, p.rot4)
            side2 += self.nr2base[p.nr8].get_side(2, p.rot8)
            side2 += self.nr2base[p.nr12].get_side(2, p.rot12)
            side2 += self.nr2base[p.nr16].get_side(2, p.rot16)

            side3 = self.nr2base[p.nr16].get_side(3, p.rot16)
            side3 += self.nr2base[p.nr15].get_side(3, p.rot15)
            side3 += self.nr2base[p.nr14].get_side(3, p.rot14)
            side3 += self.nr2base[p.nr13].get_side(3, p.rot13)

            done += 1
            self.stdout.write('[INFO] Update %s: side2=%s, side3=%s' % (done, side2, side3))

            # update all the Piece4x4 with these borders in one go
            (Piece4x4
             .objects
             .filter(nr4=p.nr4, nr8=p.nr8, nr12=p.nr12, nr13=p.nr13, nr14=p.nr14, nr15=p.nr15, nr16=p.nr16,
                     rot4=p.rot4, rot8=p.rot8, rot12=p.rot12, rot13=p.rot13, rot14=p.rot14, rot15=p.rot15,rot16=p.rot16)
             .update(side2=side2, side3=side3))
             
            # find the next piece without a side
            p = Piece4x4.objects.filter(side2='', side3='').first()
        # while

        self.stdout.write('[INFO] Done!')

# end of file
