---
layout: article
order: 5
title: "Calculate to conclude"
categories: background
---
Many solvers are based on a backtracking algorithm.
When restarted, these typically repeat all the same steps.

I wanted to come up with an algorithm that performs a calculation on part of the puzzle, draws a conclusion and stores the result so it does not have to be performed again.

The image below shows the initial board with the counts of remaining two-side options around each location.
Around the hint piece locations we see a greatly reduced number of options remaining.

In this solver, a search ("calculation") can result in a conclusion to drop one of the options, reducing the remaining possibilities.
Once concluded, the search never considers that option again. It thus reduces the amount of calculation work remaining.

Instead of calculating and accumulating results it actually works the other way around: it starts with the maximum options and performs calculations to reduce the remaining possibilities.
The initial number of options worked out to be a very reasonable number: 23814.

The end-goal is 1 remaining option around each location.

![Initial board]({{"/assets/initial-board.png" | relative_url }}){:width="75%"}

The article about [two sides]({{"/background/2024/01/01/03-two-sides" | relative_url}}) explains the numbers shown (289, 85).

The colors indicate how many options are left, on a scale for red to green with blue used for "untouched".
