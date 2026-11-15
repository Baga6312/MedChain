import time

from django.db import transaction

from . import crypto, ledger
from ..models import Block, TreatmentEpisode, TreatmentEvent, UserProfile

GENESIS_TX = ledger.sha256_hex(b"genesis")


def _chain_for(author):
    role = getattr(getattr(author, "profile", None), "role", None)
    return Block.Chain.USER if role == UserProfile.Role.PATIENT else Block.Chain.DOCTOR


def _new_block(episode, chain, index, prev_hash, txs, **body):
    chain_id = f"{episode.id}:{chain}"
    root = ledger.merkle_root(txs)
    ts = int(time.time())
    nonce, bh = ledger.mine(
        chain_id=chain_id, index=index, prev_hash=prev_hash, merkle_root=root, timestamp=ts
    )
    return Block.objects.create(
        treatment_episode=episode, chain=chain, index=index, prev_hash=prev_hash,
        merkle_root=root, timestamp=ts, nonce=nonce, block_hash=bh, **body,
    )


@transaction.atomic
def append_event(event):
    episode = event.treatment_episode
    TreatmentEpisode.objects.select_for_update().get(pk=episode.pk)  # serialize appends
    chain = _chain_for(event.author)
    chain_id = f"{episode.id}:{chain}"

    last = Block.objects.filter(treatment_episode=episode, chain=chain).order_by("-index").first()
    if last is None:
        last = _new_block(episode, chain, 0, ledger.GENESIS_PREV_HASH, [], tx_hash=GENESIS_TX)

    index = last.index + 1
    blob = crypto.encrypt_payload(episode, chain_id, index, ledger.event_payload(event))
    txh = crypto.tx_hash(blob)
    return _new_block(
        episode, chain, index, last.block_hash, [txh],
        event=event, tx_hash=txh, payload_enc=blob,
    )


def verify_chain(episode, chain):
    errors, prev = [], None
    for b in Block.objects.filter(treatment_episode=episode, chain=chain).order_by("index"):
        want_index = 0 if prev is None else prev.index + 1
        want_prev = ledger.GENESIS_PREV_HASH if prev is None else prev.block_hash
        txs = [] if b.event_id is None else [b.tx_hash]
        if b.index != want_index:
            errors.append(f"block {b.index}: index gap (expected {want_index})")
        if b.prev_hash != want_prev:
            errors.append(f"block {b.index}: broken link to previous block")
        if b.merkle_root != ledger.merkle_root(txs):
            errors.append(f"block {b.index}: merkle root mismatch")
        if b.event_id is not None and b.tx_hash != crypto.tx_hash(b.payload_enc):
            errors.append(f"block {b.index}: payload does not match tx_hash")
        if b.block_hash != b.compute_hash():
            errors.append(f"block {b.index}: block hash mismatch")
        prev = b
    return errors


def verify_episode(episode):
    errors = []
    for chain in Block.Chain.values:
        errors += [f"{chain}: {e}" for e in verify_chain(episode, chain)]
    for ev in TreatmentEvent.objects.filter(treatment_episode=episode, block__isnull=True):
        errors.append(f"event {ev.event_id} has no block")
    return errors