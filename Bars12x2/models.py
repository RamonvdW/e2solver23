# -*- coding: utf-8 -*-

#  Copyright (c) 2023 Ramon van der Winkel.
#  All rights reserved.
#  Licensed under BSD-3-Clause-Clear. See LICENSE file for details.

from django.db import models


class Bar12x2(models.Model):

    """ a bar consists of six Piece2x2 with the hints in the upper right and left corners

       +--+--+--+--+--+--+--+--+--+--+--+--+
       |h1   |     |     |     |     |   h2|
       +  p1 +  p2 +  p3 +  p4 +  p5 +  p6 +
       |     |     |     |     |     |     |
       +--+--+--+--+--+--+--+--+--+--+--+--+

    """

    nr = models.PositiveIntegerField(primary_key=True)      # max = 2147483647

    h1 = models.PositiveSmallIntegerField()
    h2 = models.PositiveSmallIntegerField()

    p1 = models.PositiveIntegerField()      # piece2x2
    p2 = models.PositiveIntegerField()      # piece2x2
    p3 = models.PositiveIntegerField()      # piece2x2
    p4 = models.PositiveIntegerField()      # piece2x2
    p5 = models.PositiveIntegerField()      # piece2x2
    p6 = models.PositiveIntegerField()      # piece2x2

    def __str__(self):
        return str(self.nr)

    class Meta:
        verbose_name = 'Bar12x2'

        indexes = [
            models.Index(fields=['h1']),
            models.Index(fields=['h2']),
            models.Index(fields=['p1']),
            models.Index(fields=['p6']),
        ]

    objects = models.Manager()  # for the editor only


# end of file
