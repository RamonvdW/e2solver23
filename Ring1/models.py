# -*- coding: utf-8 -*-

#  Copyright (c) 2023-2024 Ramon van der Winkel.
#  All rights reserved.
#  Licensed under BSD-3-Clause-Clear. See LICENSE file for details.

from django.db import models


class Ring1(models.Model):

    """ the outer (first) ring of 2x2 piece

        +----+----+----+----+----+----+----+----+
        | 1  | 2  | 3  | 4  | 5  | 6  | 7  | 8  |
        +----+----+----+----+----+----+----+----+
        | 9  |                             | 16 |
        +----+                             +----+
        | 17 |                             | 24 |
        +----+                             +----+
        | 25 |                             | 32 |
        +----+                             +----+
        | 33 |                             | 40 |
        +----+                             +----+
        | 41 |                             | 48 |
        +----+                             +----+
        | 49 |                             | 56 |
        +----+----+----+----+----+----+----+----+
        | 57 | 58 | 59 | 60 | 61 | 62 | 63 | 64 |
        +----+----+----+----+----+----+----+----+
    """

    nr = models.AutoField(primary_key=True)

    # which instance is processing this?
    processor = models.PositiveIntegerField(default=0)
    is_processed = models.BooleanField(default=False)

    # reference to Piece2x2 numbers
    nr1 = models.PositiveIntegerField()
    nr2 = models.PositiveIntegerField()
    nr3 = models.PositiveIntegerField()
    nr4 = models.PositiveIntegerField()
    nr5 = models.PositiveIntegerField()
    nr6 = models.PositiveIntegerField()
    nr7 = models.PositiveIntegerField()
    nr8 = models.PositiveIntegerField()

    nr9 = models.PositiveIntegerField()
    nr16 = models.PositiveIntegerField()
    nr17 = models.PositiveIntegerField()
    nr24 = models.PositiveIntegerField()
    nr25 = models.PositiveIntegerField()
    nr32 = models.PositiveIntegerField()
    nr33 = models.PositiveIntegerField()
    nr40 = models.PositiveIntegerField()
    nr41 = models.PositiveIntegerField()
    nr48 = models.PositiveIntegerField()
    nr49 = models.PositiveIntegerField()
    nr56 = models.PositiveIntegerField()

    nr57 = models.PositiveIntegerField()
    nr58 = models.PositiveIntegerField()
    nr59 = models.PositiveIntegerField()
    nr60 = models.PositiveIntegerField()
    nr61 = models.PositiveIntegerField()
    nr62 = models.PositiveIntegerField()
    nr63 = models.PositiveIntegerField()
    nr64 = models.PositiveIntegerField()

    nr10 = models.PositiveIntegerField()
    nr11 = models.PositiveIntegerField()
    nr18 = models.PositiveIntegerField()

    nr14 = models.PositiveIntegerField()
    nr15 = models.PositiveIntegerField()
    nr23 = models.PositiveIntegerField()

    nr42 = models.PositiveIntegerField()
    nr50 = models.PositiveIntegerField()
    nr51 = models.PositiveIntegerField()

    nr47 = models.PositiveIntegerField()
    nr54 = models.PositiveIntegerField()
    nr55 = models.PositiveIntegerField()

    nr36 = models.PositiveIntegerField()

    def __str__(self):
        return str(self.nr)

    class Meta:
        verbose_name = 'Ring1'

    objects = models.Manager()  # for the editor only


class Corner1(models.Model):

    """ the first corner that can make up a Ring1

        +----+----+----+----+
        | 1  | 2  | 3  | 4  |
        +----+----+----+----+
        | 9  | 10 | 11 |
        +----+----+----+
        | 17 | 18 |
        +----+----+
        | 25 |
        +----+
    """

    nr = models.AutoField(primary_key=True)

    side3 = models.PositiveIntegerField()       # loc25 side3
    side2 = models.PositiveIntegerField()       # loc4 side2

    # reference to Piece2x2 numbers
    loc1 = models.PositiveIntegerField()
    loc2 = models.PositiveIntegerField()
    loc3 = models.PositiveIntegerField()
    loc4 = models.PositiveIntegerField()

    loc9 = models.PositiveIntegerField()
    loc10 = models.PositiveIntegerField()
    loc11 = models.PositiveIntegerField()

    loc17 = models.PositiveIntegerField()
    loc18 = models.PositiveIntegerField()

    loc25 = models.PositiveIntegerField()

    # 40 base pieces used for the 10 locations
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
    nr37 = models.PositiveSmallIntegerField()
    nr38 = models.PositiveSmallIntegerField()
    nr39 = models.PositiveSmallIntegerField()
    nr40 = models.PositiveSmallIntegerField()

    def __str__(self):
        return str(self.nr)

    class Meta:
        verbose_name = 'Corner1'

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
            models.Index(fields=['nr37']),
            models.Index(fields=['nr38']),
            models.Index(fields=['nr39']),
            models.Index(fields=['nr40']),
        ]

    objects = models.Manager()  # for the editor only


