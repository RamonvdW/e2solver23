# -*- coding: utf-8 -*-

#  Copyright (c) 2023-2024 Ramon van der Winkel.
#  All rights reserved.
#  Licensed under BSD-3-Clause-Clear. See LICENSE file for details.

from django.db import models


class BasePiece(models.Model):

    # piece number matching the game: 1..256
    nr = models.PositiveSmallIntegerField(primary_key=True)

    """ side definition:

        frontal view of the colored puzzle piece
        starting at the top, rotating clockwise: top, right, bottom, left

              side 1
               +--+
        side 4 |  | side 2
               +--+
              side 3

    """

    # the four letters A..V encode the side colors; X for the edge
    side1 = models.CharField(max_length=1, default='X')
    side2 = models.CharField(max_length=1, default='X')
    side3 = models.CharField(max_length=1, default='X')
    side4 = models.CharField(max_length=1, default='X')

    def get_side(self, side_nr: int, rot: int) -> str:
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
        return side[0:1]

    def __str__(self):
        return str(self.nr)

    class Meta:
        indexes = [
            models.Index(fields=['side1']),
            models.Index(fields=['side2']),
            models.Index(fields=['side3']),
            models.Index(fields=['side4']),
            models.Index(fields=['side1', 'side2']),
            models.Index(fields=['side2', 'side3']),
            models.Index(fields=['side3', 'side4']),
            models.Index(fields=['side4', 'side1']),
        ]

    objects = models.Manager()  # for the editor only


class Block(models.Model):

    nr = models.PositiveSmallIntegerField(primary_key=True)

    # which base piece (1..256) defined this block?
    base_nr = models.PositiveSmallIntegerField()

    """
        block definition:
        
                 side1   
              +----+----+
              | b1 | b2 |
        side4 +----+----+ side2
              | b4 | b3 |
              +----+----+
                 side3

        sides are defined clockwise:
            side1 = b1 b2
            side2 = b2 b3
            side3 = b3 b4
            side4 = b4 b1

    """

    # the letters A..V encode the block color; X for edge
    # see pieces1x1: INTERNAL_SIDES and INTERNAL_BORDER_SIDES
    b1 = models.CharField(max_length=1, default='X')
    b2 = models.CharField(max_length=1, default='X')
    b3 = models.CharField(max_length=1, default='X')
    b4 = models.CharField(max_length=1, default='X')

    side1 = models.CharField(max_length=2, default='XX')
    side2 = models.CharField(max_length=2, default='XX')
    side3 = models.CharField(max_length=2, default='XX')
    side4 = models.CharField(max_length=2, default='XX')

    def get_side(self, side_nr: int, rot: int) -> str:
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
        return side

    def __str__(self):
        return str(self.nr)

    class Meta:
        indexes = [
            models.Index(fields=['b1']),
            models.Index(fields=['b2']),
            models.Index(fields=['b3']),
            models.Index(fields=['b4']),
            models.Index(fields=['side1']),
            models.Index(fields=['side2']),
            models.Index(fields=['side3']),
            models.Index(fields=['side4']),
            models.Index(fields=['base_nr']),
        ]

    objects = models.Manager()  # for the editor only


# end of file
