# -*- coding: utf-8 -*-

#  Copyright (c) 2024 Ramon van der Winkel.
#  All rights reserved.
#  Licensed under BSD-3-Clause-Clear. See LICENSE file for details.

from django.core.management.base import BaseCommand
from Pieces2x2.models import Piece2x2
from Ring1.models import Ring1


class Command(BaseCommand):

    help = "Check for alternative pieces for a Ring1"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # p2x2 nrs per side
        self._ring1 = None

        # Piece2x2 cache
        self._nr2p2x2 = dict()

        # used base pieces for entire Ring1
        self._used = list()

    def add_arguments(self, parser):
        parser.add_argument('ring1_nr', type=int, help='Ring1 nr to work on')

    def _load_ring1(self, nr):
        # returns False when it failed to load the Ring1

        self.stdout.write('[INFO] Loading Ring1 nr %s' % nr)

        try:
            self._ring1 = Ring1.objects.get(nr=nr)
        except Ring1.DoesNotExist:
            return False

        p2x2_nrs = list()
        for loc in (1, 2, 3, 4, 5, 6, 7, 8,
                    9, 16,
                    17, 24,
                    25, 32,
                    33, 40,
                    41, 48,
                    49, 56,
                    57, 58, 59, 60, 61, 62, 63, 64):
            nr_str = 'nr%s' % loc
            p2x2_nr = getattr(self._ring1, nr_str)
            p2x2_nrs.append(p2x2_nr)
        # for

        # load all p2x2's
        for p2x2 in Piece2x2.objects.filter(nr__in=p2x2_nrs):
            # set the p2x2 pieces as used
            self._nr2p2x2[p2x2.nr] = p2x2
            base_nrs = [p2x2.nr1, p2x2.nr2, p2x2.nr3, p2x2.nr4]
            self._used.extend(base_nrs)
        # for

        self._used = [nr
                      for nr in self._used
                      if nr > 60]
        self._used.sort()

        self.stdout.write('[INFO] Used base nrs: %s' % repr(self._used))

        return True

    def _find_alt_side1(self, loc):
        self.stdout.write('[INFO] Searching alternatives for loc %s on side1' % loc)

        loc_str = 'nr%s' % loc
        nr = getattr(self._ring1, loc_str)
        p2x2 = self._nr2p2x2[nr]

        used = self._used[:]
        used.remove(p2x2.nr3)
        used.remove(p2x2.nr4)

        count = (Piece2x2
                 .objects
                 .filter(nr1=p2x2.nr1,
                         nr2=p2x2.nr2,
                         side2=p2x2.side2,
                         side4=p2x2.side4)
                 .exclude(nr3__in=used)
                 .exclude(nr4__in=used)
                 .count())

        if count > 1:
            print('p2x2 %s: side2=%s, side4=%s --> %s' % (p2x2.nr, p2x2.side2, p2x2.side4, count))

    def _find_alt_side2(self, loc):
        self.stdout.write('[INFO] Searching alternatives for loc %s on side2' % loc)

        loc_str = 'nr%s' % loc
        nr = getattr(self._ring1, loc_str)
        p2x2 = self._nr2p2x2[nr]

        used = self._used[:]
        used.remove(p2x2.nr1)
        used.remove(p2x2.nr3)

        count = (Piece2x2
                 .objects
                 .filter(nr2=p2x2.nr2,
                         nr4=p2x2.nr4,
                         side1=p2x2.side1,
                         side3=p2x2.side3)
                 .exclude(nr1__in=used)
                 .exclude(nr3__in=used)
                 .count())

        if count > 1:
            print('p2x2 %s: side1=%s, side3=%s --> %s options' % (p2x2.nr, p2x2.side1, p2x2.side3, count))

    def _find_alt_side3(self, loc):
        self.stdout.write('[INFO] Searching alternatives for loc %s on side3' % loc)

        loc_str = 'nr%s' % loc
        nr = getattr(self._ring1, loc_str)
        p2x2 = self._nr2p2x2[nr]

        used = self._used[:]
        used.remove(p2x2.nr1)
        used.remove(p2x2.nr2)

        count = (Piece2x2
                 .objects
                 .filter(nr3=p2x2.nr3,
                         nr4=p2x2.nr4,
                         side2=p2x2.side2,
                         side4=p2x2.side4)
                 .exclude(nr1__in=used)
                 .exclude(nr2__in=used)
                 .count())

        if count > 1:
            print('p2x2 %s: side2=%s, side4=%s --> %s' % (p2x2.nr, p2x2.side2, p2x2.side4, count))

    def _find_alt_side4(self, loc):
        self.stdout.write('[INFO] Searching alternatives for loc %s on side4' % loc)

        loc_str = 'nr%s' % loc
        nr = getattr(self._ring1, loc_str)
        p2x2 = self._nr2p2x2[nr]

        used = self._used[:]
        used.remove(p2x2.nr2)
        used.remove(p2x2.nr4)

        count = (Piece2x2
                 .objects
                 .filter(nr1=p2x2.nr1,
                         nr3=p2x2.nr3,
                         side1=p2x2.side1,
                         side3=p2x2.side3)
                 .exclude(nr2__in=used)
                 .exclude(nr4__in=used)
                 .count())

        if count > 1:
            print('p2x2 %s: side1=%s, side3=%s --> %s options' % (p2x2.nr, p2x2.side1, p2x2.side3, count))

    def handle(self, *args, **options):
        nr = options['ring1_nr']

        if not self._load_ring1(nr):
            self.stdout.write('[ERROR] Cannot locate Ring1 with nr=%s' % nr)
            return

        self._find_alt_side1(3)
        self._find_alt_side1(4)
        self._find_alt_side1(5)
        self._find_alt_side1(6)

        self._find_alt_side2(24)
        self._find_alt_side2(32)
        self._find_alt_side2(40)
        self._find_alt_side2(48)

        self._find_alt_side3(59)
        self._find_alt_side3(60)
        self._find_alt_side3(61)
        self._find_alt_side3(62)

# end of file
