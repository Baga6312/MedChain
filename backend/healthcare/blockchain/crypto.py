import json
import os

from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from . import ledger
from .keys import get_key_provider

VERSION = b"\x01"


def _dek(episode, create):
    from ..models import EpisodeKey

    provider = get_key_provider()
    row = EpisodeKey.objects.filter(treatment_episode=episode).first()
    if row is None:
        if not create:
            raise LookupError("No key exists for this episode.")
        dek, wrapped = provider.generate_data_key()
        row, created = EpisodeKey.objects.get_or_create(
            treatment_episode=episode,
            defaults={"wrapped_dek": wrapped, "kek_id": provider.key_id},
        )
        if created:
            return dek
    return provider.unwrap(row.wrapped_dek)


def _aad(chain_id, index):
    return f"{chain_id}:{index}".encode()


def encrypt_payload(episode, chain_id, index, payload) -> bytes:
    nonce = os.urandom(12)
    ct = AESGCM(_dek(episode, True)).encrypt(nonce, ledger.canonical(payload), _aad(chain_id, index))
    return VERSION + nonce + ct


def decrypt_payload(episode, chain_id, index, blob) -> dict:
    blob = bytes(blob)
    if blob[:1] != VERSION:
        raise ValueError("Unsupported ciphertext version.")
    plain = AESGCM(_dek(episode, False)).decrypt(blob[1:13], blob[13:], _aad(chain_id, index))
    return json.loads(plain)


def tx_hash(blob) -> str:
    return ledger.sha256_hex(bytes(blob))