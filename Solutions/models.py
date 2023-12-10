# -*- coding: utf-8 -*-

#  Copyright (c) 2023 Ramon van der Winkel.
#  All rights reserved.
#  Licensed under BSD-3-Clause-Clear. See LICENSE file for details.

from django.db import models

NRS_ADDED_IN_8X8 = (1, 2, 3, 4, 5, 6, 7, 8,
                    9, 16,
                    17, 24,
                    25, 32,
                    33, 40,
                    41, 48,
                    49, 56,
                    57, 58, 59, 60, 61, 62, 63, 64)

P_CORNER = (1, 8, 57, 64)
P_BORDER = (2, 3, 4, 5, 6, 7,  16, 24, 32, 40, 48, 56,  9, 17, 25, 33, 41, 49,  58, 59, 60, 61, 62, 63)
P_HINTS = (10, 15, 36, 50, 55)


class Solution8x8(models.Model):

    """ A solution contains up to 64 Piece2x2

        Piece numbering starts in top-left with nr1, fills 1 row and then continues on the next row

         1  2  3  4  5  6  7  8
         9 10 11 12 13 14 15 16
        17 18 19 20 21 22 23 24
        25 26 27 28 29 30 31 32
        33 34 35 36 37 38 39 40
        41 42 43 44 45 46 47 48
        49 50 51 52 53 54 55 56
        57 58 59 60 61 62 63 64

        Corner pieces: 1 8 57 64
        Border pieces: 2 3 4 5 6 7 9  16 24 32 40 47 56  17 25 33 41 49 56  58 59 60 61 62 63
        Hints in locations: 10, 15, 36, 50, 55

        10.p1 = 208
        15.p2 = 255
        36.p2 = 139
        50.p3 = 181
        55.p4 = 249
    """

    when = models.DateTimeField(auto_now_add=True)

    based_on_6x6 = models.PositiveBigIntegerField()

    # 2x2 pieces used to build up this piece
    nr1 = models.PositiveIntegerField()
    nr2 = models.PositiveIntegerField()
    nr3 = models.PositiveIntegerField()
    nr4 = models.PositiveIntegerField()
    nr5 = models.PositiveIntegerField()
    nr6 = models.PositiveIntegerField()
    nr7 = models.PositiveIntegerField()
    nr8 = models.PositiveIntegerField()
    nr9 = models.PositiveIntegerField()

    nr10 = models.PositiveIntegerField()
    nr11 = models.PositiveIntegerField()
    nr12 = models.PositiveIntegerField()
    nr13 = models.PositiveIntegerField()
    nr14 = models.PositiveIntegerField()
    nr15 = models.PositiveIntegerField()
    nr16 = models.PositiveIntegerField()
    nr17 = models.PositiveIntegerField()
    nr18 = models.PositiveIntegerField()
    nr19 = models.PositiveIntegerField()

    nr20 = models.PositiveIntegerField()
    nr21 = models.PositiveIntegerField()
    nr22 = models.PositiveIntegerField()
    nr23 = models.PositiveIntegerField()
    nr24 = models.PositiveIntegerField()
    nr25 = models.PositiveIntegerField()
    nr26 = models.PositiveIntegerField()
    nr27 = models.PositiveIntegerField()
    nr28 = models.PositiveIntegerField()
    nr29 = models.PositiveIntegerField()

    nr30 = models.PositiveIntegerField()
    nr31 = models.PositiveIntegerField()
    nr32 = models.PositiveIntegerField()
    nr33 = models.PositiveIntegerField()
    nr34 = models.PositiveIntegerField()
    nr35 = models.PositiveIntegerField()
    nr36 = models.PositiveIntegerField()
    nr37 = models.PositiveIntegerField()
    nr38 = models.PositiveIntegerField()
    nr39 = models.PositiveIntegerField()

    nr40 = models.PositiveIntegerField()
    nr41 = models.PositiveIntegerField()
    nr42 = models.PositiveIntegerField()
    nr43 = models.PositiveIntegerField()
    nr44 = models.PositiveIntegerField()
    nr45 = models.PositiveIntegerField()
    nr46 = models.PositiveIntegerField()
    nr47 = models.PositiveIntegerField()
    nr48 = models.PositiveIntegerField()
    nr49 = models.PositiveIntegerField()

    nr50 = models.PositiveIntegerField()
    nr51 = models.PositiveIntegerField()
    nr52 = models.PositiveIntegerField()
    nr53 = models.PositiveIntegerField()
    nr54 = models.PositiveIntegerField()
    nr55 = models.PositiveIntegerField()
    nr56 = models.PositiveIntegerField()
    nr57 = models.PositiveIntegerField()
    nr58 = models.PositiveIntegerField()
    nr59 = models.PositiveIntegerField()

    nr60 = models.PositiveIntegerField()
    nr61 = models.PositiveIntegerField()
    nr62 = models.PositiveIntegerField()
    nr63 = models.PositiveIntegerField()
    nr64 = models.PositiveIntegerField()

    note1 = models.CharField(max_length=30, default='', blank=True)
    note2 = models.CharField(max_length=30, default='', blank=True)
    note3 = models.CharField(max_length=30, default='', blank=True)
    note4 = models.CharField(max_length=30, default='', blank=True)
    note5 = models.CharField(max_length=30, default='', blank=True)
    note6 = models.CharField(max_length=30, default='', blank=True)
    note7 = models.CharField(max_length=30, default='', blank=True)
    note8 = models.CharField(max_length=30, default='', blank=True)
    note9 = models.CharField(max_length=30, default='', blank=True)

    note16 = models.CharField(max_length=30, default='', blank=True)
    note17 = models.CharField(max_length=30, default='', blank=True)

    note24 = models.CharField(max_length=30, default='', blank=True)
    note25 = models.CharField(max_length=30, default='', blank=True)

    note32 = models.CharField(max_length=30, default='', blank=True)
    note33 = models.CharField(max_length=30, default='', blank=True)

    note40 = models.CharField(max_length=30, default='', blank=True)
    note41 = models.CharField(max_length=30, default='', blank=True)

    note48 = models.CharField(max_length=30, default='', blank=True)
    note49 = models.CharField(max_length=30, default='', blank=True)

    note56 = models.CharField(max_length=30, default='', blank=True)
    note57 = models.CharField(max_length=30, default='', blank=True)
    note58 = models.CharField(max_length=30, default='', blank=True)
    note59 = models.CharField(max_length=30, default='', blank=True)
    note60 = models.CharField(max_length=30, default='', blank=True)
    note61 = models.CharField(max_length=30, default='', blank=True)
    note62 = models.CharField(max_length=30, default='', blank=True)
    note63 = models.CharField(max_length=30, default='', blank=True)
    note64 = models.CharField(max_length=30, default='', blank=True)

    class Meta:
        verbose_name = 'Solution8x8'

    objects = models.Manager()  # for the editor only


# end of file