class Corner2(models.Model):

    """ the second corner that can make up a Ring1

        +----+----+----+----+
        | 5  | 6  | 7  | 8  |
        +----+----+----+----+
             | 14 | 15 | 16 |
             +----+----+----+
                  | 23 | 24 |
                  +----+----+
                       | 32 |
                       +----+
    """

    nr = models.AutoField(primary_key=True)

    side4 = models.PositiveIntegerField()       # loc5 side4
    side3 = models.PositiveIntegerField()       # loc32 side3

    # reference to Piece2x2 numbers
    loc5 = models.PositiveIntegerField()
    loc6 = models.PositiveIntegerField()
    loc7 = models.PositiveIntegerField()
    loc8 = models.PositiveIntegerField()

    loc14 = models.PositiveIntegerField()
    loc15 = models.PositiveIntegerField()
    loc16 = models.PositiveIntegerField()

    loc23 = models.PositiveIntegerField()
    loc24 = models.PositiveIntegerField()

    loc32 = models.PositiveIntegerField()

    # 40 base pieces used for the 10 locations
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
    nr37 = models.PositiveSmallIntegerField()
    nr38 = models.PositiveSmallIntegerField()
    nr39 = models.PositiveSmallIntegerField()
    nr40 = models.PositiveSmallIntegerField()

    def __str__(self):
        return str(self.nr)

    class Meta:
        verbose_name = 'Corner2'

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
            models.Index(fields=['nr37']),
            models.Index(fields=['nr38']),
            models.Index(fields=['nr39']),
            models.Index(fields=['nr40']),
        ]

    objects = models.Manager()  # for the editor only


class Corner3(models.Model):

    """ the third corner that can make up a Ring1

                       +----+
                       | 40 |
                  +----+----+
                  | 47 | 48 |
             +----+----+----+
             | 54 | 55 | 56 |
        +----+----+----+----+
        | 61 | 62 | 63 | 64 |
        +----+----+----+----+
    """

    nr = models.AutoField(primary_key=True)

    side1 = models.PositiveIntegerField()       # loc40 side1
    side4 = models.PositiveIntegerField()       # loc61 side4

    # reference to Piece2x2 numbers
    loc40 = models.PositiveIntegerField()

    loc47 = models.PositiveIntegerField()
    loc48 = models.PositiveIntegerField()

    loc54 = models.PositiveIntegerField()
    loc55 = models.PositiveIntegerField()
    loc56 = models.PositiveIntegerField()

    loc61 = models.PositiveIntegerField()
    loc62 = models.PositiveIntegerField()
    loc63 = models.PositiveIntegerField()
    loc64 = models.PositiveIntegerField()

    # 40 base pieces used for the 10 locations
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
    nr37 = models.PositiveSmallIntegerField()
    nr38 = models.PositiveSmallIntegerField()
    nr39 = models.PositiveSmallIntegerField()
    nr40 = models.PositiveSmallIntegerField()

    def __str__(self):
        return str(self.nr)

    class Meta:
        verbose_name = 'Corner3'

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
            models.Index(fields=['nr37']),
            models.Index(fields=['nr38']),
            models.Index(fields=['nr39']),
            models.Index(fields=['nr40']),
        ]

    objects = models.Manager()  # for the editor only


class Corner4(models.Model):

    """ the fourth corner that can make up a Ring1

        +----+
        | 33 |
        +----+----+
        | 41 | 42 |
        +----+----+----+
        | 49 | 50 | 51 |
        +----+----+----+----+
        | 57 | 58 | 59 | 60 |
        +----+----+----+----+
    """

    nr = models.AutoField(primary_key=True)

    side2 = models.PositiveIntegerField()       # loc60 side2
    side1 = models.PositiveIntegerField()       # loc33 side1

    # reference to Piece2x2 numbers
    loc33 = models.PositiveIntegerField()

    loc41 = models.PositiveIntegerField()
    loc42 = models.PositiveIntegerField()

    loc49 = models.PositiveIntegerField()
    loc50 = models.PositiveIntegerField()
    loc51 = models.PositiveIntegerField()

    loc57 = models.PositiveIntegerField()
    loc58 = models.PositiveIntegerField()
    loc59 = models.PositiveIntegerField()
    loc60 = models.PositiveIntegerField()

    # 40 base pieces used for the 10 locations
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
    nr37 = models.PositiveSmallIntegerField()
    nr38 = models.PositiveSmallIntegerField()
    nr39 = models.PositiveSmallIntegerField()
    nr40 = models.PositiveSmallIntegerField()

    def __str__(self):
        return str(self.nr)

    class Meta:
        verbose_name = 'Corner4'

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
            models.Index(fields=['nr37']),
            models.Index(fields=['nr38']),
            models.Index(fields=['nr39']),
            models.Index(fields=['nr40']),
        ]

    objects = models.Manager()  # for the editor only


# end of file
