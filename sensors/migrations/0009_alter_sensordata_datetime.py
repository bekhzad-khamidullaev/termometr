# Generated by Django 5.0.4 on 2024-07-01 16:34

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sensors', '0008_alter_sensordata_humidity'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sensordata',
            name='datetime',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]
