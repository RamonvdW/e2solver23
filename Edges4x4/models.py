# -*- coding: utf-8 -*-

#  Copyright (c) 2023 Ramon van der Winkel.
#  All rights reserved.
#  Licensed under BSD-3-Clause-Clear. See LICENSE file for details.

from django.db import models


class FourSides(models.Model):

    """ a side consisting of 4 consecutive base pieces

        the primary key of this record is a simple number that can be used efficiently in queries
    """

    nr = models.PositiveIntegerField(primary_key=True)

    # see BasePiece for definition
    four_sides = models.CharField(max_length=4, default='XXXX')

    def __str__(self):
        return "[%s] %s" % (self.pk, self.four_sides)

    class Meta:
        verbose_name = verbose_name_plural = 'Four sides'

    objects = models.Manager()  # for the editor only


class Edge4x4(models.Model):

    """ the unique outer edges of a 4 combi of Piece2x2

        each side consists of 4 base piece sides and is given a new simple numeric reference

                 side 1
               +---+---+
               | 1 | 2 |
        side 4 +---+---+ side 2
               | 3 | 4 |
               +---+---+
                 side 3
    """

    nr = models.PositiveIntegerField(primary_key=True)      # max = 2147483647

    # side is a reference to a FourSide
    side1 = models.PositiveIntegerField()       # top
    side2 = models.PositiveIntegerField()       # right
    side3 = models.PositiveIntegerField()       # bottom
    side4 = models.PositiveIntegerField()       # left

    def __str__(self):
        return str(self.pk)

    class Meta:
        verbose_name = 'Edge 4x4'
        verbose_name_plural = 'Edges 4x4'

        indexes = [
            models.Index(fields=['side1']),
            models.Index(fields=['side2']),
            models.Index(fields=['side3']),
            models.Index(fields=['side4']),
        ]

    objects = models.Manager()  # for the editor only


# end of file
