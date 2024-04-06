# -*- coding: utf-8 -*-

#  Copyright (c) 2024 Ramon van der Winkel.
#  All rights reserved.
#  Licensed under BSD-3-Clause-Clear. See LICENSE file for details.

from django.db import migrations
from django.db.models import F


def renumber(apps, _):
    """ Segment numbering has changed: 129..193 is now 101..165
    """

    options_klas = apps.get_model('Pieces2x2', 'TwoSideOptions')
    progres_klas = apps.get_model('Pieces2x2', 'EvalProgress')

    options_klas.objects.filter(segment__gte=129).update(segment=F('segment') - 28)
    progres_klas.objects.filter(segment__gte=129).update(segment=F('segment') - 28)


class Migration(migrations.Migration):

    dependencies = [
        ('Pieces2x2', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(renumber)
    ]

# end of file
