# Generated by Django 4.2.7 on 2023-12-19 18:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Pieces2x2', '0005_twosideoptions_processor'),
    ]

    operations = [
        migrations.CreateModel(
            name='EvalProgress',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('eval_size', models.PositiveSmallIntegerField()),
                ('eval_loc', models.PositiveSmallIntegerField()),
                ('processor', models.PositiveIntegerField()),
                ('segment', models.PositiveSmallIntegerField()),
                ('todo_count', models.PositiveSmallIntegerField()),
                ('left_count', models.PositiveSmallIntegerField()),
                ('solve_order', models.CharField(max_length=128)),
                ('updated', models.DateTimeField()),
            ],
        ),
    ]
