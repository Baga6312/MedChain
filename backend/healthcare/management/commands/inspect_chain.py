from django.core.management.base import BaseCommand

from healthcare.blockchain import anchoring, crypto
from healthcare.models import Anchor, TreatmentEvent


class Command(BaseCommand):
    help = "Show the latest event: block, decrypted payload and on-chain anchor."

    def add_arguments(self, parser):
        parser.add_argument("--episode", type=int)

    def handle(self, *args, **opts):
        qs = TreatmentEvent.objects.filter(block__isnull=False)
        if opts["episode"]:
            qs = qs.filter(treatment_episode_id=opts["episode"])
        ev = qs.select_related("block", "treatment_episode").order_by("-created_at").first()
        if ev is None:
            return self.stdout.write("No event with a block.")
        b, w = ev.block, self.stdout.write
        blob = bytes(b.payload_enc)
        p = crypto.decrypt_payload(ev.treatment_episode, b.chain_id, b.index, blob)

        w(f"EVENT    {ev.event_id}  [{ev.event_type}] {ev.title}")
        w(f"BLOCK    {b.chain} #{b.index}  hash={b.block_hash[:20]}…  prev={b.prev_hash[:20]}…  nonce={b.nonce}")
        w(f"STORED   ciphertext {len(blob)} bytes, starts {blob[:10].hex()}  (no plaintext in the DB block)")
        w(f"DECRYPT  outcome={p['outcome']!r}  title={p['title']!r}  description={p['description']!r}")

        a = (Anchor.objects
             .filter(treatment_episode=ev.treatment_episode, chain=b.chain, block_index__gte=b.index)
             .order_by("block_index").first())
        if a is None:
            return w("ANCHOR   none yet (run: manage.py anchor_chains)")
        onchain = bytes(anchoring._w3().eth.get_transaction(a.tx_hash)["input"])
        want = anchoring.anchor_data(b.chain_id, a.block_hash)
        w(f"ANCHOR   tx={a.tx_hash}  eth block={a.eth_block}  covers block #{a.block_index}")
        w(f"ONCHAIN  input=0x{onchain.hex()}")
        w(f"MATCH    {'YES' if onchain == want else 'NO'}")