# -*- coding: utf-8 -*-

#  Copyright (c) 2023 Ramon van der Winkel.
#  All rights reserved.
#  Licensed under BSD-3-Clause-Clear. See LICENSE file for details.

from django.db import models

P_CORNER = (1, 8, 57, 64)
P_BORDER = (2, 3, 4, 5, 6, 7,  16, 24, 32, 40, 48, 56,  9, 17, 25, 33, 41, 49,  58, 59, 60, 61, 62, 63)
P_HINTS = (10, 15, 36, 50, 55)
ALL_HINT_NRS = (139, 181, 208, 249, 255)


class Solution(models.Model):

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

    nr = models.PositiveIntegerField(primary_key=True)      # max = 2147483647

    when = models.DateTimeField(auto_now_add=True)

    state = models.PositiveBigIntegerField()

    # aantal velden niet gevuld
    gap_count = models.PositiveSmallIntegerField()

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
    note10 = models.CharField(max_length=30, default='', blank=True)
    note11 = models.CharField(max_length=30, default='', blank=True)
    note12 = models.CharField(max_length=30, default='', blank=True)
    note13 = models.CharField(max_length=30, default='', blank=True)
    note14 = models.CharField(max_length=30, default='', blank=True)
    note15 = models.CharField(max_length=30, default='', blank=True)
    note16 = models.CharField(max_length=30, default='', blank=True)
    note17 = models.CharField(max_length=30, default='', blank=True)
    note18 = models.CharField(max_length=30, default='', blank=True)
    note19 = models.CharField(max_length=30, default='', blank=True)
    note20 = models.CharField(max_length=30, default='', blank=True)
    note21 = models.CharField(max_length=30, default='', blank=True)
    note22 = models.CharField(max_length=30, default='', blank=True)
    note23 = models.CharField(max_length=30, default='', blank=True)
    note24 = models.CharField(max_length=30, default='', blank=True)
    note25 = models.CharField(max_length=30, default='', blank=True)
    note26 = models.CharField(max_length=30, default='', blank=True)
    note27 = models.CharField(max_length=30, default='', blank=True)
    note28 = models.CharField(max_length=30, default='', blank=True)
    note29 = models.CharField(max_length=30, default='', blank=True)
    note30 = models.CharField(max_length=30, default='', blank=True)
    note31 = models.CharField(max_length=30, default='', blank=True)
    note32 = models.CharField(max_length=30, default='', blank=True)
    note33 = models.CharField(max_length=30, default='', blank=True)
    note34 = models.CharField(max_length=30, default='', blank=True)
    note35 = models.CharField(max_length=30, default='', blank=True)
    note36 = models.CharField(max_length=30, default='', blank=True)
    note37 = models.CharField(max_length=30, default='', blank=True)
    note38 = models.CharField(max_length=30, default='', blank=True)
    note39 = models.CharField(max_length=30, default='', blank=True)
    note40 = models.CharField(max_length=30, default='', blank=True)
    note41 = models.CharField(max_length=30, default='', blank=True)
    note42 = models.CharField(max_length=30, default='', blank=True)
    note43 = models.CharField(max_length=30, default='', blank=True)
    note44 = models.CharField(max_length=30, default='', blank=True)
    note45 = models.CharField(max_length=30, default='', blank=True)
    note46 = models.CharField(max_length=30, default='', blank=True)
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
        verbose_name = 'Solution'

    objects = models.Manager()  # for the editor only


