# -*- coding: utf-8 -*-

#  Copyright (c) 2023 Ramon van der Winkel.
#  All rights reserved.
#  Licensed under BSD-3-Clause-Clear. See LICENSE file for details.

from django.db import models

NRS_PARTIAL_6X6 = (10, 11, 12, 13, 14, 15,
                   18, 19, 20, 21, 22, 23,
                   26, 27, 28, 29, 30, 31,
                   34, 35, 36, 37, 38, 39,
                   42, 43, 44, 45, 46, 47,
                   50, 51, 52, 53, 54, 55)


class Quart6(models.Model):
    """
        Quart of a 6x6 outer ring
        Made for a specific 4x4, so the inner ring is not stored


         c1    p2                 p1    c1
           +--+--+               +--+--+
           |10|11|               |14|15|
           +--+--+               +--+--+
        p1 |18|                     |23| p2
           +--+ type10       type15 +--+

           +--+ type50       type55 +--+
        p2 |42|                     |47| p1
           +--+--+               +--+--+
           |50|51|               |54|55|
           +--+--+               +--+--+
         c1    p1                 p2    c1
    """

    # created by which task?
    processor = models.PositiveIntegerField(default=0)

    based_on_4x4 = models.PositiveBigIntegerField()

    # 10, 15, 50 or 55
    type = models.PositiveSmallIntegerField()

    # composite pieces making up this quart
    p1 = models.PositiveIntegerField()  # Piece2x2
    c1 = models.PositiveIntegerField()  # Piece2x2 with hint
    p2 = models.PositiveIntegerField()  # Piece2x2

    # base pieces making up this quart
    # (only intended for filtering)
    nr1 = models.PositiveSmallIntegerField()
    nr2 = models.PositiveSmallIntegerField()
    nr3 = models.PositiveSmallIntegerField()
    nr4 = models.PositiveSmallIntegerField()

    nr5 = models.PositiveSmallIntegerField()
    nr6 = models.PositiveSmallIntegerField()
    nr7 = models.PositiveSmallIntegerField()
    nr8 = models.PositiveSmallIntegerField()

    nr9 = models.PositiveSmallIntegerField()
    nr10 = models.PositiveSmallIntegerField()
    nr11 = models.PositiveSmallIntegerField()
    nr12 = models.PositiveSmallIntegerField()

    class Meta:
        verbose_name = verbose_name_plural = 'Quart6'

        indexes = [
            models.Index(fields=['nr1']),
            models.Index(fields=['nr2']),
            models.Index(fields=['nr3']),
            models.Index(fields=['nr4']),
            models.Index(fields=['nr5']),
            models.Index(fields=['nr6']),
            models.Index(fields=['nr7']),
            models.Index(fields=['nr8']),
            models.Index(fields=['nr9']),
            models.Index(fields=['nr10']),
            models.Index(fields=['nr11']),
            models.Index(fields=['nr12']),
            models.Index(fields=['based_on_4x4']),
            models.Index(fields=['processor']),
        ]

    objects = models.Manager()  # for the editor only


class Partial6x6(models.Model):
    """
        A partial solution contains 36 Piece2x2 in the center

        Piece numbering as per Solution: starting in top-left with nr1, fills 1 row and then continues on the next row

         1   2  3  4  5  6  7   8

         9  10 11 12 13 14 15  16
        17  18 19 20 21 22 23  24
        25  26 27 28 29 30 31  32
        33  34 35 36 37 38 39  40
        41  42 43 44 45 46 47  48
        49  50 51 52 53 54 55  56

        57  58 59 60 61 62 63  64
    """

    when = models.DateTimeField(auto_now_add=True)

    # was this 6x6 processed further into an 8x8?
    processor = models.PositiveIntegerField(default=0)
    is_processed = models.BooleanField(default=False)

    based_on_4x4 = models.PositiveBigIntegerField()

    note1 = models.CharField(max_length=30, default='', blank=True)
    note2 = models.CharField(max_length=30, default='', blank=True)
    note3 = models.CharField(max_length=30, default='', blank=True)
    note4 = models.CharField(max_length=30, default='', blank=True)
    note5 = models.CharField(max_length=30, default='', blank=True)
    note6 = models.CharField(max_length=30, default='', blank=True)
    note7 = models.CharField(max_length=30, default='', blank=True)
    note8 = models.CharField(max_length=30, default='', blank=True)
    note9 = models.CharField(max_length=30, default='', blank=True)

    # 2x2 pieces used to build up this piece
    nr10 = models.PositiveIntegerField()
    nr11 = models.PositiveIntegerField()
    nr12 = models.PositiveIntegerField()
    nr13 = models.PositiveIntegerField()
    nr14 = models.PositiveIntegerField()
    nr15 = models.PositiveIntegerField()

    note16 = models.CharField(max_length=30, default='', blank=True)
    note17 = models.CharField(max_length=30, default='', blank=True)

    nr18 = models.PositiveIntegerField()
    nr19 = models.PositiveIntegerField()
    nr20 = models.PositiveIntegerField()
    nr21 = models.PositiveIntegerField()
    nr22 = models.PositiveIntegerField()
    nr23 = models.PositiveIntegerField()

    note24 = models.CharField(max_length=30, default='', blank=True)
    note25 = models.CharField(max_length=30, default='', blank=True)

    nr26 = models.PositiveIntegerField()
    nr27 = models.PositiveIntegerField()
    nr28 = models.PositiveIntegerField()
    nr29 = models.PositiveIntegerField()
    nr30 = models.PositiveIntegerField()
    nr31 = models.PositiveIntegerField()

    note32 = models.CharField(max_length=30, default='', blank=True)
    note33 = models.CharField(max_length=30, default='', blank=True)

    nr34 = models.PositiveIntegerField()
    nr35 = models.PositiveIntegerField()
    nr36 = models.PositiveIntegerField()
    nr37 = models.PositiveIntegerField()
    nr38 = models.PositiveIntegerField()
    nr39 = models.PositiveIntegerField()

    note40 = models.CharField(max_length=30, default='', blank=True)
    note41 = models.CharField(max_length=30, default='', blank=True)

    nr42 = models.PositiveIntegerField()
    nr43 = models.PositiveIntegerField()
    nr44 = models.PositiveIntegerField()
    nr45 = models.PositiveIntegerField()
    nr46 = models.PositiveIntegerField()
    nr47 = models.PositiveIntegerField()

    note48 = models.CharField(max_length=30, default='', blank=True)
    note49 = models.CharField(max_length=30, default='', blank=True)

    nr50 = models.PositiveIntegerField()
    nr51 = models.PositiveIntegerField()
    nr52 = models.PositiveIntegerField()
    nr53 = models.PositiveIntegerField()
    nr54 = models.PositiveIntegerField()
    nr55 = models.PositiveIntegerField()

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
        verbose_name = 'Partial 6x6'
        verbose_name_plural = 'Partial 6x6'

    objects = models.Manager()  # for the editor only


# end of file
