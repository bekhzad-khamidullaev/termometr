import socket
import re
from django.core.management.base import BaseCommand
from sensors.models import Sensor

class Command(BaseCommand):
    help = "TCP messages listener"

    def handle(self, *args, **options):
        HOST = "0.0.0.0"
        PORT = 1234
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.bind((HOST, PORT))
            sock.listen()
            self.stdout.write(self.style.SUCCESS(f"Listening on {HOST}:{PORT}"))

            while True:
                conn, addr = sock.accept()
                self.stdout.write(self.style.SUCCESS(f"Connection established from {addr}"))

                try:
                    parsed_data = conn.recv(1024).decode('utf-8')


                    string_data = re.findall(r'(?s)(?<=#).*?(?=#)', parsed_data)
                    json_data = {'device_ip': addr[0], 'device_port': addr[1], 'device_id': string_data[0]}
                    for i in range(1, len(string_data) - 1, 2):
                        json_data[string_data[i]] = string_data[i + 1]

                    device_id = json_data['device_id'].strip()
                    try:
                        sensor = Sensor.objects.get(hostname=device_id)
                    except Sensor.DoesNotExist:
                        self.stderr.write(self.style.ERROR(f"Sensor with hostname {device_id} does not exist. Skipping data processing."))
                        continue
                    
                    temperature = float(json_data.get('T1', 0.0))
                    sensor.temperature = temperature
                    sensor.save()

                    self.stdout.write(self.style.SUCCESS(f"Received data from {device_id}: {json_data}"))
                except Exception as e:
                    self.stderr.write(self.style.ERROR(f"Error occurred: {e}"))
                finally:
                    conn.close()
