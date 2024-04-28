import random
import string
from faker import Faker
from django.utils import timezone
from django.core.management.base import BaseCommand
from sensors.models import Host, Sensor, SNMPSettings, TCPSettings

fake = Faker()

class Command(BaseCommand):
    help = "Populate models with random data"

    def handle(self, *args, **options):
        # Create Hosts
        hosts = []
        for _ in range(10):
            host_name = fake.domain_name()
            host, _ = Host.objects.get_or_create(name=host_name)
            hosts.append(host)

        # Create Sensors
        for _ in range(50):
            host = random.choice(hosts)
            ip = fake.ipv4()
            port = random.randint(1000, 9999)
            probe_sens_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
            protocol = random.choice(["SNMPv2", "TCP"])
            temperature = round(random.uniform(10.0, 40.0), 2)
            error = fake.word()
            uptime = fake.sentence()
            last_changes_at = timezone.now()
            last_update = timezone.now()
            status = random.choice([True, False])

            sensor = Sensor.objects.create(
                hostname=host,
                ip=ip,
                port=port,
                probe_sens_id=probe_sens_id,
                protocol=protocol,
                temperature=temperature,
                error=error,
                uptime=uptime,
                last_changes_at=last_changes_at,
                last_update=last_update,
                status=status
            )

            if protocol == "SNMPv2":
                temp_oid = fake.word()
                community = fake.word()
                SNMPSettings.objects.get_or_create(sensor=sensor, ip=ip, port=port)

            elif protocol == "TCP":
                # Check if TCPSettings already exists for the current sensor
                tcp_settings, created = TCPSettings.objects.get_or_create(sensor=sensor)
                # If TCPSettings is not created, update the port
                if created:
                    tcp_settings.port = port
                    tcp_settings.save()


        self.stdout.write(self.style.SUCCESS("Data populated successfully"))
