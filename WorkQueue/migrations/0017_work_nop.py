# Generated by Django 4.2.11 on 2024-04-11 19:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('WorkQueue', '0016_processorusedpieces_from_ring2'),
    ]

    operations = [
        migrations.AddField(
            model_name='work',
            name='nop',
            field=models.BooleanField(default=False),
        ),
    ]