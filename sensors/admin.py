from django.contrib import admin
from .models import Sensor, SNMPSettings, TCPSettings

admin.site.register(Sensor)
admin.site.register(SNMPSettings)
admin.site.register(TCPSettings)

