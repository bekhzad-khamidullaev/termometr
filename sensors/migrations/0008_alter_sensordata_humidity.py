# Generated by Django 5.0.4 on 2024-07-01 16:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sensors', '0007_alter_sensordata_heat_index_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sensordata',
            name='humidity',
            field=models.FloatField(null=True),
        ),
    ]
