---
layout: article
order: 5
title:  "Calculate to conclude"
categories: background
---
Many solvers are based on a backtracking algorithm.
When restarted, these typically repeat all the same calculations.

I wanted to come up with an algorithm that calculates, draws a conclusion and stores the result so it does not have to be calculated again.

The image below shows the initial board with the remaining counts of two-side options around each location.
Around the hint piece locations we see a greatly reduced number of options remaining.

In my solver, a calculation can conclude to drop one of the options, reducing the remaining possibilities.
Once concluded, the calculation does not have to be repeated anymore and the result can be used in other calculations.

The end-goal is 1 remaining option around each location.

![Initial board]({{"/assets/initial-board.png" | relative_url }}){:width="75%"}

The article about [two sides](/background/2024/01/01/03-sides) explains the numbers (289, 85).
