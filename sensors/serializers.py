from rest_framework import serializers
from .models import SensorData

class SensorDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = SensorData
        fields = ('temperature', 'humidity', 'heat_index', 'datetime', 'sensor_id', 'uptime')
