from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta

class SensorData(models.Model):
    sensor_id = models.CharField(max_length=100)
    temperature = models.FloatField(null=True)
    humidity = models.FloatField(null=True)
    heat_index = models.FloatField(null=True)
    uptime = models.CharField(max_length=50)
    datetime = models.DateTimeField(default=timezone.now)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.BooleanField(default=False)

    def __str__(self):
        return f"Sensor {self.sensor_id} - {self.datetime}"

    def save(self, *args, **kwargs):
        if not self.datetime:
            self.datetime = timezone.now()

        # Check if this instance has a primary key (i.e., it's being updated)
        if self.pk:
            last_modified = SensorData.objects.filter(pk=self.pk).values_list('datetime', flat=True).first()
            if last_modified and timezone.now() - last_modified > timedelta(minutes=1):
                self.status = False  # Update status to False if no update within 1 minute
            else:
                self.status = True   # Keep status as True if updated within 1 minute

        super().save(*args, **kwargs)
