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
- Level 6: 1005 boards

An example of a level 6 board can be seen below. Will it survive much longer?

![Reduce ring3 claims]({{"/assets/close_to_solution_board.png" | relative_url }}){: width="70%"}

![Reduce ring3 claims]({{"/assets/close_to_solution_claims.png" | relative_url }}){: width="55%"}

It did not survive much longer. Walking all the remaining open spots with eval_loc_1 resulted in the following end-results.
As can be seen, the constraints in the outer ring are the challenge.
With the current technique we have to wait until the very end before we find it is a non-solution.

![Reduce ring3 claims]({{"/assets/close_to_solution_pieces.png" | relative_url }}){: width="80%"}

After adding the 7th (419 boards) and 8th fixed pieces, only 1 board survived. Everything else was eliminated and removed.

![Reduce ring3 claims]({{"/assets/close_to_solution_last.png" | relative_url }}){: width="70%"}

Below are the claims for base pieces on each location, limited to 5 claims.

{% highlight text %}
[INFO] Processor=16365
[INFO] 88 base pieces in use
[INFO] Loc 10 requires base 208 on nr1
[INFO] Loc 11 requires base 222 on nr4
[INFO] Loc 15 requires base 255 on nr2
[INFO] Loc 47 requires base 124 on nr1
[INFO] Loc 51 requires base 72 on nr1
[INFO] Loc 55 requires base 249 on nr4
[INFO] Remaining small claims:
1.nr1: [1, 2, 3]  *** MULTI (2) 1.nr1 + 57.nr3 ***
1.nr2: [15, 20, 24, 25]
2.nr1: [6, 11, 20, 31, 33]
2.nr2: [7, 25, 42, 43, 44]
2.nr3: [104, 120, 125, 247]
2.nr4: [131, 166, 237, 240]
3.nr1: [11, 20, 31, 45, 54]
3.nr3: [174, 177, 236]
3.nr4: [111, 131, 189, 194, 223]
4.nr1: [13, 46, 47, 54]
4.nr2: [30, 36, 45]
4.nr3: [126, 231, 237, 240]
4.nr4: [238, 243, 247]
5.nr1: [14, 28]
5.nr2: [9, 52]
5.nr3: [126, 250]
5.nr4: [142, 230]
6.nr1: [7, 55]
6.nr2: [35, 50, 58]
6.nr3: [122, 156]
6.nr4: [133, 234]
7.nr1: [29, 30, 44]
7.nr2: [32, 34, 60]
7.nr3: [108, 145, 175, 184]
7.nr4: [125, 197, 256]
8.nr2: [1, 2, 3, 4]  *** MULTI (2) 64.nr4 + 8.nr2 ***
9.nr1: [22, 28, 46, 53]
9.nr2: [103, 233, 236, 237]
9.nr3: [12, 13, 35, 40, 47]
9.nr4: [122, 169, 242]
10.nr2: [112, 145]
10.nr3: [194, 231, 232]
10.nr4: [132, 204]
11.nr1: [158, 239]
11.nr2: [163, 202, 246]
11.nr3: [205, 206]
12.nr1: [158, 225]
12.nr2: [168, 226]
12.nr3: [218, 232]
12.nr4: [83, 92]
13.nr1: [182, 244]
13.nr2: [166, 180]
13.nr3: [226, 236]
13.nr4: [80, 90]
14.nr1: [104, 111]
14.nr2: [111, 240]
14.nr3: [102, 195]
14.nr4: [131, 192]
15.nr1: [122, 218]
15.nr3: [104, 248]
15.nr4: [133, 223]
17.nr1: [25, 45, 55, 59]
17.nr2: [97, 99]
17.nr3: [14, 15, 50]
17.nr4: [133, 195]
23.nr1: [215, 223]
23.nr2: [134, 220, 225]
23.nr3: [214, 227]
23.nr4: [136, 182, 210, 229]
25.nr1: [6, 44]
25.nr2: [130, 174]
25.nr3: [24, 33]
25.nr4: [170, 244]
31.nr1: [132, 216]
31.nr3: [118, 128, 247]
33.nr1: [10, 22]
33.nr2: [243, 248]
33.nr3: [13, 38]
33.nr4: [215, 251]
39.nr1: [123, 184, 192]
39.nr3: [174, 243]
47.nr3: [112, 113, 217]
49.nr1: [54, 55]
49.nr2: [166, 170]
49.nr3: [38, 47, 56, 59]
49.nr4: [182, 186, 210]
51.nr2: [150, 163]
51.nr3: [123, 192, 199]
52.nr1: [118, 215]
52.nr2: [237, 240, 247]
53.nr1: [92, 97]
53.nr2: [133, 195, 201]
54.nr1: [119, 227]
54.nr2: [105, 163]
54.nr3: [115, 170, 180, 246]
54.nr4: [105, 108, 111, 126, 225]
55.nr1: [120, 134, 247]
55.nr3: [125, 132, 223, 231, 232]
57.nr3: [1, 2, 3]  *** MULTI (2) 1.nr1 + 57.nr3 ***
58.nr2: [92, 120, 125, 126, 231]
64.nr4: [1, 2, 3, 4]  *** MULTI (2) 64.nr4 + 8.nr2 ***
{% endhighlight %}

In the end, it also reached a dead end. No solution possible for this Ring3.

![Reduce ring3 claims]({{"/assets/close_to_solution_last_failed.png" | relative_url }}){: width="60%"}
