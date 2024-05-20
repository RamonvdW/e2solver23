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

<h2>Try location 15 option 2</h2>

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
- Selection 4: solves locations 55, 47, 39 but dead-ends in the bottom row (locations 50, 51, 52, 53)
- Selection 5: stable with 6754 options remaining. Location 23 has 3 pieces remaining.

Let's duplicate the last board and work with location 23.

- Selection 1: stable with 5742 options remaining.
- Selection 2: stable with 5903 options remaining.
- Selection 3: stable with 5671 options remaining.

All three boards have tension in the right column (locations 31, 39, 47, 55).
Location 31 only has 3 to 4 pieces remaining.
Locations 10, 50 and 55 only have 5 pieces remaining.

Let's duplicate the board with the most options and work with location 31.

- Selection 1: dead-end in location 11 after solving locations 31, 39, 47, 55, 14, 13, 12. 
- Selection 2: dead-end in location 12 after solving locations 31, 39, 47, 55, 54, 53, 52, 51. 
- Selection 3: dead-end in location 11 after solving locations 31, 39, 47, 55, 14, 13, 12.
- Selection 4: dead-end in location 50 after solving locations 31, 39, 47, 55, 54, 53, 52, 51. 

Let's duplicate the board with the fewest options and work with location 31.

- Selection 1: dead-end in location 46 after solving locations 31, 39, 47, 55, 54. 
- Selection 2: dead-end in location 44 after solving locations 31, 39, 47, 55, 54, 53, 52, 51, 50, 42. 
- Selection 3: dead-end in location 12 after solving locations 31, 54, 10, 18. 

And the last option:

- Selection 1: dead-end in location 14 after solving 31, 39, 47, 55, 54, 53, 52. 
- Selection 2: dead-end in location 47 after solving 31, 39, 55. 
- Selection 3: dead-end in location 14 after solving 31, 39, 47, 55.

Location 14 does not have claims, but is running out of 2x2 options probably because of the used base pieces.

{% highlight text %}
$ ./manage.sh eval_loc_1 252 14
[INFO] Location: 14; processor=252
[INFO] 148 base pieces in use or claimed
[INFO] Side options: 1, 1, 6, 10
[INFO] Number of Piece2x2: 0
{% endhighlight %}

Everything is dead end, so we need to take the next option for location 15.

<h2>Try location 15 option 3</h2>

Option 3 was a quick dead-end after immediately solving the right column and reducing the total option to below 4000, which is typically a bad sign.

Trying option 4 for location 15 instead.

<h2>Try location 15 option 4</h2>

After the initial propagation "scan1" was done to touch all locations and a "scan9" to evaluate 3x3 on 20 positions.
Since the board did not run into a dead-end, a "line2" evaluator was used on each side followed by a 4x4 evaluation in 4 position.

![Reduction animation]({{"/assets/anim1.gif" | relative_url }})

The intermediate result has 6220 options left, with 6, 3, 8 and 5 pieces possible in location 10, 23, 50 and 55.
Let's duplicate the board three times and fix location 23 to a different option on each board.

{% highlight text %}
$ dup 210 211
$ dup 210 212
$ dup 210 213
$ fix 211 23 0 --commit
$ fix 212 23 1 --commit
$ fix 213 23 2 --commit
{% endhighlight %}

![Reduced ring1]({{"/assets/reduce_ring1_3.png" | relative_url }}){: width="70%"}

Add scanning with 1x1 at prio 2 and 3x3 at prio 9 all over the board:

{% highlight text %}
$ ./manage.sh add_work 211 scan1 2 2
$ ./manage.sh add_work 212 scan1 2 2
$ ./manage.sh add_work 213 scan1 2 2
$ ./manage.sh add_work 211 scan9 9 9 --limit=289
$ ./manage.sh add_work 212 scan9 9 9 --limit=289
$ ./manage.sh add_work 213 scan9 9 9 --limit=289
{% endhighlight %}

(board 211, 212, 213 = 23/0, 23/1, 23/2)
