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

With a little shell magic we create 123 duplicates of this board and fix location 34 on that board.
The workers immediately jump at it and 
