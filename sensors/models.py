from django.db import models
from simple_history.models import HistoricalRecords


class Sensor(models.Model):
    hostname = models.CharField(max_length=255)
    sensor_id = models.IntegerField()
    PROTO_CHOICES = (
        ("SNMPv2", "snmp2"),
        ("TCP", "tcp"),
    )
    protocol = models.CharField(
        max_length=20,
        choices=PROTO_CHOICES,
        default="SNMPv2"
    )
    port = models.IntegerField()
    history = HistoricalRecords()
    temperature = models.FloatField(null=True, blank=True)
class SNMPSettings(models.Model):
    sensor = models.OneToOneField(Sensor, on_delete=models.CASCADE, primary_key=True)
    temp_oid = models.CharField(max_length=200)
    community = models.CharField(max_length=200)
    ip = models.GenericIPAddressField()

class TCPSettings(models.Model):
    sensor = models.OneToOneField(Sensor, on_delete=models.CASCADE, primary_key=True)
    ip = models.GenericIPAddressField()
