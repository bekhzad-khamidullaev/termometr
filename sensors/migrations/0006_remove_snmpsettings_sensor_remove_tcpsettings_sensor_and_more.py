# Generated by Django 5.0.4 on 2024-04-23 08:39

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sensors', '0005_historicalsensor_last_changes_at_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='snmpsettings',
            name='sensor',
        ),
        migrations.RemoveField(
            model_name='tcpsettings',
            name='sensor',
        ),
        migrations.AddField(
            model_name='historicalsensor',
            name='protocol_choose',
            field=models.CharField(choices=[('SNMPv2', 'SNMPv2'), ('TCP', 'TCP')], default='SNMPv2', max_length=20),
        ),
        migrations.AddField(
            model_name='sensor',
            name='protocol_choose',
            field=models.CharField(choices=[('SNMPv2', 'SNMPv2'), ('TCP', 'TCP')], default='SNMPv2', max_length=20),
        ),
        migrations.AlterField(
            model_name='historicalsensor',
            name='protocol',
            field=models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='sensors.tcpsettings'),
        ),
        migrations.AlterField(
            model_name='sensor',
            name='protocol',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='sensors.tcpsettings'),
        ),
    ]