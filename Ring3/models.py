# -*- coding: utf-8 -*-

#  Copyright (c) 2024 Ramon van der Winkel.
#  All rights reserved.
#  Licensed under BSD-3-Clause-Clear. See LICENSE file for details.

from django.db import models


class Ring3(models.Model):

    """ the third ring of 2x2 pieces
        +----+----+----+----+----+----+----+----+
        |    |    |    |    |    |    |    |    |
        +----+----+----+----+----+----+----+----+
        |    |    |    |    |    |    |    |    |
        +----+----+----+----+----+----+----+----+
        |    |    | 19 | 20 | 21 | 22 |    |    |
        +----+----+----+----+----+----+----+----+
        |    |    | 27 |    |    | 30 |    |    |
        +----+----+----+----+----+----+----+----+
        |    |    | 35 |    |    | 38 |    |    |
        +----+----+----+----+----+----+----+----+
        |    |    | 43 | 44 | 45 | 46 |    |    |
        +----+----+----+----+----+----+----+----+
        |    |    |    |  Ring2  |    |    |    |
        +----+----+----+----+----+----+----+----+
        |    |    |    |  Ring1  |    |    |    |
        +----+----+----+----+----+----+----+----+
    """

    nr = models.AutoField(primary_key=True)

    # reference to Piece2x2 numbers
    loc19 = models.PositiveIntegerField(default=0)
    loc20 = models.PositiveIntegerField(default=0)
    loc21 = models.PositiveIntegerField(default=0)
    loc22 = models.PositiveIntegerField(default=0)
    loc27 = models.PositiveIntegerField(default=0)
    loc30 = models.PositiveIntegerField(default=0)
    loc35 = models.PositiveIntegerField(default=0)
    loc38 = models.PositiveIntegerField(default=0)
    loc43 = models.PositiveIntegerField(default=0)
    loc44 = models.PositiveIntegerField(default=0)
    loc45 = models.PositiveIntegerField(default=0)
    loc46 = models.PositiveIntegerField(default=0)

    def __str__(self):
        return str(self.nr)

    class Meta:
        verbose_name = 'Ring3'

    objects = models.Manager()  # for the editor only


# end of file
