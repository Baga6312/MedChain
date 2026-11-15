from django.core.management.base import BaseCommand

from healthcare.blockchain.chain import append_event
from healthcare.models import TreatmentEvent


class Command(BaseCommand):
    help = "Append chain blocks for events that have none."

    def handle(self, *args, **opts):
        n = 0
        for ev in TreatmentEvent.objects.filter(block__isnull=True).order_by("created_at"):
            append_event(ev)
            n += 1
        self.stdout.write(f"{n} block(s) appended.")