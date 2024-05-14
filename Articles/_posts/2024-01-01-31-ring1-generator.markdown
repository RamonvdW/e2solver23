---
layout: article
order: 31
title: "Ring1 generator"
categories: background
---
The ring1 generator creates a closed ring of 2x2 pieces along the outer border.
It starts with a border consisting of base pieces, then finds compatible 2x2 pieces.
It also verifies that all inner corners can be solved: it requires a valid 2x2 pieces (with unused base pieces) plus two direct neighbours.

![Ring1]({{"/assets/ring1.png" | relative_url }}){: width="70%"}

<h2>Generating an outer border</h2>
Efficiently generating a border is a challenge by itself.
One optimization is using lists of pre-calculated corners with two border pieces on each side: border, border, corner, border, border.
The pre-calculated lists are checked for being able to make a valid solution with the hint piece. 
In the top-left corner, the 4 corner pieces can be coupled to four border pieces in 2600 ways.
The top-right corner can be made in 3400 ways.

A seed number provided by the operator allows to vary the starting position for the generator.
This allows generating controlled variations while being able to re-generation the same solution when needed.

The method used is to shuffle the pre-calculated lists by repeatedly removing one element and appending it to the end.
The number of shuffles depends on the length of the array: 10, 1000 or 10000.

The seed initializes a pseudo-random generator.
The numbers it generates are indexes into the array, for the shuffle.

Once the shuffle is done, the border generator searches for complete borders and outputs these.
It is possible to try the border generator with a management command:

{% highlight text %}
$ ./manage.py generate_border 221
solution: [49, 39, 54, 30, 16, 31, 32, 3, 6, 25, 19, 11, 7, 5, 57, 23, 51, 18, 43, 10, 22, 40, 2, 45, 14, 15, 59, 17, 33, 41, 48, 36, 29, 60, 13, 42, 21, 4, 44, 47, 12, 52, 58, 8, 24, 20, 26, 27, 28, 56, 38, 34, 1, 50, 35, 9, 37, 46, 53, 55]
solution: [39, 54, 49, 30, 16, 31, 32, 3, 6, 25, 19, 11, 7, 5, 57, 23, 51, 18, 43, 10, 22, 40, 2, 45, 14, 15, 59, 17, 33, 41, 48, 36, 29, 60, 13, 42, 21, 4, 44, 47, 12, 52, 58, 8, 24, 20, 26, 27, 28, 56, 38, 34, 1, 50, 35, 9, 37, 46, 53, 55]
solution: [55, 39, 54, 30, 16, 31, 32, 3, 6, 25, 19, 11, 7, 5, 57, 23, 51, 18, 43, 10, 22, 40, 2, 45, 14, 15, 59, 17, 33, 41, 48, 36, 29, 60, 13, 42, 21, 4, 44, 47, 12, 52, 58, 8, 24, 20, 26, 27, 28, 56, 38, 34, 1, 50, 35, 9, 37, 46, 53, 49]
solution: [39, 54, 55, 30, 16, 31, 32, 3, 6, 25, 19, 11, 7, 5, 57, 23, 51, 18, 43, 10, 22, 40, 2, 45, 14, 15, 59, 17, 33, 41, 48, 36, 29, 60, 13, 42, 21, 4, 44, 47, 12, 52, 58, 8, 24, 20, 26, 27, 28, 56, 38, 34, 1, 50, 35, 9, 37, 46, 53, 49]
$
{% endhighlight %}

{% highlight text %}
$ ./manage.py generate_border 222
solution: [43, 48, 34, 32, 29, 27, 44, 2, 5, 45, 10, 37, 36, 56, 39, 53, 23, 51, 30, 41, 14, 25, 4, 9, 22, 33, 28, 60, 35, 16, 40, 46, 12, 50, 49, 18, 31, 1, 15, 19, 59, 58, 13, 57, 8, 42, 54, 55, 38, 47, 21, 26, 3, 6, 52, 17, 20, 11, 7, 24]
solution: [43, 48, 34, 29, 32, 27, 44, 2, 5, 45, 10, 37, 36, 56, 39, 53, 23, 51, 30, 41, 14, 25, 4, 9, 22, 33, 28, 60, 35, 16, 40, 46, 12, 50, 49, 18, 31, 1, 15, 19, 59, 58, 13, 57, 8, 42, 54, 55, 38, 47, 21, 26, 3, 6, 52, 17, 20, 11, 7, 24]
solution: [43, 48, 34, 32, 29, 27, 44, 2, 5, 45, 10, 37, 36, 56, 39, 53, 23, 51, 30, 41, 14, 25, 4, 9, 22, 33, 28, 60, 35, 16, 40, 46, 12, 50, 49, 18, 31, 1, 15, 19, 59, 58, 13, 57, 8, 42, 54, 55, 38, 47, 21, 26, 3, 6, 52, 17, 11, 7, 24, 20]
solution: [43, 48, 34, 29, 32, 27, 44, 2, 5, 45, 10, 37, 36, 56, 39, 53, 23, 51, 30, 41, 14, 25, 4, 9, 22, 33, 28, 60, 35, 16, 40, 46, 12, 50, 49, 18, 31, 1, 15, 19, 59, 58, 13, 57, 8, 42, 54, 55, 38, 47, 21, 26, 3, 6, 52, 17, 11, 7, 24, 20]
$
{% endhighlight %}

The output shows the pieces outer border piece numbers. The last piece connects to the first.
