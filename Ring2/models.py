# -*- coding: utf-8 -*-

#  Copyright (c) 2024 Ramon van der Winkel.
#  All rights reserved.
#  Licensed under BSD-3-Clause-Clear. See LICENSE file for details.

from django.db import models


class Ring2(models.Model):

    """ the outer 2 rings of 2x2 piece

        +----+----+----+----+----+----+----+----+
        |  1 |  2 |  3 |  4 |  5 |  6 |  7 |  8 |
        +----+----+----+----+----+----+----+----+
        |  9 | 10 | 11 | 12 | 13 | 14 | 15 | 16 |
        +----+----+----+----+----+----+----+----+
        | 17 | 18 |                   | 23 | 24 |
        +----+----+                   +----+----+
        | 25 | 26 |                   | 31 | 32 |
        +----+---+                    +----+----+
        | 33 | 34 |                   | 39 | 40 |
        +----+----+                   +----+----+
        | 41 | 42 |                   | 47 | 48 |
        +----+----+----+----+----+----+----+----+
        | 49 | 50 | 51 | 52 | 53 | 54 | 55 | 56 |
        +----+----+----+----+----+----+----+----+
        | 57 | 58 | 59 | 60 | 61 | 62 | 63 | 64 |
        +----+----+----+----+----+----+----+----+
    """

    nr = models.AutoField(primary_key=True)

    based_on_ring1 = models.PositiveIntegerField(default=0)

    # reference to Piece2x2 numbers
    loc1 = models.PositiveIntegerField(default=0)
    loc2 = models.PositiveIntegerField(default=0)
    loc3 = models.PositiveIntegerField(default=0)
    loc4 = models.PositiveIntegerField(default=0)
    loc5 = models.PositiveIntegerField(default=0)
    loc6 = models.PositiveIntegerField(default=0)
    loc7 = models.PositiveIntegerField(default=0)
    loc8 = models.PositiveIntegerField(default=0)

    loc9 = models.PositiveIntegerField(default=0)
    loc10 = models.PositiveIntegerField(default=0)
    loc11 = models.PositiveIntegerField(default=0)
    loc12 = models.PositiveIntegerField(default=0)
    loc13 = models.PositiveIntegerField(default=0)
    loc14 = models.PositiveIntegerField(default=0)
    loc15 = models.PositiveIntegerField(default=0)
    loc16 = models.PositiveIntegerField(default=0)

    loc17 = models.PositiveIntegerField(default=0)
    loc18 = models.PositiveIntegerField(default=0)
    loc23 = models.PositiveIntegerField(default=0)
    loc24 = models.PositiveIntegerField(default=0)

    loc25 = models.PositiveIntegerField(default=0)
    loc26 = models.PositiveIntegerField(default=0)
    loc31 = models.PositiveIntegerField(default=0)
    loc32 = models.PositiveIntegerField(default=0)

    loc33 = models.PositiveIntegerField(default=0)
    loc34 = models.PositiveIntegerField(default=0)
    loc39 = models.PositiveIntegerField(default=0)
    loc40 = models.PositiveIntegerField(default=0)

    loc41 = models.PositiveIntegerField(default=0)
    loc42 = models.PositiveIntegerField(default=0)
    loc47 = models.PositiveIntegerField(default=0)
    loc48 = models.PositiveIntegerField(default=0)

    loc49 = models.PositiveIntegerField(default=0)
    loc50 = models.PositiveIntegerField(default=0)
    loc51 = models.PositiveIntegerField(default=0)
    loc52 = models.PositiveIntegerField(default=0)
    loc53 = models.PositiveIntegerField(default=0)
    loc54 = models.PositiveIntegerField(default=0)
    loc55 = models.PositiveIntegerField(default=0)
    loc56 = models.PositiveIntegerField(default=0)

    loc57 = models.PositiveIntegerField(default=0)
    loc58 = models.PositiveIntegerField(default=0)
    loc59 = models.PositiveIntegerField(default=0)
    loc60 = models.PositiveIntegerField(default=0)
    loc61 = models.PositiveIntegerField(default=0)
    loc62 = models.PositiveIntegerField(default=0)
    loc63 = models.PositiveIntegerField(default=0)
    loc64 = models.PositiveIntegerField(default=0)

    is_processed = models.BooleanField(default=False)

    def __str__(self):
        return str(self.nr)

    class Meta:
        verbose_name = 'Ring2'

    objects = models.Manager()  # for the editor only


# end of file
