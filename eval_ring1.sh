#!/bin/bash

#  Copyright (c) 2024 Ramon van der Winkel.
#  All rights reserved.
#  Licensed under BSD-3-Clause-Clear. See LICENSE file for details.

RING1_NR="$1"
BASE_PROC=0
M="./manage.py"

PROC=$($M dup_segments_new $BASE_PROC)
$M load_ring1 "$RING1_NR" "$PROC"
$M eval_claims "$PROC"

# trigger workers
$M eval_loc_1 "$PROC" 11
$M eval_loc_1 "$PROC" 23
$M eval_loc_1 "$PROC" 54
$M eval_loc_1 "$PROC" 42

# end of file
