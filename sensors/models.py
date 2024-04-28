from django.db import models
from simple_history.models import HistoricalRecords
from django.utils import timezone


class Host(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name

class SNMPSettings(models.Model):
    temp_oid = models.CharField(max_length=40)
    community = models.CharField(max_length=20)
    ip = models.GenericIPAddressField()
    port = models.IntegerField(default=0)

class TCPSettings(models.Model):
    port = models.IntegerField(default=0)

class Sensor(models.Model):
    hostname = models.ForeignKey(Host, on_delete=models.CASCADE, related_name='sensors')
    probe_sens_id = models.CharField(max_length=20, null=True, blank=True, unique=True)
    PROTOCOL_CHOICES = (
        ("SNMPv2", "SNMPv2"),
        ("TCP", "TCP"),
    )
    protocol = models.CharField(
        max_length=20,
        choices=PROTOCOL_CHOICES,
        default="TCP"
    )
    temperature = models.FloatField(null=True, blank=True)
    error = models.CharField(max_length=30, null=True, blank=True)
    last_changes_at = models.DateTimeField(default=timezone.now)
    history = HistoricalRecords()
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.protocol == "SNMPv2":
            SNMPSettings.objects.get_or_create(sensor=self)
        elif self.protocol == "TCP":
            TCPSettings.objects.get_or_create()
        else:
            raise ValueError("Invalid protocol specified.")



    def __str__(self):
        return f"{self.hostname.name} - {self.probe_sens_id}"

