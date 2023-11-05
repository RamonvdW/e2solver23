# -*- coding: utf-8 -*-

#  Copyright (c) 2023 Ramon van der Winkel.
#  All rights reserved.
#  Licensed under BSD-3-Clause-Clear. See LICENSE file for details.

from django.db import models


class FourSides(models.Model):
    """ a side made up from 4 consecutive base pieces

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


class Piece4x4(models.Model):

    """ a 4x4 piece consists of 16 base pieces, each under a certain rotation

        each side consists of 4 base piece sides and is given a new simple numeric

                      side 1
                +---+---+---+---+
                | 1 | 2 | 3 | 4 |
                +---+---+---+---+
                | 5 | 6 | 7 | 8 |
        side 4  +---+---+---+---+ side 2
                | 9 |10 |11 |12 |
                +---+---+---+---+
                |13 |14 |15 |16 |
                +---+---+---+---+
                     side 3
    """

    nr = models.PositiveIntegerField(primary_key=True)      # max = 2147483647

    # the four sides of this 4x4, starting at the top and rotating clockwise
    side1 = models.PositiveIntegerField()       # top
    side2 = models.PositiveIntegerField()       # right
    side3 = models.PositiveIntegerField()       # bottom
    side4 = models.PositiveIntegerField()       # left

    # base pieces used to build up this piece
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

    # number of counter-clockwise rotations of each base piece
    rot1 = models.PositiveSmallIntegerField()
    rot2 = models.PositiveSmallIntegerField()
    rot3 = models.PositiveSmallIntegerField()
    rot4 = models.PositiveSmallIntegerField()
    rot5 = models.PositiveSmallIntegerField()
    rot6 = models.PositiveSmallIntegerField()
    rot7 = models.PositiveSmallIntegerField()
    rot8 = models.PositiveSmallIntegerField()
    rot9 = models.PositiveSmallIntegerField()
    rot10 = models.PositiveSmallIntegerField()
    rot11 = models.PositiveSmallIntegerField()
    rot12 = models.PositiveSmallIntegerField()
    rot13 = models.PositiveSmallIntegerField()
    rot14 = models.PositiveSmallIntegerField()
    rot15 = models.PositiveSmallIntegerField()
    rot16 = models.PositiveSmallIntegerField()

    piece2x2_nr1 = models.PositiveIntegerField()

    def __str__(self):
        return str(self.pk)

    class Meta:
        verbose_name = 'Piece 4x4'
        verbose_name_plural = 'Pieces 4x4'

        indexes = [
            models.Index(fields=['nr1']),
            models.Index(fields=['nr11']),
        ]

    objects = models.Manager()  # for the editor only


# end of file
