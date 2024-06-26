---
layout: article
order: 2
title: "Bigger pieces"
categories: background
---
Considering just the base pieces without a border, we see 17 different sides in use.
This allows for approximately 75000 unique pieces.
The puzzle only has 192 inner pieces.
192 out of 75000 means there is potentially a lot to gain to pre-calculate bigger pieces with *valid* inner side combinations.
A first estimate was 1 million 2x2 pieces.

![2x2 bad]({{"/assets/2x2_bad.png" | relative_url }}){:width="150px"}
![2x2 good]({{"/assets/2x2_good.png" | relative_url }}){:width="150px"}

The 2x2 pieces generator considers the following special cases:
- Hint pieces (5x) must be in a specific location in the 2x2 and never together in the same 2x2.
- Corner piece must be combined with 2 border pieces and one inner piece that is never a hint.
- Borders pieces always in pairs on at most one of the sides (never in the middle) combined with 2 inner pieces

Since the pieces do not have a predefined “up” direction, each piece can be placed under 4 possible rotations.
I considered the option to pre-generate all rotation variants of the 2x2 pieces, mainly to avoid rotating the corners, borders and hints into *invalid* positions on the board.
This approximately quadruples the number of 2x2 pieces generated, but trades work in the solvers versus handling some more rows in a database table.
I decided for it.

This resulted in a total of 3.95 million 2x2 pieces.

A 2x2 piece stores information about the 4 base pieces it is based on, including their respective rotations.
The fields are named nr1, nr2, nr3, nr4 and rot1, rot2, rot3, rot4.

To search for a piece that does not need one of the base pieces already in use on the board:
{% highlight text %}
qset = Piece2x2.objects.exclude(nr1__in=used_pieces)
                       .exclude(nr2__in=used_pieces)
                       .exclude(nr3__in=used_pieces)
                       .exclude(nr4__in=used_pieces)
{% endhighlight %}

I also tried creating 3x3 pieces, but the number of possible pieces is simply too much (trillions).
