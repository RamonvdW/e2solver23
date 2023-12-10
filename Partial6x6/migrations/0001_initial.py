# Generated by Django 4.2.7 on 2023-12-09 18:26

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='Partial6x6',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('when', models.DateTimeField(auto_now_add=True)),
                ('processor', models.PositiveIntegerField(default=0)),
                ('is_processed', models.BooleanField(default=False)),
                ('based_on_4x4', models.PositiveBigIntegerField()),
                ('note1', models.CharField(blank=True, default='', max_length=30)),
                ('note2', models.CharField(blank=True, default='', max_length=30)),
                ('note3', models.CharField(blank=True, default='', max_length=30)),
                ('note4', models.CharField(blank=True, default='', max_length=30)),
                ('note5', models.CharField(blank=True, default='', max_length=30)),
                ('note6', models.CharField(blank=True, default='', max_length=30)),
                ('note7', models.CharField(blank=True, default='', max_length=30)),
                ('note8', models.CharField(blank=True, default='', max_length=30)),
                ('note9', models.CharField(blank=True, default='', max_length=30)),
                ('nr10', models.PositiveIntegerField()),
                ('nr11', models.PositiveIntegerField()),
                ('nr12', models.PositiveIntegerField()),
                ('nr13', models.PositiveIntegerField()),
                ('nr14', models.PositiveIntegerField()),
                ('nr15', models.PositiveIntegerField()),
                ('note16', models.CharField(blank=True, default='', max_length=30)),
                ('note17', models.CharField(blank=True, default='', max_length=30)),
                ('nr18', models.PositiveIntegerField()),
                ('nr19', models.PositiveIntegerField()),
                ('nr20', models.PositiveIntegerField()),
                ('nr21', models.PositiveIntegerField()),
                ('nr22', models.PositiveIntegerField()),
                ('nr23', models.PositiveIntegerField()),
                ('note24', models.CharField(blank=True, default='', max_length=30)),
                ('note25', models.CharField(blank=True, default='', max_length=30)),
                ('nr26', models.PositiveIntegerField()),
                ('nr27', models.PositiveIntegerField()),
                ('nr28', models.PositiveIntegerField()),
                ('nr29', models.PositiveIntegerField()),
                ('nr30', models.PositiveIntegerField()),
                ('nr31', models.PositiveIntegerField()),
                ('note32', models.CharField(blank=True, default='', max_length=30)),
                ('note33', models.CharField(blank=True, default='', max_length=30)),
                ('nr34', models.PositiveIntegerField()),
                ('nr35', models.PositiveIntegerField()),
                ('nr36', models.PositiveIntegerField()),
                ('nr37', models.PositiveIntegerField()),
                ('nr38', models.PositiveIntegerField()),
                ('nr39', models.PositiveIntegerField()),
                ('note40', models.CharField(blank=True, default='', max_length=30)),
                ('note41', models.CharField(blank=True, default='', max_length=30)),
                ('nr42', models.PositiveIntegerField()),
                ('nr43', models.PositiveIntegerField()),
                ('nr44', models.PositiveIntegerField()),
                ('nr45', models.PositiveIntegerField()),
                ('nr46', models.PositiveIntegerField()),
                ('nr47', models.PositiveIntegerField()),
                ('note48', models.CharField(blank=True, default='', max_length=30)),
                ('note49', models.CharField(blank=True, default='', max_length=30)),
                ('nr50', models.PositiveIntegerField()),
                ('nr51', models.PositiveIntegerField()),
                ('nr52', models.PositiveIntegerField()),
                ('nr53', models.PositiveIntegerField()),
                ('nr54', models.PositiveIntegerField()),
                ('nr55', models.PositiveIntegerField()),
                ('note56', models.CharField(blank=True, default='', max_length=30)),
                ('note57', models.CharField(blank=True, default='', max_length=30)),
                ('note58', models.CharField(blank=True, default='', max_length=30)),
                ('note59', models.CharField(blank=True, default='', max_length=30)),
                ('note60', models.CharField(blank=True, default='', max_length=30)),
                ('note61', models.CharField(blank=True, default='', max_length=30)),
                ('note62', models.CharField(blank=True, default='', max_length=30)),
                ('note63', models.CharField(blank=True, default='', max_length=30)),
                ('note64', models.CharField(blank=True, default='', max_length=30)),
            ],
            options={
                'verbose_name': 'Partial 6x6',
                'verbose_name_plural': 'Partial 6x6',
            },
        ),
        migrations.CreateModel(
            name='Quart6',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('processor', models.PositiveIntegerField(default=0)),
                ('based_on_4x4', models.PositiveBigIntegerField()),
                ('type', models.PositiveSmallIntegerField()),
                ('p1', models.PositiveIntegerField()),
                ('c1', models.PositiveIntegerField()),
                ('p2', models.PositiveIntegerField()),
                ('nr1', models.PositiveSmallIntegerField()),
                ('nr2', models.PositiveSmallIntegerField()),
                ('nr3', models.PositiveSmallIntegerField()),
                ('nr4', models.PositiveSmallIntegerField()),
                ('nr5', models.PositiveSmallIntegerField()),
                ('nr6', models.PositiveSmallIntegerField()),
                ('nr7', models.PositiveSmallIntegerField()),
                ('nr8', models.PositiveSmallIntegerField()),
                ('nr9', models.PositiveSmallIntegerField()),
                ('nr10', models.PositiveSmallIntegerField()),
                ('nr11', models.PositiveSmallIntegerField()),
                ('nr12', models.PositiveSmallIntegerField()),
            ],
            options={
                'verbose_name': 'Quart6',
                'verbose_name_plural': 'Quart6',
                'indexes': [models.Index(fields=['nr1'], name='Partial6x6__nr1_1fe5eb_idx'), models.Index(fields=['nr2'], name='Partial6x6__nr2_417f6d_idx'), models.Index(fields=['nr3'], name='Partial6x6__nr3_80c958_idx'), models.Index(fields=['nr4'], name='Partial6x6__nr4_3cf9c8_idx'), models.Index(fields=['nr5'], name='Partial6x6__nr5_740d2b_idx'), models.Index(fields=['nr6'], name='Partial6x6__nr6_069272_idx'), models.Index(fields=['nr7'], name='Partial6x6__nr7_7fde20_idx'), models.Index(fields=['nr8'], name='Partial6x6__nr8_c8f558_idx'), models.Index(fields=['nr9'], name='Partial6x6__nr9_253e7b_idx'), models.Index(fields=['nr10'], name='Partial6x6__nr10_f3c330_idx'), models.Index(fields=['nr11'], name='Partial6x6__nr11_f02097_idx'), models.Index(fields=['nr12'], name='Partial6x6__nr12_fba2f4_idx'), models.Index(fields=['based_on_4x4'], name='Partial6x6__based_o_326676_idx'), models.Index(fields=['processor'], name='Partial6x6__process_4f307c_idx')],
            },
        ),
    ]

# end of file