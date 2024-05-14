---
layout: article
order: 20
title: "Solving manually"
categories: background
---
After creating all 2x2 pieces and initializing the board, the operator can input manual commands to solve a puzzle:
- Duplicate a board
- Drop a board that is no longer needed
- Fix a location: select and place one of the remaining 2x2 pieces that fit the selected location
- Fix a segment: select one of the remaining options for a specific segment (remove all other options)
- Run one of the evaluators on a selected board and selected top-left location

Find out that location 36 on board 1 has 4633 possible 2x2 pieces:
{% highlight text %}
$ ./manage.sh fix_loc 1 36 0
[INFO] Processor=1; Location: 36
[INFO] 0 base pieces in use or claimed
[INFO] Selecting 0 / 4633
[INFO] Performing eval_loc_1 equivalent check for loc 36
[INFO] Selected p2x2 with base nrs: [67, 139, 63, 167]
[INFO] Side 1 is segment 36
[INFO] Side 2 is segment 137
[INFO] Side 3 is segment 44
[INFO] Side 4 is segment 136
[INFO] Reductions: 16, 16, 279, 283
[WARNING] Use --commit to keep
$
{% endhighlight %}

Fix location 36 on board 1 with first option:
{% highlight text %}
$ ./manage.sh fix_loc 1 36 0 --commit --nop
[INFO] Processor=1; Location: 36
[INFO] 0 base pieces in use or claimed
[INFO] Selecting 0 / 4633
[INFO] Performing eval_loc_1 equivalent check for loc 36
[INFO] Selected p2x2 with base nrs: [67, 139, 63, 167]
[INFO] Side 1 is segment 36
[INFO] Side 2 is segment 137
[INFO] Side 3 is segment 44
[INFO] Side 4 is segment 136
[INFO] Reductions: 16, 16, 279, 283
$
{% endhighlight %}

The result:

![Progress]({{"/assets/fix_loc_36.png" | relative_url }}){: width="60%"}

The colors indicate how many options are left, on a scale for red to green with blue used for "untouched".
White is used to indicate a delta compared the board it was duplicated from.

Evaluate location 28, which resulted in removal of 37 and 90 of the remaining options on sides 2 and 4 respectively.
{% highlight text %}
$ ./manage.sh eval_loc_1 1 28 --nop
[INFO] Location: 28; processor=1
[INFO] 8 base pieces in use or claimed
[INFO] Side options: 289, 289, 1, 289
[INFO] Number of Piece2x2: 11382
[INFO] Reductions: 0, 37, 0, 90
$
{% endhighlight %}

![Progress]({{"/assets/eval_loc_1_28.png" | relative_url }}){: width="60%"}

<h2>Solving for a single location</h2>
At some point during all the evaluations and removal of possibilities, it can happen that only a single 2x2 piece remains for a location.

The evaluator for a single location (eval_loc_1) has the power to decide to select that one remaining 2x2 piece for that location on board, marking the location as "filled".

{% highlight text %}
$ ./manage.sh eval_loc_1 11 31
[INFO] Location: 31; processor=11
[INFO] 152 base pieces in use or claimed
[INFO] Side options: 1, 1, 2, 1
[INFO] Number of Piece2x2: 1
[INFO] Single solution left for loc 31
$
{% endhighlight %}
