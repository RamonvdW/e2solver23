---
layout: article
order: 32
title: "Manually solving from ring1"
categories: background
---
The image below shows a ring1 loaded into a board.
Several 3x3 evaluators (eval_loc_9) are at work to reduce the remaining options.

![Reduce ring1]({{"/assets/reduce_ring1_1.png" | relative_url }}){: width="70%"}

Approximately 20 minutes later it looks like this:

![Reduce ring1]({{"/assets/reduce_ring1_2.png" | relative_url }}){: width="70%"}

How would you continue?
- Fix the center hint? Location 36 has 1857 pieces to chose from
- Fix the other four hints? Locations 10, 15, 50, 55 respectively have 7, 5, 11 and 8 pieces to chose from
- Fix some of the segments? Will you chose a high or low number?
- The right side seems to have fewer options.
- Looking at the claims: location 10 has 2 claims

Let's try location 15

{% highlight text %}
$ dup 200 201
[INFO] Duplicating processor 200 to 201
[INFO] Creating 8620 records
$ fix 201 15 2 --commit
[INFO] Processor=201; Location: 15
[INFO] 117 base pieces in use or claimed
[INFO] Selecting 2 / 5
[INFO] Performing eval_loc_1 equivalent check for loc 15
[INFO] Selected p2x2 with base nrs: [109, 255, 83, 215]
[INFO] Side 1 is segment 15
[INFO] Side 2 is segment 116
[INFO] Side 3 is segment 23
[INFO] Side 4 is segment 115
[INFO] Reductions: 0, 0, 4, 4
$ 
{% endhighlight %}
(the commands used are shell aliases for the commands shown earlier)

- Selection 1: dead-end in location 47.
- Selection 2: dead-end in location 47.
- Selection 3: stable with 6373 options remaining. Tension in locations 50 (2 pieces remaining) and 47 (3 pieces remaining).
- Selection 4: "solves" locations 55, 47, 39 but dead-ends in the bottom row (locations 50, 51, 52, 53)
- Selection 5: stable with 6757 options remaining. Location 23 has 3 pieces remaining.

Let's duplicate the last board and work with location 23.

- (board 210)Selection 1: stable with xxx options remaining. Tension in the right column (locations 31, 39, 47, 55).
- (board 211)Selection 2: stable with xxx options remaining.
- (board 212)Selection 3: stable with xxx options remaining. Location 31 has 3 pieces remaining.
