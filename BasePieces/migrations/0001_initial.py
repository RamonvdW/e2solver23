# -*- coding: utf-8 -*-

#  Copyright (c) 2019-2024 Ramon van der Winkel.
#  All rights reserved.
#  Licensed under BSD-3-Clause-Clear. See LICENSE file for details.

from django.db import migrations, models
from BasePieces.pieces_1x1 import PIECES


def make_base_pieces(apps, _):

    basepiece_class = apps.get_model('BasePieces', 'BasePiece')

    bulk = []
    for nr, sides in enumerate(PIECES, 1):
        bulk.append(
                basepiece_class(nr=nr,
                                side1=sides[0],
                                side2=sides[1],
                                side3=sides[2],
                                side4=sides[3]))
    # for

    basepiece_class.objects.bulk_create(bulk)


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='BasePiece',
            fields=[
                ('nr', models.PositiveSmallIntegerField(primary_key=True, serialize=False)),
                ('side1', models.CharField(default='X', max_length=1)),
                ('side2', models.CharField(default='X', max_length=1)),
                ('side3', models.CharField(default='X', max_length=1)),
                ('side4', models.CharField(default='X', max_length=1)),
            ],
        ),
        migrations.AddIndex(
            model_name='basepiece',
            index=models.Index(fields=['side1'], name='BasePieces__side1_889cb6_idx'),
        ),
        migrations.AddIndex(
            model_name='basepiece',
            index=models.Index(fields=['side2'], name='BasePieces__side2_9c3149_idx'),
        ),
        migrations.AddIndex(
            model_name='basepiece',
            index=models.Index(fields=['side3'], name='BasePieces__side3_3176de_idx'),
        ),
        migrations.AddIndex(
            model_name='basepiece',
            index=models.Index(fields=['side4'], name='BasePieces__side4_e903bf_idx'),
        ),
        migrations.AddIndex(
            model_name='basepiece',
            index=models.Index(fields=['side1', 'side2'], name='BasePieces__side1_4dd0b2_idx'),
        ),
        migrations.AddIndex(
            model_name='basepiece',
            index=models.Index(fields=['side2', 'side3'], name='BasePieces__side2_5c9ddf_idx'),
        ),
        migrations.AddIndex(
            model_name='basepiece',
            index=models.Index(fields=['side3', 'side4'], name='BasePieces__side3_a43219_idx'),
        ),
        migrations.AddIndex(
            model_name='basepiece',
            index=models.Index(fields=['side4', 'side1'], name='BasePieces__side4_2605ff_idx'),
        ),
        migrations.RunPython(make_base_pieces, reverse_code=migrations.RunPython.noop)
    ]

# end of file
