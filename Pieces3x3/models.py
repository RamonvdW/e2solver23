# -*- coding: utf-8 -*-

#  Copyright (c) 2024 Ramon van der Winkel.
#  All rights reserved.
#  Licensed under BSD-3-Clause-Clear. See LICENSE file for details.

from django.db import models


class Piece3x3(models.Model):

    """ a 3x3 piece consists of 9 base pieces, each under a certain rotation

        each side consists of 2 base piece sides and is given a new simple numeric reference

                   side 1
               +---+---+---+
               | 1 | 2 | 3 |
               +---+---+---+
        side 4 | 4 | 5 | 6 | side 2
               +---+---+---+
               | 7 | 8 | 9 |
               +---+---+---+
                   side 3
    """

    nr = models.PositiveIntegerField(primary_key=True)      # max = 2147483647

    is_border = models.BooleanField()
    has_hint = models.BooleanField()

    # side is a reference to a ThreeSide
    side1 = models.PositiveIntegerField()       # top
    side2 = models.PositiveIntegerField()       # right
    side3 = models.PositiveIntegerField()       # bottom
    side4 = models.PositiveIntegerField()       # left

    # base pieces used to build up this piece
    nr1 = models.PositiveSmallIntegerField()    # top left
    nr2 = models.PositiveSmallIntegerField()    # top right
    nr3 = models.PositiveSmallIntegerField()    # bottom right
    nr4 = models.PositiveSmallIntegerField()    # bottom left
    nr5 = models.PositiveSmallIntegerField()    # bottom left
    nr6 = models.PositiveSmallIntegerField()    # bottom left
    nr7 = models.PositiveSmallIntegerField()    # bottom left
    nr8 = models.PositiveSmallIntegerField()    # bottom left
    nr9 = models.PositiveSmallIntegerField()    # bottom left

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

    def get_side(self, side_nr: int, rot: int) -> int:
        """
            rot = number of counterclockwise rotations (0..3)

            rot  side_nr=1  2  3  4
            ---          ----------
             0           1  2  3  4
             1           2  3  4  1
             2           3  4  1  2
             3           4  1  2  3

            rot+side_nr  return
             1           side1
             2           side2
             3           side3
             4           side4
             5           side1
             6           side2
             7           side3
        """
        side_nr += rot
        if side_nr in (1, 5):
            side = self.side1
        elif side_nr in (2, 6):
            side = self.side2
        elif side_nr in (3, 7):
            side = self.side3
        else:
            side = self.side4
        return int(side)

    def __str__(self):
        return str(self.pk)

    class Meta:
        verbose_name = 'Piece 3x3'
        verbose_name_plural = 'Pieces 3x3'

        indexes = [
            models.Index(fields=['is_border']),
            models.Index(fields=['has_hint']),
            models.Index(fields=['nr1']),
            models.Index(fields=['nr2']),
            models.Index(fields=['nr3']),
            models.Index(fields=['nr4']),
            models.Index(fields=['nr5']),
            models.Index(fields=['nr6']),
            models.Index(fields=['nr7']),
            models.Index(fields=['nr8']),
            models.Index(fields=['nr9']),
            models.Index(fields=['side1']),
            models.Index(fields=['side2']),
            models.Index(fields=['side3']),
            models.Index(fields=['side4']),
        ]

    objects = models.Manager()  # for the editor only

# end of file
