# -*- coding: utf-8 -*-

#  Copyright (c) 2023 Ramon van der Winkel.
#  All rights reserved.
#  Licensed under BSD-3-Clause-Clear. See LICENSE file for details.

from django.db import models


class CornerSolution(models.Model):

    """ a corner solution consists of four Piece4x4; total 64 base pieces.

        +---+---+---+---+
        | 1 |       | 2 |
        +---+       +---+
        |               |
        +               +
        |               |
        +---+       +---+
        | 4 |       | 3 |
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

    # piece4x4 numbers
    nr1 = models.PositiveIntegerField()
    nr2 = models.PositiveIntegerField()
    nr3 = models.PositiveIntegerField()
    nr4 = models.PositiveIntegerField()

    # number of clockwise rotations of each 4x4 piece
    # nr  rot
    #  1   0
    #  2   1
    #  3   2
    #  4   3

    def __str__(self):
        return str(self.nr)

    class Meta:
        verbose_name = 'Corner solution'

        # indexes = [
        #     models.Index(fields=['nr1']),
        #     models.Index(fields=['nr11']),
        # ]

    objects = models.Manager()  # for the editor only


# end of file
