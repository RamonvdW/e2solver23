# Generated by Django 4.2.7 on 2023-11-11 15:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Corners4', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='corner4',
            name='side2',
            field=models.CharField(default='', max_length=4),
        ),
        migrations.AddField(
            model_name='corner4',
            name='side3',
            field=models.CharField(default='', max_length=4),
        ),
    ]