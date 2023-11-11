# -*- coding: utf-8 -*-

#  Copyright (c) 2023 Ramon van der Winkel.
#  All rights reserved.
#  Licensed under BSD-3-Clause-Clear. See LICENSE file for details.

from django.db import models


class Ring4(models.Model):

    """ a ring4 solution consists of four 4x4, eight 4x2 and sixteen 2x2


      c1           b1      b2            c2
        +-------+-------+-------+-------+
        |       |  4x2  |  4x2  |       |
        +  4x4  +---+---+---+---+  4x4  +
        |       |2x2|2x2|2x2|2x2|       |
        +---+---+---+---+---+---+---+---+
                  p1  p2  p3  p4
        +---+---+               +---+---+
        |   |2x2|p16          p5|2x2|   |
     b8 |4x2+---+               +---+4x2+ b3
        |   |2x2|p15          p6|2x2|   |
        +---+---+               +---+---+
        |   |2x2|p14          p7|2x2|   |
     b7 |4x2+---+               +---+4x2+ b4
        |   |2x2|p13          p8|2x2|   |
        +---+---+               +---+---+
                 p12 p11 p10 p9
        +---+---+---+---+---+---+---+---+
        |       |2x2|2x2|2x2|2x2|       |
        +  4x4  +---+---+---+---+  4x4  +
        |       |  4x2  |  4x2  |       |
        +-------+-------+-------+-------+
      c4           b6      b5            c3
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

    # each Piece2x2 pre-exists in the 4 possible rotations
    p1 = models.PositiveIntegerField()      # piece2x2
    p2 = models.PositiveIntegerField()      # piece2x2
    p3 = models.PositiveIntegerField()      # piece2x2
    p4 = models.PositiveIntegerField()      # piece2x2
    p5 = models.PositiveIntegerField()      # piece2x2
    p6 = models.PositiveIntegerField()      # piece2x2
    p7 = models.PositiveIntegerField()      # piece2x2
    p8 = models.PositiveIntegerField()      # piece2x2
    p9 = models.PositiveIntegerField()      # piece2x2
    p10 = models.PositiveIntegerField()      # piece2x2
    p11 = models.PositiveIntegerField()      # piece2x2
    p12 = models.PositiveIntegerField()      # piece2x2
    p13 = models.PositiveIntegerField()      # piece2x2
    p14 = models.PositiveIntegerField()      # piece2x2
    p15 = models.PositiveIntegerField()      # piece2x2
    p16 = models.PositiveIntegerField()      # piece2x2

    def __str__(self):
        return str(self.nr)

    class Meta:
        verbose_name = 'Ring4'

    objects = models.Manager()  # for the editor only


# end of file