class Solution6x6(models.Model):

    """ A solution contains 36 Piece2x2 in the center

        Piece numbering starts in top-left with nr1, fills 1 row and then continues on the next row

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

    # 2x2 pieces used to build up this piece
    nr10 = models.PositiveIntegerField()
    nr11 = models.PositiveIntegerField()
    nr12 = models.PositiveIntegerField()
    nr13 = models.PositiveIntegerField()
    nr14 = models.PositiveIntegerField()
    nr15 = models.PositiveIntegerField()

    nr18 = models.PositiveIntegerField()
    nr19 = models.PositiveIntegerField()
    nr20 = models.PositiveIntegerField()
    nr21 = models.PositiveIntegerField()
    nr22 = models.PositiveIntegerField()
    nr23 = models.PositiveIntegerField()

    nr26 = models.PositiveIntegerField()
    nr27 = models.PositiveIntegerField()
    nr28 = models.PositiveIntegerField()
    nr29 = models.PositiveIntegerField()
    nr30 = models.PositiveIntegerField()
    nr31 = models.PositiveIntegerField()

    nr34 = models.PositiveIntegerField()
    nr35 = models.PositiveIntegerField()
    nr36 = models.PositiveIntegerField()
    nr37 = models.PositiveIntegerField()
    nr38 = models.PositiveIntegerField()
    nr39 = models.PositiveIntegerField()

    nr42 = models.PositiveIntegerField()
    nr43 = models.PositiveIntegerField()
    nr44 = models.PositiveIntegerField()
    nr45 = models.PositiveIntegerField()
    nr46 = models.PositiveIntegerField()
    nr47 = models.PositiveIntegerField()

    nr50 = models.PositiveIntegerField()
    nr51 = models.PositiveIntegerField()
    nr52 = models.PositiveIntegerField()
    nr53 = models.PositiveIntegerField()
    nr54 = models.PositiveIntegerField()
    nr55 = models.PositiveIntegerField()

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
    note19 = models.CharField(max_length=30, default='', blank=True)
    note20 = models.CharField(max_length=30, default='', blank=True)
    note21 = models.CharField(max_length=30, default='', blank=True)
    note22 = models.CharField(max_length=30, default='', blank=True)
    note23 = models.CharField(max_length=30, default='', blank=True)
    note24 = models.CharField(max_length=30, default='', blank=True)
    note25 = models.CharField(max_length=30, default='', blank=True)
    note26 = models.CharField(max_length=30, default='', blank=True)
    note27 = models.CharField(max_length=30, default='', blank=True)
    note28 = models.CharField(max_length=30, default='', blank=True)
    note29 = models.CharField(max_length=30, default='', blank=True)
    note30 = models.CharField(max_length=30, default='', blank=True)
    note31 = models.CharField(max_length=30, default='', blank=True)
    note32 = models.CharField(max_length=30, default='', blank=True)
    note33 = models.CharField(max_length=30, default='', blank=True)
    note34 = models.CharField(max_length=30, default='', blank=True)
    note35 = models.CharField(max_length=30, default='', blank=True)
    note36 = models.CharField(max_length=30, default='', blank=True)
    note37 = models.CharField(max_length=30, default='', blank=True)
    note38 = models.CharField(max_length=30, default='', blank=True)
    note39 = models.CharField(max_length=30, default='', blank=True)
    note40 = models.CharField(max_length=30, default='', blank=True)
    note41 = models.CharField(max_length=30, default='', blank=True)
    note42 = models.CharField(max_length=30, default='', blank=True)
    note43 = models.CharField(max_length=30, default='', blank=True)
    note44 = models.CharField(max_length=30, default='', blank=True)
    note45 = models.CharField(max_length=30, default='', blank=True)
    note46 = models.CharField(max_length=30, default='', blank=True)
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
        verbose_name = 'Solution 6x6'
        verbose_name_plural = 'Solutions 6x6'

    objects = models.Manager()  # for the editor only


class Solution4x4(models.Model):

    """ A solution contains up 16 Piece2x2 in the center

        Piece numbering starts in top-left with nr1, fills 1 row and then continues on the next row

         1  2   3  4  5  6   7  8
         9 10  11 12 13 14  15 16

        17 18  19 20 21 22  23 24
        25 26  27 28 29 30  31 32
        33 34  35 36 37 38  39 40
        41 42  43 44 45 46  47 48

        49 50  51 52 53 54  55 56
        57 58  59 60 61 62  63 64
    """

    when = models.DateTimeField(auto_now_add=True)

    # was this 4x4 processed further into an 6x6?
    processor = models.PositiveIntegerField(default=0)
    is_processed = models.BooleanField(default=False)

    # 2x2 pieces used to build up this piece
    nr19 = models.PositiveIntegerField()
    nr20 = models.PositiveIntegerField()
    nr21 = models.PositiveIntegerField()
    nr22 = models.PositiveIntegerField()

    nr27 = models.PositiveIntegerField()
    nr28 = models.PositiveIntegerField()
    nr29 = models.PositiveIntegerField()
    nr30 = models.PositiveIntegerField()

    nr35 = models.PositiveIntegerField()
    nr36 = models.PositiveIntegerField()
    nr37 = models.PositiveIntegerField()
    nr38 = models.PositiveIntegerField()

    nr43 = models.PositiveIntegerField()
    nr44 = models.PositiveIntegerField()
    nr45 = models.PositiveIntegerField()
    nr46 = models.PositiveIntegerField()

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
    note19 = models.CharField(max_length=30, default='', blank=True)
    note20 = models.CharField(max_length=30, default='', blank=True)
    note21 = models.CharField(max_length=30, default='', blank=True)
    note22 = models.CharField(max_length=30, default='', blank=True)
    note23 = models.CharField(max_length=30, default='', blank=True)
    note24 = models.CharField(max_length=30, default='', blank=True)
    note25 = models.CharField(max_length=30, default='', blank=True)
    note26 = models.CharField(max_length=30, default='', blank=True)
    note27 = models.CharField(max_length=30, default='', blank=True)
    note28 = models.CharField(max_length=30, default='', blank=True)
    note29 = models.CharField(max_length=30, default='', blank=True)
    note30 = models.CharField(max_length=30, default='', blank=True)
    note31 = models.CharField(max_length=30, default='', blank=True)
    note32 = models.CharField(max_length=30, default='', blank=True)
    note33 = models.CharField(max_length=30, default='', blank=True)
    note34 = models.CharField(max_length=30, default='', blank=True)
    note35 = models.CharField(max_length=30, default='', blank=True)
    note36 = models.CharField(max_length=30, default='', blank=True)
    note37 = models.CharField(max_length=30, default='', blank=True)
    note38 = models.CharField(max_length=30, default='', blank=True)
    note39 = models.CharField(max_length=30, default='', blank=True)
    note40 = models.CharField(max_length=30, default='', blank=True)
    note41 = models.CharField(max_length=30, default='', blank=True)
    note42 = models.CharField(max_length=30, default='', blank=True)
    note43 = models.CharField(max_length=30, default='', blank=True)
    note44 = models.CharField(max_length=30, default='', blank=True)
    note45 = models.CharField(max_length=30, default='', blank=True)
    note46 = models.CharField(max_length=30, default='', blank=True)
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
        verbose_name = 'Solution 4x4'
        verbose_name_plural = 'Solutions 4x4'

    objects = models.Manager()  # for the editor only


class Half6(models.Model):

    """ Top-right or bottom-left half segment around a 4x4 

        Border2x8 + Corner + Border2x8

                      p1          c1
                +--+--+--+--+ +--+
                |11 12 13 14| |15|
                +--+--+--+--+ +--+
                 b1 b2 b3 b4  +--+
                           b5 |23|
             type = 12     b6 |31| p2
                           b7 |39|
                           b8 |47|
                              +--+
              +--+
              |18| b8
              |26| b7   type = 34
          p2  |34| b6
              |42| b5
                    b4 b3 b2 b1
              +--+ +--+--+--+--+
              |50| |51 52 53 54|
              +--+ +--+--+--+--+
            c1          p1
    """

    when = models.DateTimeField(auto_now_add=True)

    # was this 6x6 processed further into an 8x8?
    processor = models.PositiveIntegerField(default=0)
    is_processed = models.BooleanField(default=False)       # TODO: not needed

    based_on_4x4 = models.PositiveBigIntegerField()

    # 12=top+right, 34=bottom+left
    type = models.PositiveSmallIntegerField()

    b1 = models.PositiveIntegerField()
    b2 = models.PositiveIntegerField()
    b3 = models.PositiveIntegerField()
    b4 = models.PositiveIntegerField()
    b5 = models.PositiveIntegerField()
    b6 = models.PositiveIntegerField()
    b7 = models.PositiveIntegerField()
    b8 = models.PositiveIntegerField()

    # composite pieces making up this half
    p1 = models.PositiveIntegerField()      # Border2x8 of type 1 / 3
    p2 = models.PositiveIntegerField()      # Border2x8 of type 2 / 4
    c1 = models.PositiveIntegerField()      # Piece2x2 with hint

    # base pieces making up this half
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

    nr13 = models.PositiveSmallIntegerField()
    nr14 = models.PositiveSmallIntegerField()
    nr15 = models.PositiveSmallIntegerField()
    nr16 = models.PositiveSmallIntegerField()


    nr17 = models.PositiveSmallIntegerField()
    nr18 = models.PositiveSmallIntegerField()
    nr19 = models.PositiveSmallIntegerField()
    nr20 = models.PositiveSmallIntegerField()

    nr21 = models.PositiveSmallIntegerField()
    nr22 = models.PositiveSmallIntegerField()
    nr23 = models.PositiveSmallIntegerField()
    nr24 = models.PositiveSmallIntegerField()

    nr25 = models.PositiveSmallIntegerField()
    nr26 = models.PositiveSmallIntegerField()
    nr27 = models.PositiveSmallIntegerField()
    nr28 = models.PositiveSmallIntegerField()

    nr29 = models.PositiveSmallIntegerField()
    nr30 = models.PositiveSmallIntegerField()
    nr31 = models.PositiveSmallIntegerField()
    nr32 = models.PositiveSmallIntegerField()

    nr33 = models.PositiveSmallIntegerField()
    nr34 = models.PositiveSmallIntegerField()
    nr35 = models.PositiveSmallIntegerField()
    nr36 = models.PositiveSmallIntegerField()

    class Meta:
        verbose_name = verbose_name_plural = 'Half6'

        indexes = [
            models.Index(fields=['b1']),
            models.Index(fields=['b2']),
            models.Index(fields=['b3']),
            models.Index(fields=['b4']),
            models.Index(fields=['b5']),
            models.Index(fields=['b6']),
            models.Index(fields=['b7']),
            models.Index(fields=['b8']),
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
            models.Index(fields=['nr13']),
            models.Index(fields=['nr14']),
            models.Index(fields=['nr15']),
            models.Index(fields=['nr16']),
            models.Index(fields=['nr17']),
            models.Index(fields=['nr18']),
            models.Index(fields=['nr19']),
            models.Index(fields=['nr20']),
            models.Index(fields=['nr21']),
            models.Index(fields=['nr22']),
            models.Index(fields=['nr23']),
            models.Index(fields=['nr24']),
            models.Index(fields=['nr25']),
            models.Index(fields=['nr26']),
            models.Index(fields=['nr27']),
            models.Index(fields=['nr28']),
            models.Index(fields=['nr29']),
            models.Index(fields=['nr30']),
            models.Index(fields=['nr31']),
            models.Index(fields=['nr32']),
            models.Index(fields=['nr33']),
            models.Index(fields=['nr34']),
            models.Index(fields=['nr35']),
            models.Index(fields=['nr36']),
        ]

    objects = models.Manager()  # for the editor only


class Quart6(models.Model):

    """ Quart of a 6x6 outer ring
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
    p1 = models.PositiveIntegerField()      # Piece2x2
    c1 = models.PositiveIntegerField()      # Piece2x2 with hint
    p2 = models.PositiveIntegerField()      # Piece2x2

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
        ]

    objects = models.Manager()  # for the editor only


# end of file
