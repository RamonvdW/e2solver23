# Generated by Django 4.2.7 on 2024-02-01 07:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('WorkQueue', '0011_processorusedpieces_choices'),
    ]

    operations = [
        migrations.AddField(
            model_name='work',
            name='limit',
            field=models.PositiveSmallIntegerField(default=0),
        ),
    ]
