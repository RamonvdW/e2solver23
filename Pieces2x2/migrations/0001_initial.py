# -*- coding: utf-8 -*-

#  Copyright (c) 2019-2023 Ramon van der Winkel.
#  All rights reserved.
#  Licensed under BSD-3-Clause-Clear. See LICENSE file for details.

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='TwoSides',
            fields=[
                ('nr', models.PositiveIntegerField(primary_key=True, serialize=False)),
                ('two_sides', models.CharField(default='XX', max_length=2)),
            ],
            options={'verbose_name': 'Two sides', 'verbose_name_plural': 'Two sides'},
        ),
        migrations.CreateModel(
            name='Piece2x2',
            fields=[
                ('nr', models.PositiveIntegerField(primary_key=True, serialize=False)),
                ('nr1', models.PositiveSmallIntegerField()),
                ('nr2', models.PositiveSmallIntegerField()),
                ('nr3', models.PositiveSmallIntegerField()),
                ('nr4', models.PositiveSmallIntegerField()),
                ('rot1', models.PositiveSmallIntegerField()),
                ('rot2', models.PositiveSmallIntegerField()),
                ('rot3', models.PositiveSmallIntegerField()),
                ('rot4', models.PositiveSmallIntegerField()),
                ('side1', models.PositiveIntegerField()),
                ('side2', models.PositiveIntegerField()),
                ('side3', models.PositiveIntegerField()),
                ('side4', models.PositiveIntegerField()),
            ],
            options={'verbose_name': 'Piece 2x2', 'verbose_name_plural': 'Pieces 2x2'},
        ),
        migrations.AddIndex(
            model_name='piece2x2',
            index=models.Index(fields=['nr1'], name='Pieces2x2_p_nr1_7f9b6f_idx'),
        ),
        migrations.AddIndex(
            model_name='piece2x2',
            index=models.Index(fields=['nr2'], name='Pieces2x2_p_nr2_44ea46_idx'),
        ),
        migrations.AddIndex(
            model_name='piece2x2',
            index=models.Index(fields=['nr3'], name='Pieces2x2_p_nr3_3f9d20_idx'),
        ),
        migrations.AddIndex(
            model_name='piece2x2',
            index=models.Index(fields=['nr4'], name='Pieces2x2_p_nr4_ac6d56_idx'),
        ),
        migrations.AddIndex(
            model_name='piece2x2',
            index=models.Index(fields=['side1'], name='Pieces2x2_p_side1_b2958d_idx'),
        ),
        migrations.AddIndex(
            model_name='piece2x2',
            index=models.Index(fields=['side2'], name='Pieces2x2_p_side2_d46a88_idx'),
        ),
        migrations.AddIndex(
            model_name='piece2x2',
            index=models.Index(fields=['side3'], name='Pieces2x2_p_side3_83760f_idx'),
        ),
        migrations.AddIndex(
            model_name='piece2x2',
            index=models.Index(fields=['side4'], name='Pieces2x2_p_side4_6c4d30_idx'),
        ),
        migrations.AddIndex(
            model_name='piece2x2',
            index=models.Index(fields=['side1', 'side2'], name='Pieces2x2_p_side1_909c9b_idx'),
        ),
        migrations.AddIndex(
            model_name='piece2x2',
            index=models.Index(fields=['side2', 'side3'], name='Pieces2x2_p_side2_06aea2_idx'),
        ),
        migrations.AddIndex(
            model_name='piece2x2',
            index=models.Index(fields=['side3', 'side4'], name='Pieces2x2_p_side3_24a655_idx'),
        ),
        migrations.AddIndex(
            model_name='piece2x2',
            index=models.Index(fields=['side4', 'side1'], name='Pieces2x2_p_side4_bd0ba3_idx'),
        ),
    ]

# end of file
