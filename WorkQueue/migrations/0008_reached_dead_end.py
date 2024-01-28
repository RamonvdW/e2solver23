# Generated by Django 4.2.7 on 2024-01-28 18:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('WorkQueue', '0007_last_claim'),
    ]

    operations = [
        migrations.AddField(
            model_name='processorusedpieces',
            name='reached_dead_end',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='processorusedpieces',
            name='claimed_nrs_double',
            field=models.CharField(blank=True, default='', max_length=512),
        ),
        migrations.AlterField(
            model_name='processorusedpieces',
            name='claimed_nrs_single',
            field=models.CharField(blank=True, default='', max_length=512),
        ),
    ]
