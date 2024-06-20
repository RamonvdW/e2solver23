# Generated by Django 4.2.7 on 2024-02-10 15:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Ring1', '0002_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Corner1',
            fields=[
                ('nr', models.AutoField(primary_key=True, serialize=False)),
                ('loc1', models.PositiveIntegerField()),
                ('loc2', models.PositiveIntegerField()),
                ('loc3', models.PositiveIntegerField()),
                ('loc4', models.PositiveIntegerField()),
                ('loc9', models.PositiveIntegerField()),
                ('loc10', models.PositiveIntegerField()),
                ('loc11', models.PositiveIntegerField()),
                ('loc17', models.PositiveIntegerField()),
                ('loc18', models.PositiveIntegerField()),
                ('loc25', models.PositiveIntegerField()),
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
                ('nr13', models.PositiveSmallIntegerField()),
                ('nr14', models.PositiveSmallIntegerField()),
                ('nr15', models.PositiveSmallIntegerField()),
                ('nr16', models.PositiveSmallIntegerField()),
                ('nr17', models.PositiveSmallIntegerField()),
                ('nr18', models.PositiveSmallIntegerField()),
                ('nr19', models.PositiveSmallIntegerField()),
                ('nr20', models.PositiveSmallIntegerField()),
                ('nr21', models.PositiveSmallIntegerField()),
                ('nr22', models.PositiveSmallIntegerField()),
                ('nr23', models.PositiveSmallIntegerField()),
                ('nr24', models.PositiveSmallIntegerField()),
                ('nr25', models.PositiveSmallIntegerField()),
                ('nr26', models.PositiveSmallIntegerField()),
                ('nr27', models.PositiveSmallIntegerField()),
                ('nr28', models.PositiveSmallIntegerField()),
                ('nr29', models.PositiveSmallIntegerField()),
                ('nr30', models.PositiveSmallIntegerField()),
                ('nr31', models.PositiveSmallIntegerField()),
                ('nr32', models.PositiveSmallIntegerField()),
                ('nr33', models.PositiveSmallIntegerField()),
                ('nr34', models.PositiveSmallIntegerField()),
                ('nr35', models.PositiveSmallIntegerField()),
                ('nr36', models.PositiveSmallIntegerField()),
                ('nr37', models.PositiveSmallIntegerField()),
                ('nr38', models.PositiveSmallIntegerField()),
                ('nr39', models.PositiveSmallIntegerField()),
                ('nr40', models.PositiveSmallIntegerField()),
            ],
            options={
                'verbose_name': 'Corner1',
                'indexes': [models.Index(fields=['nr1'], name='Ring1_corne_nr1_bcbffa_idx'),    # noqa
                            models.Index(fields=['nr2'], name='Ring1_corne_nr2_5ccfaf_idx'),    # noqa
                            models.Index(fields=['nr3'], name='Ring1_corne_nr3_e26110_idx'),
                            models.Index(fields=['nr4'], name='Ring1_corne_nr4_224a77_idx'),
                            models.Index(fields=['nr5'], name='Ring1_corne_nr5_9dad63_idx'),
                            models.Index(fields=['nr6'], name='Ring1_corne_nr6_dc6421_idx'),
                            models.Index(fields=['nr7'], name='Ring1_corne_nr7_64b06d_idx'),
                            models.Index(fields=['nr8'], name='Ring1_corne_nr8_fe3d73_idx'),
                            models.Index(fields=['nr9'], name='Ring1_corne_nr9_442f55_idx'),
                            models.Index(fields=['nr10'], name='Ring1_corne_nr10_3e1fd8_idx'),
                            models.Index(fields=['nr12'], name='Ring1_corne_nr12_951daf_idx'),
                            models.Index(fields=['nr13'], name='Ring1_corne_nr13_b97680_idx'),
                            models.Index(fields=['nr14'], name='Ring1_corne_nr14_5284d8_idx'),
                            models.Index(fields=['nr15'], name='Ring1_corne_nr15_61bde8_idx'),
                            models.Index(fields=['nr16'], name='Ring1_corne_nr16_47678f_idx'),
                            models.Index(fields=['nr17'], name='Ring1_corne_nr17_e3c652_idx'),
                            models.Index(fields=['nr18'], name='Ring1_corne_nr18_47c903_idx'),
                            models.Index(fields=['nr19'], name='Ring1_corne_nr19_79db88_idx'),
                            models.Index(fields=['nr20'], name='Ring1_corne_nr20_7112de_idx'),
                            models.Index(fields=['nr21'], name='Ring1_corne_nr21_771509_idx'),
                            models.Index(fields=['nr22'], name='Ring1_corne_nr22_68c9e0_idx'),
                            models.Index(fields=['nr23'], name='Ring1_corne_nr23_df6347_idx'),
                            models.Index(fields=['nr24'], name='Ring1_corne_nr24_645a52_idx'),
                            models.Index(fields=['nr25'], name='Ring1_corne_nr25_fbc80d_idx'),
                            models.Index(fields=['nr26'], name='Ring1_corne_nr26_5e7cab_idx'),
                            models.Index(fields=['nr27'], name='Ring1_corne_nr27_5211f1_idx'),
                            models.Index(fields=['nr28'], name='Ring1_corne_nr28_1218e4_idx'),
                            models.Index(fields=['nr29'], name='Ring1_corne_nr29_26c8cf_idx'),
                            models.Index(fields=['nr30'], name='Ring1_corne_nr30_fbaef7_idx'),  # noqa
                            models.Index(fields=['nr31'], name='Ring1_corne_nr31_0fa62f_idx'),
                            models.Index(fields=['nr32'], name='Ring1_corne_nr32_f95094_idx'),
                            models.Index(fields=['nr33'], name='Ring1_corne_nr33_c633e0_idx'),
                            models.Index(fields=['nr34'], name='Ring1_corne_nr34_32b2b5_idx'),
                            models.Index(fields=['nr35'], name='Ring1_corne_nr35_7c2a46_idx'),
                            models.Index(fields=['nr36'], name='Ring1_corne_nr36_f5ec1d_idx'),
                            models.Index(fields=['nr37'], name='Ring1_corne_nr37_5a5962_idx'),
                            models.Index(fields=['nr38'], name='Ring1_corne_nr38_2e210e_idx'),
                            models.Index(fields=['nr39'], name='Ring1_corne_nr39_222c31_idx'),
                            models.Index(fields=['nr40'], name='Ring1_corne_nr40_061d2d_idx')],
            },
        ),
    ]
