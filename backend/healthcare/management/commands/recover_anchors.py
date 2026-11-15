from django.core.management.base import BaseCommand
from web3.exceptions import TransactionNotFound

from healthcare.blockchain import anchoring
from healthcare.models import Anchor, Block, TreatmentEpisode


class Command(BaseCommand):
    help = "Remove invalid local anchors and recreate anchors for current chain heads."

    def handle(self, *args, **opts):
        web3 = anchoring._w3()
        removed = 0

        for anchor in Anchor.objects.select_related("treatment_episode").all():
            block = Block.objects.filter(
                treatment_episode=anchor.treatment_episode,
                chain=anchor.chain,
                index=anchor.block_index,
            ).first()
            invalid = block is None or block.block_hash != anchor.block_hash
            if not invalid:
                try:
                    transaction = web3.eth.get_transaction(anchor.tx_hash)
                    invalid = bytes(transaction["input"]) != anchoring.anchor_data(
                        block.chain_id,
                        block.block_hash,
                    )
                except TransactionNotFound:
                    invalid = True

            if invalid:
                self.stdout.write(
                    f"Removing invalid anchor episode {anchor.treatment_episode_id} "
                    f"{anchor.chain} #{anchor.block_index}."
                )
                anchor.delete()
                removed += 1

        created = 0
        for episode in TreatmentEpisode.objects.all():
            for chain_name in Block.Chain.values:
                anchor = anchoring.anchor_head(episode, chain_name)
                if anchor:
                    self.stdout.write(
                        f"Anchored episode {episode.id} {chain_name} "
                        f"#{anchor.block_index} -> {anchor.tx_hash[:14]}."
                    )
                    created += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Anchor recovery complete: {removed} removed, {created} created."
            )
        )
