from django.core.management.base import BaseCommand

from healthcare.blockchain import anchoring, chain
from healthcare.models import TreatmentEpisode


class Command(BaseCommand):
    help = "Verify the Postgres ledger and its on-chain anchors."

    def handle(self, *args, **opts):
        for ep in TreatmentEpisode.objects.all():
            errors = chain.verify_episode(ep) + anchoring.verify_anchors(ep)
            self.stdout.write(f"episode {ep.id}: {'OK' if not errors else errors}")