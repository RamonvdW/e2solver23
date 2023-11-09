# -*- coding: utf-8 -*-

#  Copyright (c) 2023 Ramon van der Winkel.
#  All rights reserved.
#  Licensed under BSD-3-Clause-Clear. See LICENSE file for details.

from django.db import models


class Border4x2(models.Model):

    """ a 4x2 piece consists of 8 base pieces, each under a certain rotation
        the four sides start at the top and follow the piece clockwise

                      side1 = border
                +---+---+---+---+
                | 1 | 2 | 3 | 4 |
         side 4 +---+---+---+---+ side 2
                | 5 | 6 | 7 | 8 |
                +---+---+---+---+
                      side 3
    """

    nr = models.PositiveIntegerField(primary_key=True)      # max = 2147483647

    # order: clockwise
    side2 = models.CharField(max_length=2)              # right  (4,8)
    side3 = models.CharField(max_length=4, default='')  # bottom (8,7,6,5)
    side4 = models.CharField(max_length=2)              # left   (5,1)

    # base pieces used to build up this piece
    nr1 = models.PositiveSmallIntegerField()
    nr2 = models.PositiveSmallIntegerField()
    nr3 = models.PositiveSmallIntegerField()
    nr4 = models.PositiveSmallIntegerField()
    nr5 = models.PositiveSmallIntegerField()
    nr6 = models.PositiveSmallIntegerField()
    nr7 = models.PositiveSmallIntegerField()
    nr8 = models.PositiveSmallIntegerField()

    # number of counter-clockwise rotations of each base piece
    rot1 = models.PositiveSmallIntegerField()
    rot2 = models.PositiveSmallIntegerField()
    rot3 = models.PositiveSmallIntegerField()
    rot4 = models.PositiveSmallIntegerField()
    rot5 = models.PositiveSmallIntegerField()
    rot6 = models.PositiveSmallIntegerField()
    rot7 = models.PositiveSmallIntegerField()
    rot8 = models.PositiveSmallIntegerField()

    def __str__(self):
        return str(self.nr)

    class Meta:
        verbose_name = 'Border 4x2'
        verbose_name_plural = 'Borders 4x2'

        indexes = [
            models.Index(fields=['side2']),
            models.Index(fields=['side4']),
        ]

    objects = models.Manager()  # for the editor only


# end of file
