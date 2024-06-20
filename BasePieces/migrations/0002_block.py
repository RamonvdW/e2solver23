# -*- coding: utf-8 -*-

#  Copyright (c) 2024 Ramon van der Winkel.
#  All rights reserved.
#  Licensed under BSD-3-Clause-Clear. See LICENSE file for details.

from django.db import migrations, models
from BasePieces.pieces_1x1 import PIECES


def make_blocks(apps, _):

    block_class = apps.get_model('BasePieces', 'Block')

    bulk = []
    for nr, sides in enumerate(PIECES, 1):
        b1 = sides[0]
        b2 = sides[1]
        b3 = sides[2]
        b4 = sides[3]
        bulk.append(
                block_class(nr=nr,
                            base_nr=nr,
                            b1=b1,
                            b2=b2,
                            b3=b3,
                            b4=b4,
                            side1=b1+b2,
                            side2=b2+b3,
                            side3=b3+b4,
                            side4=b4+b1))
    # for

    block_class.objects.bulk_create(bulk)


class Migration(migrations.Migration):

    dependencies = [
        ('BasePieces', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Block',
            fields=[
                ('nr', models.PositiveSmallIntegerField(primary_key=True, serialize=False)),
                ('base_nr', models.PositiveSmallIntegerField()),
                ('b1', models.CharField(default='X', max_length=1)),
                ('b2', models.CharField(default='X', max_length=1)),
                ('b3', models.CharField(default='X', max_length=1)),
                ('b4', models.CharField(default='X', max_length=1)),
                ('side1', models.CharField(default='XX', max_length=2)),
                ('side2', models.CharField(default='XX', max_length=2)),
                ('side3', models.CharField(default='XX', max_length=2)),
                ('side4', models.CharField(default='XX', max_length=2)),
            ],
            options={
                'indexes': [models.Index(fields=['b1'], name='BasePieces__b1_78b75f_idx'),
                            models.Index(fields=['b2'], name='BasePieces__b2_85551c_idx'),
                            models.Index(fields=['b3'], name='BasePieces__b3_981711_idx'),
                            models.Index(fields=['b4'], name='BasePieces__b4_a83144_idx'),
                            models.Index(fields=['side1'], name='BasePieces__side1_41e40f_idx'),
                            models.Index(fields=['side2'], name='BasePieces__side2_2752a7_idx'),
                            models.Index(fields=['side3'], name='BasePieces__side3_f9ccda_idx'),        # noqa
                            models.Index(fields=['side4'], name='BasePieces__side4_ccf482_idx'),
                            models.Index(fields=['base_nr'], name='BasePieces__base_nr_5c8898_idx')],
            },
        ),
        migrations.RunPython(make_blocks, reverse_code=migrations.RunPython.noop),
    ]

# end of file
