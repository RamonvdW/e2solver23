---
layout: article
order: 1
title:  "Technology choices"
categories: background
---
This is a follow-up on the work done about 16 years ago (2007-2008), utilizing skills and tools available in 2023.

I selected the following technology:
- Powerful Linux host in the cloud (dedicated 12-cores, 64GB RAM, 1TB NVMe)
- Python3
- PostgreSQL database
- Systemd background workers
- Django website: for visualizations and to monitor progress from any mobile / table / laptop
- Django management commands to perform work (or queue work)
- Source code in GitHub
- Focus on efficient algorithms instead of efficient code

The database serves two purposes: it hold the work queue, progress, board, remaining possibilities.
And it is also good in one important task: to efficiently search and serve programs running in parallel.
For example: answer “which puzzle pieces fit here?”

The visualizations help me identify problems in the code early.

If you are interested in the code, check out the [GitHub repository](https://github.com/RamonvdW/e2solver23).

![Technology choices](/assets/wordcloud.png){:width="250px"}
