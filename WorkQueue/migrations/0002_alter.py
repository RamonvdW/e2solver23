# Generated by Django 4.2.7 on 2024-01-07 21:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('WorkQueue', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='work',
            options={'verbose_name': 'Work', 'verbose_name_plural': 'Work'},
        ),
        migrations.AlterField(
            model_name='work',
            name='when_done',
            field=models.DateTimeField(default='2000-01-01 00:00 +0000'),
        ),
    ]
