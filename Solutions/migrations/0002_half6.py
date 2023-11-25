# Generated by Django 4.2.7 on 2023-11-25 16:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Solutions', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Half6',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('when', models.DateTimeField(auto_now_add=True)),
                ('processor', models.PositiveIntegerField(default=0)),
                ('is_processed', models.BooleanField(default=False)),
                ('based_on_4x4', models.PositiveBigIntegerField()),
                ('type', models.PositiveSmallIntegerField()),
                ('b1', models.PositiveIntegerField()),
                ('b2', models.PositiveIntegerField()),
                ('b3', models.PositiveIntegerField()),
                ('b4', models.PositiveIntegerField()),
                ('b5', models.PositiveIntegerField()),
                ('b6', models.PositiveIntegerField()),
                ('b7', models.PositiveIntegerField()),
                ('b8', models.PositiveIntegerField()),
                ('p1', models.PositiveIntegerField()),
                ('p2', models.PositiveIntegerField()),
                ('c1', models.PositiveIntegerField()),
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
            ],
            options={
                'verbose_name': 'Half6',
                'verbose_name_plural': 'Half6',
                'indexes': [models.Index(fields=['b1'], name='Solutions_h_b1_55b847_idx'), models.Index(fields=['b2'], name='Solutions_h_b2_8925ad_idx'), models.Index(fields=['b3'], name='Solutions_h_b3_dd5df8_idx'), models.Index(fields=['b4'], name='Solutions_h_b4_4fe184_idx'), models.Index(fields=['b5'], name='Solutions_h_b5_d12497_idx'), models.Index(fields=['b6'], name='Solutions_h_b6_c92bbf_idx'), models.Index(fields=['b7'], name='Solutions_h_b7_5dec69_idx'), models.Index(fields=['b8'], name='Solutions_h_b8_cb41aa_idx'), models.Index(fields=['nr1'], name='Solutions_h_nr1_4b44d3_idx'), models.Index(fields=['nr2'], name='Solutions_h_nr2_a62f3b_idx'), models.Index(fields=['nr3'], name='Solutions_h_nr3_29eb40_idx'), models.Index(fields=['nr4'], name='Solutions_h_nr4_7b5f96_idx'), models.Index(fields=['nr5'], name='Solutions_h_nr5_d0ccfb_idx'), models.Index(fields=['nr6'], name='Solutions_h_nr6_640a3b_idx'), models.Index(fields=['nr7'], name='Solutions_h_nr7_24edd5_idx'), models.Index(fields=['nr8'], name='Solutions_h_nr8_828169_idx'), models.Index(fields=['nr9'], name='Solutions_h_nr9_76662d_idx'), models.Index(fields=['nr10'], name='Solutions_h_nr10_f7e638_idx'), models.Index(fields=['nr11'], name='Solutions_h_nr11_7fc543_idx'), models.Index(fields=['nr12'], name='Solutions_h_nr12_0625cb_idx'), models.Index(fields=['nr13'], name='Solutions_h_nr13_a3613c_idx'), models.Index(fields=['nr14'], name='Solutions_h_nr14_d658ad_idx'), models.Index(fields=['nr15'], name='Solutions_h_nr15_293927_idx'), models.Index(fields=['nr16'], name='Solutions_h_nr16_01fe78_idx'), models.Index(fields=['nr17'], name='Solutions_h_nr17_d5a4ef_idx'), models.Index(fields=['nr18'], name='Solutions_h_nr18_480a7d_idx'), models.Index(fields=['nr19'], name='Solutions_h_nr19_20f7d6_idx'), models.Index(fields=['nr20'], name='Solutions_h_nr20_5048fa_idx'), models.Index(fields=['nr21'], name='Solutions_h_nr21_7875e2_idx'), models.Index(fields=['nr22'], name='Solutions_h_nr22_81faf4_idx'), models.Index(fields=['nr23'], name='Solutions_h_nr23_ddcf21_idx'), models.Index(fields=['nr24'], name='Solutions_h_nr24_f662fd_idx'), models.Index(fields=['nr25'], name='Solutions_h_nr25_82f47d_idx'), models.Index(fields=['nr26'], name='Solutions_h_nr26_ac79e9_idx'), models.Index(fields=['nr27'], name='Solutions_h_nr27_66b24c_idx'), models.Index(fields=['nr28'], name='Solutions_h_nr28_6ecfae_idx'), models.Index(fields=['nr29'], name='Solutions_h_nr29_52e478_idx'), models.Index(fields=['nr30'], name='Solutions_h_nr30_b53d22_idx'), models.Index(fields=['nr31'], name='Solutions_h_nr31_f74271_idx'), models.Index(fields=['nr32'], name='Solutions_h_nr32_dba6cb_idx'), models.Index(fields=['nr33'], name='Solutions_h_nr33_afa9cc_idx'), models.Index(fields=['nr34'], name='Solutions_h_nr34_68b492_idx'), models.Index(fields=['nr35'], name='Solutions_h_nr35_a8313f_idx'), models.Index(fields=['nr36'], name='Solutions_h_nr36_110a56_idx')],
            },
        ),
    ]
