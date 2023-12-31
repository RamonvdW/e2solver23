# Generated by Django 4.2.7 on 2024-01-07 21:11

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Work',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('done', models.BooleanField(default=False)),
                ('doing', models.BooleanField(default=False)),
                ('job_type', models.CharField(default='', max_length=10)),
                ('priority', models.PositiveSmallIntegerField(default=0)),
                ('processor', models.PositiveIntegerField(default=0)),
                ('location', models.PositiveSmallIntegerField(default=0)),
                ('when_added', models.DateTimeField(auto_now_add=True)),
                ('when_done', models.DateTimeField(default='2000-01-01 00:00')),
            ],
            options={
                'verbose_name': 'Work',
            },
        ),
    ]
