---
layout: article
order: 22
title: "Propagation"
categories: background
---
When an evaluator removes a segment option, it can affect the possible options for the locations around it.

Therefore, the work is queued up to evaluate the locations around an affected segment:
- Evaluate the single locations left + right or above + below the segment
- Evaluate three 2x2 blocks around/touching the affected segment 

These new evaluations can again result in knock-on effects.

When a location is filled, either manually or simply because it is the last 2x2 possible in that location,
then the same thing happens: segments around the location are set to 1 option and evaluations of all neighbors is requested.

Because the number of 2x2 pieces that fit in the neighboring location is now limited by the fixed segment,
fewer options remain for the other segments of that location. And this can again trigger options removal on other segments.

An example of this is shown in [solving manually]({{"/background/2024/01/01/20-solving-manually" | relative_url }}) 

A typical situation in the work queue: the 3x3 evaluator (eval_loc_9) removes options and propagates to eval_loc_1 and eval_loc_4.

![Work queue]({{"/assets/queued_work.png" | relative_url }}){: width="45%"}
