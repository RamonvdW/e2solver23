---
layout: article
order: 1
title: "Technology choices"
categories: background
---
This is a follow-up on the work done about 16 years ago (2007-2008), utilizing skills and tools available in 2023.

I selected the following technology:
- Powerful Linux host in the cloud (dedicated 12-cores, 64GB RAM, 1TB NVMe)
- Python3
- PostgreSQL database
- Django website: for visualizations and to monitor progress from any mobile / table / laptop
- Django management commands to perform work (or queue up for the workers)
- Systemd-managed workers
- Source code in GitHub
- Focus on efficient algorithms instead of efficient code

The database serves two purposes: it holds the work queue, progress, boards, remaining options per board.
And it is also good in one important task: to efficiently search and handle parallel queries.
For example: answer “which puzzle pieces fit on this location given these used pieces?”

The visualizations helped me identify problems in the code early.

If you are interested in the code, check out the [GitHub repository](https://github.com/RamonvdW/e2solver23).

![Technology choices]({{"/assets/wordcloud.png" | relative_url }}){:width="250px"}
