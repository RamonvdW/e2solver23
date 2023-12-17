# -*- coding: utf-8 -*-

#  Copyright (c) 2023 Ramon van der Winkel.
#  All rights reserved.
#  Licensed under BSD-3-Clause-Clear. See LICENSE file for details.

from django.core.management.base import BaseCommand
from Pieces2x2.models import Piece2x2, TwoSide


class Command(BaseCommand):

    help = "Calculate the set of sides needed for each ring"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.border_side = TwoSide.objects.get(two_sides='XX').nr

    def _calc_all(self):
        # bepaal hoeveel TwoSides er zijn
        print('totaal: %s' % TwoSide.objects.count())

    def _calc_side1(self):
        c = Piece2x2.objects.filter(side1=self.border_side).distinct('side3').count()
        print('boven: %s' % c)

    def _calc_side2(self):
        c = Piece2x2.objects.filter(side2=self.border_side).distinct('side4').count()
        print('rechts: %s' % c)

    def _calc_side3(self):
        c = Piece2x2.objects.filter(side3=self.border_side).distinct('side1').count()
        print('onder: %s' % c)

    def _calc_side4(self):
        c = Piece2x2.objects.filter(side4=self.border_side).distinct('side2').count()
        print('links: %s' % c)

    def handle(self, *args, **options):
        self._calc_all()
        self._calc_side1()
        self._calc_side2()
        self._calc_side3()
        self._calc_side4()


# end of file
