# Generated by Django 4.2.7 on 2024-01-21 19:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('WorkQueue', '0005_processorusedpieces'),
    ]

    operations = [
        migrations.AddField(
            model_name='processorusedpieces',
            name='claimed_nrs_double',
            field=models.CharField(default='', max_length=512),
        ),
        migrations.AddField(
            model_name='processorusedpieces',
            name='claimed_nrs_single',
            field=models.CharField(default='', max_length=512),
        ),
    ]

# end of file