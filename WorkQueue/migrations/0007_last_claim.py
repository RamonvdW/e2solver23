# Generated by Django 4.2.7 on 2024-01-25 05:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('WorkQueue', '0006_claimed'),
    ]

    operations = [
        migrations.AddField(
            model_name='processorusedpieces',
            name='claimed_at_twoside_count',
            field=models.PositiveIntegerField(default=99999),
        ),
    ]
