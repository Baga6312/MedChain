import hashlib
import json
from datetime import timezone

from django.conf import settings

GENESIS_PREV_HASH = "0" * 64


def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical(obj) -> bytes:
    return json.dumps(
        obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")


def merkle_root(tx_hashes):
    if not tx_hashes:
        return sha256_hex(b"")
    level = list(tx_hashes)
    while len(level) > 1:
        if len(level) % 2:
            level.append(level[-1])
        level = [sha256_hex((a + b).encode()) for a, b in zip(level[::2], level[1::2])]
    return level[0]


def header_hash(*, chain_id, index, prev_hash, merkle_root, timestamp, nonce):
    return sha256_hex(canonical({
        "chain_id": chain_id,
        "index": index,
        "prev_hash": prev_hash,
        "merkle_root": merkle_root,
        "timestamp": timestamp,
        "nonce": nonce,
    }))


def difficulty() -> int:
    return int(getattr(settings, "BLOCKCHAIN_DIFFICULTY", 3))


def mine(*, chain_id, index, prev_hash, merkle_root, timestamp, diff=None):
    """Find a nonce so the header hash starts with `diff` zero hex digits."""
    target = "0" * (difficulty() if diff is None else diff)
    nonce = 0
    while True:
        h = header_hash(
            chain_id=chain_id, index=index, prev_hash=prev_hash,
            merkle_root=merkle_root, timestamp=timestamp, nonce=nonce,
        )
        if h.startswith(target):
            return nonce, h
        nonce += 1


def event_payload(event) -> dict:
    """The transaction content recorded for a TreatmentEvent."""
    return {
        "event_id": str(event.event_id),
        "episode": event.treatment_episode_id,
        "phase": event.treatment_phase_id,
        "appointment": event.appointment_id,
        "author": event.author_id,
        "event_type": event.event_type,
        "title": event.title,
        "description": event.description,
        "result": event.result,
        "outcome": event.outcome,
        "created_at": event.created_at.astimezone(timezone.utc).isoformat(),
    }