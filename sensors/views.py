from django.shortcuts import render
from .models import Sensor

def index(request):
    return render(request, 'index.html')

def sensors(request):
    sensors = Sensor.objects.all
    return render(request, 'sensors.html', {"sensors": sensors})