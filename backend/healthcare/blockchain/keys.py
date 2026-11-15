import base64
import os
from abc import ABC, abstractmethod

from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

_AAD = b"medchain-dek"


class KeyProvider(ABC):
    key_id: str

    @abstractmethod
    def generate_data_key(self):
        """Return (plaintext_dek, wrapped_dek)."""

    @abstractmethod
    def unwrap(self, wrapped: bytes) -> bytes:
        """Return the plaintext DEK."""


class EnvKeyProvider(KeyProvider):
    """Master key from the environment. Swap for a KMS provider later."""

    def __init__(self):
        raw = base64.b64decode(settings.MEDCHAIN_MASTER_KEY or "")
        if len(raw) != 32:
            raise ImproperlyConfigured("MEDCHAIN_MASTER_KEY must be 32 bytes, base64-encoded.")
        self._kek = AESGCM(raw)
        self.key_id = settings.MEDCHAIN_KEY_ID

    def generate_data_key(self):
        dek = AESGCM.generate_key(bit_length=256)
        nonce = os.urandom(12)
        return dek, nonce + self._kek.encrypt(nonce, dek, _AAD)

    def unwrap(self, wrapped: bytes) -> bytes:
        wrapped = bytes(wrapped)
        return self._kek.decrypt(wrapped[:12], wrapped[12:], _AAD)


def get_key_provider() -> KeyProvider:
    # Later: return KmsKeyProvider() (kms.generate_data_key / kms.decrypt).
    return EnvKeyProvider()