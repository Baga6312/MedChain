from django.core.management.base import BaseCommand

from healthcare.blockchain import anchoring
from healthcare.models import Block, TreatmentEpisode


class Command(BaseCommand):
    help = "Anchor each episode chain's head hash on the blockchain service."

    def handle(self, *args, **opts):
        n = 0
        for ep in TreatmentEpisode.objects.all():
            for chain in Block.Chain.values:
                a = anchoring.anchor_head(ep, chain)
                if a:
                    n += 1
                    self.stdout.write(f"episode {ep.id} {chain} #{a.block_index} -> {a.tx_hash[:14]} (eth block {a.eth_block})")
        self.stdout.write(f"{n} anchor(s) written.")