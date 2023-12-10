# -*- coding: utf-8 -*-

#  Copyright (c) 2023 Ramon van der Winkel.
#  All rights reserved.
#  Licensed under BSD-3-Clause-Clear. See LICENSE file for details.


""" A solution contains up to 64 Piece2x2

    Piece numbering starts in top-left with nr1, fills 1 row and then continues on the next row

     1  2  3  4  5  6  7  8
     9 10 11 12 13 14 15 16
    17 18 19 20 21 22 23 24
    25 26 27 28 29 30 31 32
    33 34 35 36 37 38 39 40
    41 42 43 44 45 46 47 48
    49 50 51 52 53 54 55 56
    57 58 59 60 61 62 63 64

    Corner pieces: 1 8 57 64
    Border pieces: 2 3 4 5 6 7 9  16 24 32 40 47 56  17 25 33 41 49 56  58 59 60 61 62 63
    Hints in locations: 10, 15, 36, 50, 55

    10.p1 = 208
    15.p2 = 255
    36.p2 = 139
    50.p3 = 181
    55.p4 = 249
"""

NRS_CORNER = (1, 8, 57, 64)

NRS_BORDER = (2, 3, 4, 5, 6, 7, 16, 24, 32, 40, 48, 56, 9, 17, 25, 33, 41, 49, 58, 59, 60, 61, 62, 63)

NRS_HINTS = (10, 15, 36, 50, 55)

NRS_NEIGHBOURS = dict()     # [nr] = (nr on side1, nr on side2, nr on side3, nr on side4)


for nr in range(1, 64+1):
    NRS_NEIGHBOURS[nr] = (nr - 8, nr + 1, nr + 8, nr - 1)       # side 1, 2, 3, 4
# for

# redo the corners
NRS_NEIGHBOURS[1] = (0, 1 + 1, 1 + 8, 0)
NRS_NEIGHBOURS[8] = (0, 0, 8 + 8, 8 - 1)
NRS_NEIGHBOURS[57] = (57 - 8, 57 + 1, 0, 0)
NRS_NEIGHBOURS[64] = (64 - 8, 0, 0, 64 - 1)

# redo for the borders
for nr in range(2, 7+1):
    NRS_NEIGHBOURS[nr] = (0, nr + 1, nr + 8, nr - 1)
for nr in range(9, 49+1, 8):
    NRS_NEIGHBOURS[nr] = (nr - 8, nr + 1, nr + 8, 0)
for nr in range(16, 56+1, 8):
    NRS_NEIGHBOURS[nr] = (nr - 8, 0, nr + 8, nr - 1)
for nr in range(58, 63+1):
    NRS_NEIGHBOURS[nr] = (nr - 8, nr + 1, 0, nr - 1)


# end of file
