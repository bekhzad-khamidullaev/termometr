import socket
import re
import logging
from django.core.management.base import BaseCommand
from sensors.models import Sensor

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = "TCP messages listener"

    def handle(self, *args, **options):
        HOST = "0.0.0.0"
        PORT = 1234
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            try:
                sock.bind((HOST, PORT))
                sock.listen()
                self.stdout.write(self.style.SUCCESS(f"Listening on {HOST}:{PORT}"))

                while True:
                    conn, addr = sock.accept()
                    self.stdout.write(self.style.SUCCESS(f"Connection established from {addr}"))
                    try:
                        parsed_data = conn.recv(1024).decode('utf-8')
                        pattern = re.compile(r'\n|#')
                        lines = pattern.split(parsed_data.strip('#'))
                        lines = list(filter(lambda x: x.strip(), lines))
                        hostname = lines[0]
                        sensor_id = lines[1]  # Rename to sensor_id for clarity
                        temperature = lines[2]
                        error_code = lines[4]
                        self.stdout.write(self.style.SUCCESS(f"hostname:{hostname} sensor_id:{sensor_id} temperature:{temperature}, error_code:{error_code}"))
                        
                        sensor, created = Sensor.objects.get_or_create(hostname=hostname)
                        sensor.temperature = float(temperature)
                        sensor.probe_sens_id = sensor_id
                        sensor.error = error_code
                        sensor.save()  # Actually save the sensor data
                        
                        self.stdout.write(self.style.SUCCESS("SAVED"))

                    except socket.error as e:
                        logger.error(f"Socket error occurred: {e}")
                    except ValueError as e:
                        logger.error(f"ValueError occurred: {e}")
                    except Exception as e:
                        logger.error(f"Error occurred: {e}")
                    finally:
                        conn.close()

            except KeyboardInterrupt:
                self.stdout.write(self.style.ERROR("Keyboard interrupt received. Exiting..."))
