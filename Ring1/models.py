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
        | 9  | 10 | 11 |         | 14 | 15 | 16 |
        +----+----+----+         +----+----+----+
        | 17 | 18 |                   | 23 | 24 |
        +----+----+                   +----+----+
        | 25 |                             | 32 |
        +----+                             +----+
        | 33 |                             | 40 |
        +----+---+                    +----+----+
        | 41 | 42 |                   | 47 | 48 |
        +----+----+----+         +----+----+----+
        | 49 | 50 | 51 |         | 54 | 55 | 56 |
        +----+----+----+----+----+----+----+----+
        | 57 | 58 | 59 | 60 | 61 | 62 | 63 | 64 |
        +----+----+----+----+----+----+----+----+
    """

    nr = models.AutoField(primary_key=True)

    seed = models.PositiveIntegerField(default=0)

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

    # nr36 = models.PositiveIntegerField()

    is_processed = models.BooleanField(default=False)

    def __str__(self):
        return str(self.nr)

    class Meta:
        verbose_name = 'Ring1'

    objects = models.Manager()  # for the editor only


# end of file
