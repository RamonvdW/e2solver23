# Generated by Django 4.2.7 on 2023-11-24 20:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Pieces2x2', '0002_block2x8'),
    ]

    operations = [
        migrations.AddField(
            model_name='block2x8',
            name='processor',
            field=models.PositiveIntegerField(default=0),
            preserve_default=False,
        ),
    ]