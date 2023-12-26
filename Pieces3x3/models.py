# -*- coding: utf-8 -*-

#  Copyright (c) 2023 Ramon van der Winkel.
#  All rights reserved.
#  Licensed under BSD-3-Clause-Clear. See LICENSE file for details.

from django.db import models


class ThreeSide(models.Model):

    """ a side consisting of 3 consecutive base pieces

        the primary key of this record is a simple number that can be used efficiently in queries
    """

    nr = models.PositiveIntegerField(primary_key=True)

    # see BasePiece for definition
    three_sides = models.CharField(max_length=3, default='XXX')

    def __str__(self):
        return "[%s] %s" % (self.pk, self.three_sides)

    class Meta:
        verbose_name = verbose_name_plural = 'Three sides'

    objects = models.Manager()  # for the editor only


class Piece3x3(models.Model):

    """ a 3x3 piece consists of 9 base pieces, each under a certain rotation

        each side consists of 3 base piece sides and is given a new simple numeric reference

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

    has_hint = models.BooleanField()

    # side is a reference to a ThreeSide
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

    def get_nr_rot(self, pos: int, rot: int) -> (int, int):
        """
            rot = number of counterclockwise rotations (0..3)

            pos =
               +---+---+---+
               | 1 | 2 | 3 |
               +---+---+---+
               | 4 | 5 | 6 |
               +---+---+---+
               | 7 | 8 | 9 |
               +---+---+---+

            rot  pos=1  2  3  4  5  6  7  8  9
            ---      -------------------------
             0       1  2  3  4  5  6  7  8  9  nr
             1       3  6  9  2  5  8  1  4  7
             2       9  8  7  6  5  4  3  2  1
             3       7  4  1  8  5  2  9  6  3

            base piece rotation correction:

            rot  extra rotation
            ---  --------------
             0   0
             1   1
             2   2
             3   3
        """
        pos -= 1
        if rot == 0:
            nr, rot = ((self.nr1, self.rot1), (self.nr2, self.rot2), (self.nr3, self.rot3), (self.nr4, self.rot4),
                       (self.nr5, self.rot5),
                       (self.nr6, self.rot6), (self.nr7, self.rot7), (self.nr8, self.rot8), (self.nr9, self.rot9))[pos]
        elif rot == 1:
            nr, rot = ((self.nr3, self.rot3), (self.nr6, self.rot6), (self.nr9, self.rot9), (self.nr2, self.rot2),
                       (self.nr5, self.rot5),
                       (self.nr8, self.rot8), (self.nr1, self.rot1), (self.nr4, self.rot4), (self.nr7, self.rot7))[pos]
            rot += 1
        elif rot == 2:
            nr, rot = ((self.nr9, self.rot9), (self.nr8, self.rot8), (self.nr7, self.rot7), (self.nr6, self.rot6),
                       (self.nr5, self.rot5),
                       (self.nr4, self.rot4), (self.nr3, self.rot3), (self.nr2, self.rot2), (self.nr1, self.rot1))[pos]
            rot += 2
        else:
            nr, rot = ((self.nr7, self.rot7), (self.nr4, self.rot4), (self.nr1, self.rot1), (self.nr8, self.rot8),
                       (self.nr5, self.rot5),
                       (self.nr2, self.rot2), (self.nr9, self.rot9), (self.nr6, self.rot6), (self.nr3, self.rot3))[pos]
            rot += 3
        return nr, rot % 4

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
