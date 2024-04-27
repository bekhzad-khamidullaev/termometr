from django.db import models
from simple_history.models import HistoricalRecords
from django.utils import timezone
from django.db import transaction

class SNMPSettings(models.Model):
    id = models.IntegerField(default=0, primary_key=True)
    # sensor = models.OneToOneField(Sensor, on_delete=models.CASCADE)
    temp_oid = models.CharField(max_length=200)
    community = models.CharField(max_length=200)
    ip = models.GenericIPAddressField()
    port = models.IntegerField(default=0)

class TCPSettings(models.Model):
    id = models.IntegerField(default=0, primary_key=True)
    # sensor = models.OneToOneField('Sensor', on_delete=models.CASCADE)

class Sensor(models.Model):
    id = models.IntegerField(default=0, primary_key=True)
    hostname = models.CharField(max_length=255, unique=True)
    probe_sens_id = models.CharField(max_length=255, null=True, blank=True, unique=True)
    PROTO_CHOICES = (
        ("SNMPv2", "SNMPv2"),
        ("TCP", "TCP"),
    )
    protocol_choose = models.CharField(
        max_length=20,
        choices=PROTO_CHOICES,
        default="SNMPv2"
    )
    if protocol_choose == "SNMPv2":
        protocol = models.ForeignKey(SNMPSettings, on_delete=models.CASCADE)
    
    else:
        protocol = models.ForeignKey(TCPSettings, on_delete=models.CASCADE)
    
    temperature = models.FloatField(null=True, blank=True)
    last_changes_at = models.DateTimeField(default=timezone.now)
    history = HistoricalRecords()
    
    def __str__ (self):
        return self.hostname

@transaction.atomic
def create_sensor_with_settings(hostname, probe_sens_id, protocol, temperature=None, temp_oid=None, community=None, ip=None, port=None):
    sensor = Sensor.objects.create(hostname=hostname, probe_sens_id=probe_sens_id, protocol_choose=protocol, temperature=temperature)
    if protocol == "SNMPv2":
        SNMPSettings.objects.create(sensor=sensor, temp_oid=temp_oid, community=community, ip=ip, port=port)
    elif protocol == "TCP":
        tcp_settings = TCPSettings.objects.create()
        sensor.protocol = tcp_settings
        sensor.save()
    else:
        raise ValueError("Invalid protocol specified.")
    return sensor
