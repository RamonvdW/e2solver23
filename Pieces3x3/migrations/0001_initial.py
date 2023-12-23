# Generated by Django 4.2.7 on 2023-12-23 13:31

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ThreeSide',
            fields=[
                ('nr', models.PositiveIntegerField(primary_key=True, serialize=False)),
                ('three_sides', models.CharField(default='XXX', max_length=3)),
            ],
            options={
                'verbose_name': 'Three sides',
                'verbose_name_plural': 'Three sides',
            },
        ),
        migrations.CreateModel(
            name='Piece3x3',
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
                ('nr5', models.PositiveSmallIntegerField()),
                ('nr6', models.PositiveSmallIntegerField()),
                ('nr7', models.PositiveSmallIntegerField()),
                ('nr8', models.PositiveSmallIntegerField()),
                ('nr9', models.PositiveSmallIntegerField()),
                ('rot1', models.PositiveSmallIntegerField()),
                ('rot2', models.PositiveSmallIntegerField()),
                ('rot3', models.PositiveSmallIntegerField()),
                ('rot4', models.PositiveSmallIntegerField()),
                ('rot5', models.PositiveSmallIntegerField()),
                ('rot6', models.PositiveSmallIntegerField()),
                ('rot7', models.PositiveSmallIntegerField()),
                ('rot8', models.PositiveSmallIntegerField()),
                ('rot9', models.PositiveSmallIntegerField()),
            ],
            options={
                'verbose_name': 'Piece 3x3',
                'verbose_name_plural': 'Pieces 3x3',
                'indexes': [models.Index(fields=['is_border'], name='Pieces3x3_p_is_bord_802d89_idx'), models.Index(fields=['has_hint'], name='Pieces3x3_p_has_hin_314f36_idx'), models.Index(fields=['nr1'], name='Pieces3x3_p_nr1_5f1e95_idx'), models.Index(fields=['nr2'], name='Pieces3x3_p_nr2_e8134b_idx'), models.Index(fields=['nr3'], name='Pieces3x3_p_nr3_ed249e_idx'), models.Index(fields=['nr4'], name='Pieces3x3_p_nr4_e410e5_idx'), models.Index(fields=['nr5'], name='Pieces3x3_p_nr5_acc619_idx'), models.Index(fields=['nr6'], name='Pieces3x3_p_nr6_a6eb74_idx'), models.Index(fields=['nr7'], name='Pieces3x3_p_nr7_b0f32c_idx'), models.Index(fields=['nr8'], name='Pieces3x3_p_nr8_07fbbc_idx'), models.Index(fields=['nr9'], name='Pieces3x3_p_nr9_e23548_idx'), models.Index(fields=['side1'], name='Pieces3x3_p_side1_394a70_idx'), models.Index(fields=['side2'], name='Pieces3x3_p_side2_c74a8e_idx'), models.Index(fields=['side3'], name='Pieces3x3_p_side3_590984_idx'), models.Index(fields=['side4'], name='Pieces3x3_p_side4_e97a67_idx')],
            },
        ),
    ]
