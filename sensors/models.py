from django.db import models
from django.contrib.auth.models import User

class SensorData(models.Model):
    sensor_id = models.CharField(max_length=50)
    temperature = models.FloatField()
    humidity = models.FloatField()
    heat_index = models.FloatField()
    uptime = models.CharField(max_length=50)
    datetime = models.DateTimeField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"Sensor {self.sensor_id} - {self.datetime}"
