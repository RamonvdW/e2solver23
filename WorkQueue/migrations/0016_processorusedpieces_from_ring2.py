# Generated by Django 4.2.10 on 2024-03-18 19:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('WorkQueue', '0015_processorusedpieces_from_ring1'),
    ]

    operations = [
        migrations.AddField(
            model_name='processorusedpieces',
            name='from_ring2',
            field=models.PositiveIntegerField(default=0),
        ),
    ]
