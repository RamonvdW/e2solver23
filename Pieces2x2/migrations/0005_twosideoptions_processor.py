# Generated by Django 4.2.7 on 2023-12-17 08:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Pieces2x2', '0004_segment_options'),
    ]

    operations = [
        migrations.AddField(
            model_name='twosideoptions',
            name='processor',
            field=models.PositiveIntegerField(default=0),
        ),
    ]
