---
layout: article
order: 99
title: "Server setup"
categories: background
---
The code available in the [GitHub repository](https://github.com/RamonvdW/e2solver23) has some prerequisites.
This article provides some background on what is needed.

These are the big lines of my recipe:
- Install headless Linux (my choice is Debian)
- Secure your installation and verify it is secure
- Create a domain address that points to your server IP
- Install PostgreSQL
- Tweak PostgreSQL for on-host efficiency: no ssl, huge cache size, large shared buffers, large work mem
- Create database user + create empty database
- Install Apache2
- Configure Apache2: enable ssl, http2 and disable unnecessary things
- Install CertBot and get a certificate for https
- Install Django
- Install git
- Create Python virtual env for website, update pip, install pip-tools
- Fetch the repo + deploy code
- Install the 3rd-party packages with pip-sync 
- Install, enable and start the systemd workers
