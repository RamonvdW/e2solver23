# -*- coding: utf-8 -*-

#  Copyright (c) 2023-2024 Ramon van der Winkel.
#  All rights reserved.
#  Licensed under BSD-3-Clause-Clear. See LICENSE file for details.

# 208: top left
# 181: bottom left
# 249: bottom right
# 255: top right
# 139: center

ALL_HINT_NRS = (139, 181, 208, 249, 255)

ALL_CORNER_NRS = (1, 2, 3, 4)

# required number of counter-clockwise rotations of each hint piece
ALL_HINT_ROTS = {
    139: 2,
    181: 1,
    208: 1,
    249: 0,
    255: 1
}

ALL_HINT_SIDES = {
    139: ('R', 'F'),        # side1__endswith, side2__startswith
    181: ('U', 'K'),        # side3__endswith, side4__startswith
    208: ('S', 'V'),        # side3__endswith, side1__startswith
    249: ('U', 'O'),        # side2__endswith, side3__startswith
    255: ('V', 'T'),        # side1__endswith, side2__startswith
}

# hints are located in the corners of the third ring in
# or diagonally: in 2 from each corner
HINT_NRS = (181, 208, 249, 255)

CENTER_NR = 139
CENTER_ROT = 2      # yellow side up
CENTER_XY = (7, 8)  # 0-based: 8th column, 9th row

# end of file
