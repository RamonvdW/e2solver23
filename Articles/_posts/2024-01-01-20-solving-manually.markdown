---
layout: article
order: 20
title:  "Solving manually"
categories: background
---
After creating all 2x2 pieces and initializing the board, the operator can input manual commands to solve a puzzle:
- Duplicate a board
- Drop a board that is no longer needed
- Fix a location: select one of the remaining 2x2 pieces that can fit a specific location
- Fix a segment: select one of the remaining options for a specific segment
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

![Progress]({{"/assets/fix_loc_36.png" | relative_url }}){: width="60%"}

Evaluate location 28 (just above)
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
