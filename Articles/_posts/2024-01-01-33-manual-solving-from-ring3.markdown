---
layout: article
order: 33
title: "Manually solving from ring3"
categories: background
---
The image below shows one of the generated ring3 loaded onto a board.

![Reduce ring3]({{"/assets/reduce_ring3_1.png" | relative_url }}){: width="70%"}

There is only 1 piece possible 2x2 piece for location 36.
When evaluated, the other 3 central pieces fall into place automatically.

![Reduce ring3]({{"/assets/reduce_ring3_2.png" | relative_url }}){: width="70%"}

We run the usual scans with 1x1 and 3x3 evaluators and up with 6781 options left.
To continue we have to fix one of the locations around this core.

The hint locations:
- Location 10: 254 pieces
- Location 15: 842 pieces
- Location 50: **167 pieces**
- Location 55: 399 pieces 

Other sides:
- Location 11: 629 pieces
- Location 12: 184 pieces
- Location 13: 196 pieces
- Location 14: 629 pieces

- Location 23: 1205 pieces
- Location 31: 1071 pieces
- Location 39: 1023 pieces
- Location 47: 851 pieces

- Location 18: 339 pieces
- Location 26: 184 pieces
- Location 34: **123 pieces**
- Location 42: 233 pieces
 
- Location 51: 289 pieces
- Location 52: 595 pieces
- Location 53: 725 pieces
- Location 54: 441 pieces

We observe that the tension is in the bottom left corner (location 50) and the fewest options are in location 34.

With a little shell magic we create 123 duplicates of this board and fix location 34 on each board to a different option.
We then add a 1x1 scan, 3x3 scan and 4x4 evaluation in strategic locations: the corners and centered against each border.

The workers immediately jump at it and start removing options.
While this is ongoing, claims start to develop as shown in blue below (location 26 was also filled in this example).

![Reduce ring3 claims]({{"/assets/reduce_ring3_3_claims.png" | relative_url }}){: width="55%"}

The claims further reduce the options in other locations.
On boards with fewer total options left we see more claims showing up.
The example below has 2215 total options remaining.

![Reduce ring3 claims]({{"/assets/reduce_ring3_4_claims.png" | relative_url }}){: width="55%"}

After a few days, 93 of the 123 board instances survived with between 1779 and 4711 options remaining.
The differences are caused by the number of additional locations that were fixed.

Many days later we reached the sixth level of fixing locations, with this many boards remaining:
- Level 1: 1 board
- Level 2: 43 boards (down from 74)
- Level 3: 92 boards (down from 208)
- Level 4: 181 boards (down from 495)
- Level 5: 283 boards (down from 1677)
- Level 6: 

An example of a level 6 board can be seen below. Will it survive much longer?

![Reduce ring3 claims]({{"/assets/close_to_solution_board.png" | relative_url }}){: width="70%"}

![Reduce ring3 claims]({{"/assets/close_to_solution_claims.png" | relative_url }}){: width="55%"}

It did not survive much longer. Walking all the remaining open spots with eval_loc_1 resulted in the following end-results.
As can be seen, the constraints in the outer ring are the challenge.
With the current technique we have to wait until the very end before we find it is a non-solution.

![Reduce ring3 claims]({{"/assets/close_to_solution_pieces.png" | relative_url }}){: width="80%"}
