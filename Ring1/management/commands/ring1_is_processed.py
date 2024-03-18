# -*- coding: utf-8 -*-

#  Copyright (c) 2024 Ramon van der Winkel.
#  All rights reserved.
#  Licensed under BSD-3-Clause-Clear. See LICENSE file for details.

from django.core.management.base import BaseCommand
from Ring1.models import Ring1


class Command(BaseCommand):

    help = "Find a Ring1 with is_processed flag set to False"

    def handle(self, *args, **options):
        ring = Ring1.objects.filter(is_processed=False).first()
        if ring:
            self.stdout.write("%s" % ring.nr)


# end of file
