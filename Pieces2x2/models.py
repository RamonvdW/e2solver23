# -*- coding: utf-8 -*-

#  Copyright (c) 2023-2024 Ramon van der Winkel.
#  All rights reserved.
#  Licensed under BSD-3-Clause-Clear. See LICENSE file for details.

from django.db import models


class TwoSide(models.Model):

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


class TwoSideOptions(models.Model):
    """
        For each Piece2x2 location track which possible TwoSide remain a possibility.

        Options are removed when a search concludes there is no solution given for that TwoSide.
    """

    # which instance does this belong to?
    processor = models.PositiveIntegerField(default=0)

    # line segment around the 64 locations
    # in total 72 + 66 = 138 segments exists (due to acceptable overlap of the left and right borders)
    segment = models.PositiveSmallIntegerField()        # max 32767

    # reference to a TwoSide, of which 460 exist
    two_side = models.PositiveSmallIntegerField()       # max 32767


class EvalProgress(models.Model):

    # size of the evaluator: 4, 9, 16, etc.
    eval_size = models.PositiveSmallIntegerField()        # max 32767

    # top-left board location
    eval_loc = models.PositiveSmallIntegerField()         # max 32767

    # which TwoSideOptions is being updated?
    processor = models.PositiveIntegerField()

    # working on which segment?
    segment = models.PositiveSmallIntegerField()        # max 32767

    # how many options left to evaluate in this segment?
    todo_count = models.PositiveSmallIntegerField()     # max 32767
    left_count = models.PositiveSmallIntegerField()     # max 32767

    solve_order = models.CharField(max_length=250)

    # last updated
    updated = models.DateTimeField()


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
    nr3 = models.PositiveSmallIntegerField()    # bottom left
    nr4 = models.PositiveSmallIntegerField()    # bottom right

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


# end of file
