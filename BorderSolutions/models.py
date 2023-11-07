# -*- coding: utf-8 -*-

#  Copyright (c) 2023 Ramon van der Winkel.
#  All rights reserved.
#  Licensed under BSD-3-Clause-Clear. See LICENSE file for details.

from django.db import models


class BorderSolution(models.Model):

    """ a corner solution consists of four Piece4x4; total 64 base pieces.

         4x4 4x2 4x2 4x4
        +---+---+---+---+
        | 1 |+--+--+| 2 |  4x4
        +---+       +---+
        | +           + |  4x2
        + +           + +
        | +           + |  4x2
        +---+       +---+
        | 4 |+++++++| 3 |  4x4
        +---+---+---+---+

        The corner is in position 1
        The hint is in position 11

        +---+---+---+---+
        | 1 | 2 | 3 | 4 |
        +---+---+---+---+
        | 5 | 6 | 7 | 8 |
        +---+---+---+---+
        | 9 |10 |11 |12 |
        +---+---+---+---+
        |13 |14 |15 |16 |
        +---+---+---+---+

    """

    nr = models.PositiveIntegerField(primary_key=True)      # max = 2147483647

    # clockwise starting in the top-left:
    #   c1, b1, b2, c2, b3, b4, c3, b5, b6, c4, b7, b8

    c1 = models.PositiveIntegerField()      # piece4x4
    c2 = models.PositiveIntegerField()      # piece4x4
    c3 = models.PositiveIntegerField()      # piece4x4
    c4 = models.PositiveIntegerField()      # piece4x4

    b1 = models.PositiveIntegerField()      # border4x2
    b2 = models.PositiveIntegerField()      # border4x2
    b3 = models.PositiveIntegerField()      # border4x2
    b4 = models.PositiveIntegerField()      # border4x2
    b5 = models.PositiveIntegerField()      # border4x2
    b6 = models.PositiveIntegerField()      # border4x2
    b7 = models.PositiveIntegerField()      # border4x2
    b8 = models.PositiveIntegerField()      # border4x2

    def __str__(self):
        return str(self.nr)

    class Meta:
        verbose_name = 'Border solution'

    objects = models.Manager()  # for the editor only


# end of file
