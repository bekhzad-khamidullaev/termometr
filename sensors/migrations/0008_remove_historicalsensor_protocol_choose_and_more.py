# Generated by Django 5.0.4 on 2024-04-27 18:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sensors', '0007_historicalsensor_error_sensor_error'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='historicalsensor',
            name='protocol_choose',
        ),
        migrations.RemoveField(
            model_name='sensor',
            name='protocol_choose',
        ),
        migrations.AlterField(
            model_name='historicalsensor',
            name='id',
            field=models.BigIntegerField(auto_created=True, blank=True, db_index=True, verbose_name='ID'),
        ),
        migrations.AlterField(
            model_name='historicalsensor',
            name='protocol',
            field=models.CharField(choices=[('SNMPv2', 'SNMPv2'), ('TCP', 'TCP')], default='SNMPv2', max_length=20),
        ),
        migrations.AlterField(
            model_name='sensor',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
        migrations.AlterField(
            model_name='sensor',
            name='protocol',
            field=models.CharField(choices=[('SNMPv2', 'SNMPv2'), ('TCP', 'TCP')], default='SNMPv2', max_length=20),
        ),
        migrations.AlterField(
            model_name='snmpsettings',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
        migrations.AlterField(
            model_name='tcpsettings',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
    ]
