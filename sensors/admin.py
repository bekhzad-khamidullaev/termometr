from django.contrib import admin
from .models import Sensor, SNMPSettings, TCPSettings

class SensorAdmin(admin.ModelAdmin):
    model = Sensor
    list_display = ['hostname', 'last_changes_at', 'last_update', 'status', 'probe_sens_id', 'temperature', 'error', 'protocol']


admin.site.register(Sensor, SensorAdmin)
admin.site.register(SNMPSettings)
admin.site.register(TCPSettings)

