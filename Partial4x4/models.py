# -*- coding: utf-8 -*-

#  Copyright (c) 2023 Ramon van der Winkel.
#  All rights reserved.
#  Licensed under BSD-3-Clause-Clear. See LICENSE file for details.

from django.db import models

NRS_PARTIAL_4X4 = (19, 20, 21, 22,
                   27, 28, 29, 30,
                   35, 36, 37, 38,
                   43, 44, 45, 46)


class Partial4x4(models.Model):
    """
        A partial solution contains 16 Piece2x2 in the center

        Piece numbering as per Solution: starting in top-left with nr1, fills 1 row and then continues on the next row

         1  2   3  4  5  6   7  8
         9 10  11 12 13 14  15 16
              +-----------+
        17 18 |19 20 21 22| 23 24
        25 26 |27 28 29 30| 31 32
        33 34 |35 36 37 38| 39 40
        41 42 |43 44 45 46| 47 48
              +-----------+
        49 50  51 52 53 54  55 56
        57 58  59 60 61 62  63 64
    """

    when = models.DateTimeField(auto_now_add=True)

    # was this 4x4 processed further into an 6x6?
    processor = models.PositiveIntegerField(default=0)
    is_processed = models.BooleanField(default=False)

    note1 = models.CharField(max_length=30, default='', blank=True)
    note2 = models.CharField(max_length=30, default='', blank=True)
    note3 = models.CharField(max_length=30, default='', blank=True)
    note4 = models.CharField(max_length=30, default='', blank=True)
    note5 = models.CharField(max_length=30, default='', blank=True)
    note6 = models.CharField(max_length=30, default='', blank=True)
    note7 = models.CharField(max_length=30, default='', blank=True)
    note8 = models.CharField(max_length=30, default='', blank=True)
    note9 = models.CharField(max_length=30, default='', blank=True)
    note10 = models.CharField(max_length=30, default='', blank=True)
    note11 = models.CharField(max_length=30, default='', blank=True)
    note12 = models.CharField(max_length=30, default='', blank=True)
    note13 = models.CharField(max_length=30, default='', blank=True)
    note14 = models.CharField(max_length=30, default='', blank=True)
    note15 = models.CharField(max_length=30, default='', blank=True)
    note16 = models.CharField(max_length=30, default='', blank=True)
    note17 = models.CharField(max_length=30, default='', blank=True)
    note18 = models.CharField(max_length=30, default='', blank=True)

    # 2x2 pieces used to build up this piece
    nr19 = models.PositiveIntegerField()
    nr20 = models.PositiveIntegerField()
    nr21 = models.PositiveIntegerField()
    nr22 = models.PositiveIntegerField()

    note23 = models.CharField(max_length=30, default='', blank=True)
    note24 = models.CharField(max_length=30, default='', blank=True)
    note25 = models.CharField(max_length=30, default='', blank=True)
    note26 = models.CharField(max_length=30, default='', blank=True)

    nr27 = models.PositiveIntegerField()
    nr28 = models.PositiveIntegerField()
    nr29 = models.PositiveIntegerField()
    nr30 = models.PositiveIntegerField()

    note31 = models.CharField(max_length=30, default='', blank=True)
    note32 = models.CharField(max_length=30, default='', blank=True)
    note33 = models.CharField(max_length=30, default='', blank=True)
    note34 = models.CharField(max_length=30, default='', blank=True)

    nr35 = models.PositiveIntegerField()
    nr36 = models.PositiveIntegerField()
    nr37 = models.PositiveIntegerField()
    nr38 = models.PositiveIntegerField()

    note39 = models.CharField(max_length=30, default='', blank=True)
    note40 = models.CharField(max_length=30, default='', blank=True)
    note41 = models.CharField(max_length=30, default='', blank=True)
    note42 = models.CharField(max_length=30, default='', blank=True)

    nr43 = models.PositiveIntegerField()
    nr44 = models.PositiveIntegerField()
    nr45 = models.PositiveIntegerField()
    nr46 = models.PositiveIntegerField()

    note47 = models.CharField(max_length=30, default='', blank=True)
    note48 = models.CharField(max_length=30, default='', blank=True)
    note49 = models.CharField(max_length=30, default='', blank=True)
    note50 = models.CharField(max_length=30, default='', blank=True)
    note51 = models.CharField(max_length=30, default='', blank=True)
    note52 = models.CharField(max_length=30, default='', blank=True)
    note53 = models.CharField(max_length=30, default='', blank=True)
    note54 = models.CharField(max_length=30, default='', blank=True)
    note55 = models.CharField(max_length=30, default='', blank=True)
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
        verbose_name = 'Partial 4x4'
        verbose_name_plural = 'Partial 4x4s'

    objects = models.Manager()  # for the editor only


# end of file
