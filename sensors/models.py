from django.db import models
from simple_history.models import HistoricalRecords
from django.utils import timezone

class SNMPSettings(models.Model):
    temp_oid = models.CharField(max_length=200)
    community = models.CharField(max_length=200)
    ip = models.GenericIPAddressField()
    port = models.IntegerField(default=0)

class TCPSettings(models.Model):
    port = models.IntegerField(default=0)

class Sensor(models.Model):
    hostname = models.CharField(max_length=255, unique=True)
    probe_sens_id = models.CharField(max_length=255, null=True, blank=True, unique=True)
    PROTOCOL_CHOICES = (
        ("SNMPv2", "SNMPv2"),
        ("TCP", "TCP"),
    )
    protocol = models.CharField(
        max_length=20,
        choices=PROTOCOL_CHOICES,
        default="SNMPv2"
    )
    temperature = models.FloatField(null=True, blank=True)
    error = models.CharField(max_length=30, null=True, blank=True)
    last_changes_at = models.DateTimeField(default=timezone.now)
    history = HistoricalRecords()
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)  # Call save() method of the parent class first
        if self.protocol == "SNMPv2":
            SNMPSettings.objects.get_or_create(sensor=self)
        elif self.protocol == "TCP":
            TCPSettings.objects.get_or_create()  # Remove 'sensor=self' argument
        else:
            raise ValueError("Invalid protocol specified.")



    def __str__(self):
        return self.hostname
