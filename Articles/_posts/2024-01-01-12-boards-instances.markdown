---
layout: article
order: 12
title: "Board instances"
categories: background
---
The solver supports "board instances" that can be duplicated and deleted on command.
Each board instance has its own set of remaining two side options.
A board can also have a specified 2x2 piece on each of the 64 locations.

A board instance is referenced by its number.
Evaluators always work on a specified board.

An operator or script can request a board instance to be duplicated, as shown below.

Duplicate board 0 to board 1:
{% highlight text %}
$ ./manage.sh dup_segments 0 1
[INFO] Duplicating processor 0 to 1
[INFO] Creating 23637 records
$
{% endhighlight %}

Duplicate board 0 to the next free number (this is intended for scripts):
{% highlight text %}
$ ./manage.sh dup_segments_new 0
2
$
{% endhighlight %}

Drop board 1:
{% highlight text %}
$ ./manage.sh drop_segments 1
[INFO] Deleting 23637 TwoSide records
[INFO] Deleted 0 jobs for processor 1 from work queue
{% endhighlight %}

<h2>Dead end</h2>
An evaluator can mark a board as a "dead end", for example when zero options remain for one of the segments.
Boards that are a dead end can be cleaned up with the drop segments command.

Example of a dead-end:

![Progress]({{"/assets/dead-end_1.png" | relative_url }}){: width="60%"}

The progress shows that the single-location evaluator concluded no 2x2 pieces is available for location 13,
given the remaining two-side options around location 13 and the base pieces already taken by the filled locations.  

![Progress]({{"/assets/dead-end_3.png" | relative_url }}){: width="60%"}
