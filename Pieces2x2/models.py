# -*- coding: utf-8 -*-

#  Copyright (c) 2023 Ramon van der Winkel.
#  All rights reserved.
#  Licensed under BSD-3-Clause-Clear. See LICENSE file for details.

from django.db import models


class TwoSides(models.Model):

    """ a side consisting of 2 consecutive base pieces

        the primary key of this record is a simple number that can be used efficiently in queries
    """

    nr = models.PositiveIntegerField(primary_key=True)

    # see BasePiece for definition
    two_sides = models.CharField(max_length=2, default='XX')

    def __str__(self):
        return "[%s] %s" % (self.pk, self.two_sides)

    class Meta:
        verbose_name = verbose_name_plural = 'Two sides'

    objects = models.Manager()  # for the editor only


# TODO: Beware that Piece2x2 might be a subset with the hint pieces, used to generate the corners 4x4

class Piece2x2(models.Model):

    """ a 2x2 piece consists of 4 base pieces, each under a certain rotation

        each side consists of 2 base piece sides and is given a new simple numeric reference

                 side 1
               +---+---+
               | 1 | 2 |
        side 4 +---+---+ side 2
               | 3 | 4 |
               +---+---+
                 side 3
    """

    nr = models.PositiveIntegerField(primary_key=True)      # max = 2147483647

    is_border = models.BooleanField()
    has_hint = models.BooleanField()

    # side is a reference to a TwoSide
    side1 = models.PositiveIntegerField()       # top
    side2 = models.PositiveIntegerField()       # right
    side3 = models.PositiveIntegerField()       # bottom
    side4 = models.PositiveIntegerField()       # left

    # base pieces used to build up this piece
    nr1 = models.PositiveSmallIntegerField()    # top left
    nr2 = models.PositiveSmallIntegerField()    # top right
    nr3 = models.PositiveSmallIntegerField()    # bottom right
    nr4 = models.PositiveSmallIntegerField()    # bottom left

    # number of counter-clockwise rotations of each base piece
    rot1 = models.PositiveSmallIntegerField()
    rot2 = models.PositiveSmallIntegerField()
    rot3 = models.PositiveSmallIntegerField()
    rot4 = models.PositiveSmallIntegerField()

    def get_nr_rot(self, pos: int, rot: int) -> (int, int):
        """
            rot = number of counterclockwise rotations (0..3)

            pos =
               +---+---+
               | 1 | 2 |
               +---+---+
               | 3 | 4 |
               +---+---+

            rot  pos=1  2  3  4
            ---      ----------
             0       1  2  3  4  nr
             1       2  4  1  3
             2       4  3  2  1
             3       3  1  4  2

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
            nr, rot = ((self.nr1, self.rot1), (self.nr2, self.rot2), (self.nr3, self.rot3), (self.nr4, self.rot4))[pos]
        elif rot == 1:
            nr, rot = ((self.nr2, self.rot2), (self.nr4, self.rot4), (self.nr1, self.rot1), (self.nr3, self.rot3))[pos]
            rot += 1
        elif rot == 2:
            nr, rot = ((self.nr4, self.rot4), (self.nr3, self.rot3), (self.nr2, self.rot2), (self.nr1, self.rot1))[pos]
            rot += 2
        else:
            nr, rot = ((self.nr3, self.rot3), (self.nr1, self.rot1), (self.nr4, self.rot4), (self.nr2, self.rot2))[pos]
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
        verbose_name = 'Piece 2x2'
        verbose_name_plural = 'Pieces 2x2'

        indexes = [
            models.Index(fields=['is_border']),
            models.Index(fields=['has_hint']),
            models.Index(fields=['nr1']),
            models.Index(fields=['nr2']),
            models.Index(fields=['nr3']),
            models.Index(fields=['nr4']),
            models.Index(fields=['side1']),
            models.Index(fields=['side2']),
            models.Index(fields=['side3']),
            models.Index(fields=['side4']),
        ]

    objects = models.Manager()  # for the editor only


class Block2x8(models.Model):

    """ Block2x4 consists of four Piece2x2 with matching internal sides

        type=1 (fits side1 of the Solution4x4)

                +----+----+----+----+
          side4 | p1 | p2 | p3 | p4 | side2
                +----+----+----+----+
      big side    b1   b2   b3   b4


        OR:

        type=2 (fits side2 of the Solution4x4)

                 side1
                +----+
             b1 | p1 |
                +----+
             b2 | p2 |
       side4    +----+
             b3 | p3 |
                +----+
             b4 | p4 |
                +----+
                 side3


        OR:

        type=3 (fits side3 of the Solution4x4)

      big side    b4   b3   b2   b1
                +----+----+----+----+
          side4 | p4 | p3 | p2 | p1 | side2
                +----+----+----+----+

        OR:

        type=4 (fits side4 of the Solution4x4)
                 side1
                +----+
                | p4 | b4
                +----+
                | p3 | b3
                +----+    side2
                | p2 | b2
                +----+
                | p1 | b1
                +----+
                 side3

    """

    # belongs to which instance? (avoids conflicts)
    processor = models.PositiveIntegerField()

    # 1=top, 2=right, 3=bottom, 4=left
    type = models.PositiveSmallIntegerField()

    # 2x2 pieces used to build up this piece
    p1 = models.PositiveIntegerField()
    p2 = models.PositiveIntegerField()
    p3 = models.PositiveIntegerField()
    p4 = models.PositiveIntegerField()

    # side is a reference to a TwoSide
    side1 = models.PositiveIntegerField()       # top
    side2 = models.PositiveIntegerField()       # right
    side3 = models.PositiveIntegerField()       # bottom
    side4 = models.PositiveIntegerField()       # left

    b1 = models.PositiveIntegerField()
    b2 = models.PositiveIntegerField()
    b3 = models.PositiveIntegerField()
    b4 = models.PositiveIntegerField()

    # all 4x2x2=16 base pieces that make up this block
    # (only intended for filtering)
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

    class Meta:
        verbose_name = 'Block 2x8'
        verbose_name_plural = 'Blocks 2x8'

        indexes = [
            models.Index(fields=['b1']),
            models.Index(fields=['b2']),
            models.Index(fields=['b3']),
            models.Index(fields=['b4']),
            models.Index(fields=['nr1']),
            models.Index(fields=['nr2']),
            models.Index(fields=['nr3']),
            models.Index(fields=['nr4']),
            models.Index(fields=['nr5']),
            models.Index(fields=['nr6']),
            models.Index(fields=['nr7']),
            models.Index(fields=['nr8']),
            models.Index(fields=['nr9']),
            models.Index(fields=['nr10']),
            models.Index(fields=['nr11']),
            models.Index(fields=['nr12']),
            models.Index(fields=['nr13']),
            models.Index(fields=['nr14']),
            models.Index(fields=['nr15']),
            models.Index(fields=['nr16']),
        ]



# end of file
