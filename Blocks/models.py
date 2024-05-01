# -*- coding: utf-8 -*-

#  Copyright (c) 2023-2024 Ramon van der Winkel.
#  All rights reserved.
#  Licensed under BSD-3-Clause-Clear. See LICENSE file for details.

from django.db import models


class Block2x1(models.Model):

    """
        A Block2x1 consists of two Block

                     side1
              +--------+--------+
              |        |        |
        side4 | block1 | block2 | side2
              |        |        |
              +--------+--------+
                     side3

                      side1
              +----+----+----+----+
              | b1 | b2 | b3 | b4 |
        side4 +----+----+----+----+ side2
              | b8 | b7 | b6 | b5 |
              +----+----+----+----+
                      side3
    """

    nr = models.AutoField(primary_key=True)

    # reference to Block numbers
    block1_nr = models.PositiveIntegerField()
    block2_nr = models.PositiveIntegerField()

    # number of counter-clockwise rotation
    rot1 = models.PositiveSmallIntegerField(default=0)
    rot2 = models.PositiveSmallIntegerField(default=0)

    def __str__(self):
        return str(self.nr)

    class Meta:
        verbose_name = 'Block2x1'

    objects = models.Manager()  # for the editor only


# end of file
