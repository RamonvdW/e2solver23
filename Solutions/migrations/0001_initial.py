# Generated by Django 4.2.7 on 2023-11-17 16:51

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Solution',
            fields=[
                ('nr', models.PositiveIntegerField(primary_key=True, serialize=False)),
                ('when', models.DateTimeField(auto_now_add=True)),
                ('state', models.PositiveBigIntegerField()),
                ('gap_count', models.PositiveSmallIntegerField()),
                ('nr1', models.PositiveIntegerField()),
                ('nr2', models.PositiveIntegerField()),
                ('nr3', models.PositiveIntegerField()),
                ('nr4', models.PositiveIntegerField()),
                ('nr5', models.PositiveIntegerField()),
                ('nr6', models.PositiveIntegerField()),
                ('nr7', models.PositiveIntegerField()),
                ('nr8', models.PositiveIntegerField()),
                ('nr9', models.PositiveIntegerField()),
                ('nr10', models.PositiveIntegerField()),
                ('nr11', models.PositiveIntegerField()),
                ('nr12', models.PositiveIntegerField()),
                ('nr13', models.PositiveIntegerField()),
                ('nr14', models.PositiveIntegerField()),
                ('nr15', models.PositiveIntegerField()),
                ('nr16', models.PositiveIntegerField()),
                ('nr17', models.PositiveIntegerField()),
                ('nr18', models.PositiveIntegerField()),
                ('nr19', models.PositiveIntegerField()),
                ('nr20', models.PositiveIntegerField()),
                ('nr21', models.PositiveIntegerField()),
                ('nr22', models.PositiveIntegerField()),
                ('nr23', models.PositiveIntegerField()),
                ('nr24', models.PositiveIntegerField()),
                ('nr25', models.PositiveIntegerField()),
                ('nr26', models.PositiveIntegerField()),
                ('nr27', models.PositiveIntegerField()),
                ('nr28', models.PositiveIntegerField()),
                ('nr29', models.PositiveIntegerField()),
                ('nr30', models.PositiveIntegerField()),
                ('nr31', models.PositiveIntegerField()),
                ('nr32', models.PositiveIntegerField()),
                ('nr33', models.PositiveIntegerField()),
                ('nr34', models.PositiveIntegerField()),
                ('nr35', models.PositiveIntegerField()),
                ('nr36', models.PositiveIntegerField()),
                ('nr37', models.PositiveIntegerField()),
                ('nr38', models.PositiveIntegerField()),
                ('nr39', models.PositiveIntegerField()),
                ('nr40', models.PositiveIntegerField()),
                ('nr41', models.PositiveIntegerField()),
                ('nr42', models.PositiveIntegerField()),
                ('nr43', models.PositiveIntegerField()),
                ('nr44', models.PositiveIntegerField()),
                ('nr45', models.PositiveIntegerField()),
                ('nr46', models.PositiveIntegerField()),
                ('nr47', models.PositiveIntegerField()),
                ('nr48', models.PositiveIntegerField()),
                ('nr49', models.PositiveIntegerField()),
                ('nr50', models.PositiveIntegerField()),
                ('nr51', models.PositiveIntegerField()),
                ('nr52', models.PositiveIntegerField()),
                ('nr53', models.PositiveIntegerField()),
                ('nr54', models.PositiveIntegerField()),
                ('nr55', models.PositiveIntegerField()),
                ('nr56', models.PositiveIntegerField()),
                ('nr57', models.PositiveIntegerField()),
                ('nr58', models.PositiveIntegerField()),
                ('nr59', models.PositiveIntegerField()),
                ('nr60', models.PositiveIntegerField()),
                ('nr61', models.PositiveIntegerField()),
                ('nr62', models.PositiveIntegerField()),
                ('nr63', models.PositiveIntegerField()),
                ('nr64', models.PositiveIntegerField()),
            ],
            options={
                'verbose_name': 'Solution',
            },
        ),
        migrations.CreateModel(
            name='State',
            fields=[
                ('nr', models.PositiveBigIntegerField(primary_key=True, serialize=False)),
                ('evict', models.PositiveSmallIntegerField()),
            ],
            options={
                'verbose_name': 'State',
            },
        ),
    ]