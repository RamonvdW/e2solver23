# Generated by Django 4.2.7 on 2024-02-13 17:13

from django.db import migrations, models
from django.utils import timezone


class Migration(migrations.Migration):

    dependencies = [
        ('WorkQueue', '0013_work_seed'),
    ]

    operations = [
        migrations.AddField(
            model_name='work',
            name='start_after',
            field=models.DateTimeField(auto_now_add=True, default=timezone.now),
            preserve_default=False,
        ),
    ]
