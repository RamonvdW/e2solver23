# Generated by Django 4.2.7 on 2023-12-15 21:09

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='FourSides',
            fields=[
                ('nr', models.PositiveIntegerField(primary_key=True, serialize=False)),
                ('four_sides', models.CharField(default='XXXX', max_length=4)),
            ],
            options={
                'verbose_name': 'Four sides',
                'verbose_name_plural': 'Four sides',
            },
        ),
        migrations.CreateModel(
            name='Edge4x4',
            fields=[
                ('nr', models.PositiveIntegerField(primary_key=True, serialize=False)),
                ('side1', models.PositiveIntegerField()),
                ('side2', models.PositiveIntegerField()),
                ('side3', models.PositiveIntegerField()),
                ('side4', models.PositiveIntegerField()),
            ],
            options={
                'verbose_name': 'Edge 4x4',
                'verbose_name_plural': 'Edges 4x4',
                'indexes': [models.Index(fields=['side1'], name='Edges4x4_ed_side1_184c26_idx'), models.Index(fields=['side2'], name='Edges4x4_ed_side2_60b50c_idx'), models.Index(fields=['side3'], name='Edges4x4_ed_side3_df9c07_idx'), models.Index(fields=['side4'], name='Edges4x4_ed_side4_f08747_idx')],
            },
        ),
    ]
