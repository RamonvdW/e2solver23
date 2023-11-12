# -*- coding: utf-8 -*-

#  Copyright (c) 2023 Ramon van der Winkel.
#  All rights reserved.
#  Licensed under BSD-3-Clause-Clear. See LICENSE file for details.

from django.db import models


class Corner4(models.Model):

    """ a corner4 solution consists of one 4x4, two 4x2 and two 2x2


      c               b2
        +-------+  +-------+
        |       |  |  4x2  | side2
        +  4x4  +  +---+---+
        |       |  |2x2|
        +---+---+  +---+
                     p2
        +---+---+
        |   |2x2| p1
     b1 |4x2+---+
        |   |
        +---+
        side3
    """

    nr = models.PositiveIntegerField(primary_key=True)      # max = 2147483647

    # (c is not used)
    c = models.PositiveIntegerField()       # piece4x4

    b1 = models.PositiveIntegerField()      # border4x2
    b2 = models.PositiveIntegerField()      # border4x2

    # note: each Piece2x2 does exist in 4 possible rotations
    p1 = models.PositiveIntegerField()      # piece2x2
    p2 = models.PositiveIntegerField()      # piece2x2

    def __str__(self):
        return str(self.nr)

    class Meta:
        verbose_name = 'Corner4'

    objects = models.Manager()  # for the editor only


# end of file
