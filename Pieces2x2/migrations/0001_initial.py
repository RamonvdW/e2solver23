# -*- coding: utf-8 -*-

#  Copyright (c) 2023-2024 Ramon van der Winkel.
#  All rights reserved.
#  Licensed under BSD-3-Clause-Clear. See LICENSE file for details.

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='EvalProgress',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('eval_size', models.PositiveSmallIntegerField()),
                ('eval_loc', models.PositiveSmallIntegerField()),
                ('processor', models.PositiveIntegerField()),
                ('segment', models.PositiveSmallIntegerField()),
                ('todo_count', models.PositiveSmallIntegerField()),
                ('left_count', models.PositiveSmallIntegerField()),
                ('solve_order', models.CharField(max_length=250)),
                ('updated', models.DateTimeField()),
            ],
        ),
        migrations.CreateModel(
            name='TwoSide',
            fields=[
                ('nr', models.PositiveIntegerField(primary_key=True, serialize=False)),
                ('two_sides', models.CharField(default='XX', max_length=2)),
            ],
            options={
                'verbose_name': 'Two sides',
                'verbose_name_plural': 'Two sides',
            },
        ),
        migrations.CreateModel(
            name='TwoSideOptions',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('processor', models.PositiveIntegerField(default=0)),
                ('segment', models.PositiveSmallIntegerField()),
                ('two_side', models.PositiveSmallIntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='Piece2x2',
            fields=[
                ('nr', models.PositiveIntegerField(primary_key=True, serialize=False)),
                ('is_border', models.BooleanField()),
                ('has_hint', models.BooleanField()),
                ('side1', models.PositiveIntegerField()),
                ('side2', models.PositiveIntegerField()),
                ('side3', models.PositiveIntegerField()),
                ('side4', models.PositiveIntegerField()),
                ('nr1', models.PositiveSmallIntegerField()),
                ('nr2', models.PositiveSmallIntegerField()),
                ('nr3', models.PositiveSmallIntegerField()),
                ('nr4', models.PositiveSmallIntegerField()),
                ('rot1', models.PositiveSmallIntegerField()),
                ('rot2', models.PositiveSmallIntegerField()),
                ('rot3', models.PositiveSmallIntegerField()),
                ('rot4', models.PositiveSmallIntegerField()),
            ],
            options={
                'verbose_name': 'Piece 2x2',
                'verbose_name_plural': 'Pieces 2x2',
                'indexes': [models.Index(fields=['is_border'], name='Pieces2x2_p_is_bord_14ca88_idx'),
                            models.Index(fields=['has_hint'], name='Pieces2x2_p_has_hin_f9193d_idx'),
                            models.Index(fields=['nr1'], name='Pieces2x2_p_nr1_7f9b6f_idx'),
                            models.Index(fields=['nr2'], name='Pieces2x2_p_nr2_44ea46_idx'),
                            models.Index(fields=['nr3'], name='Pieces2x2_p_nr3_3f9d20_idx'),
                            models.Index(fields=['nr4'], name='Pieces2x2_p_nr4_ac6d56_idx'),
                            models.Index(fields=['side1'], name='Pieces2x2_p_side1_b2958d_idx'),
                            models.Index(fields=['side2'], name='Pieces2x2_p_side2_d46a88_idx'),
                            models.Index(fields=['side3'], name='Pieces2x2_p_side3_83760f_idx'),
                            models.Index(fields=['side4'], name='Pieces2x2_p_side4_6c4d30_idx')],
            },
        ),
    ]
