---
layout: article
order: 30
title: "Solving strategies"
categories: background
---

These are my learnings from trying to solve Eternity II.
Needless the say, none of these strategies resulted in a solution so far.

<h2>Short-distance effects</h2>
Due to the design of the base pieces, placing one 2x2 piece has almost no effect on the neighboring locations.
The immediate neighbour locations could loose a few two-side options, but beyond that there is typically no effect at all.
The bigger evaluators (3x3 and 4x4) are needed to find an effect.

Once the puzzle has more locations filled, the problems typically occur at a random location further away from the last placed piece, due to the used base pieces.

<h2>Location tension</h2>
Once the neighbors of a location get filled, the location comes "under tension".
With this I mean the chance of finding a solution is decreasing.

One neighbor is not too bad, two sides is tension, three or four sides means a very small chance of a solution.

<h2>Constraints</h2>
I noticed the puzzle contains "constraints" in the form of rings.

If we attempt to create a complete outer ring, then it is easy until the very end: the last piece cannot be placed.
This is the constraint that cannot be fulfilled.

In addition, when the ring is complete there could be tension on the inner corners and we typically find there is no solution left.

Specialized [ring generators]({{"/background/2024/01/01/31-ring-generators" | relative_url }}) were added to create a ring, as a good foundation for solving the remainder.

<h2>Solving outside-in</h2>
Starting with a solid ring1, it is an option to solve from the outside towards the center.
This means the tension of the border is solved.
Unfortunately, a lot of borders can be made with varying utilization of inner base pieces.

![Ring1]({{"/assets/ring1.png" | relative_url }}){: width="70%"}

<h2>Solving from in between</h2>
Starting with a solid ring2, four of the hints are already placed properly.
The challenge is to find an outer border.

![Ring2]({{"/assets/ring2.png" | relative_url }}){: width="70%"}

<h2>Solving inside-out</h2>
Starting with a solid ring3, it is an option to solve from the inside towards the border.
The advantage is that the center hint is secured.

![Ring3]({{"/assets/ring3.png" | relative_url }}){: width="70%"}

The rings all come with the problem of location tension described above: the inside corners have two sides that need to match
and at least once the three-side tension happens when closing the next ring.

<h2>Lines</h2>
Using horizontal or vertical lines it is possible to limit the location tension to two sides.
But the constraints of the rings are solved very late.

Very likely this is how the puzzle was created - see the page on [Wang Tiles]({{"/background/2024/01/01/98-wang-tiles" | relative_url}}).
