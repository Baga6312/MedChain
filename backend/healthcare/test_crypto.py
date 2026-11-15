import base64

from cryptography.exceptions import InvalidTag
from django.test import TestCase, override_settings

from . import crypto
from .models import Doctor, EpisodeKey, Patient, TreatmentEpisode

KEY = base64.b64encode(bytes(range(32))).decode()
OTHER = base64.b64encode(bytes(range(1, 33))).decode()
PAYLOAD = {"title": "secret diagnosis", "outcome": "recovering"}


@override_settings(MEDCHAIN_MASTER_KEY=KEY, MEDCHAIN_KEY_ID="test-v1")
class CryptoTests(TestCase):
    def setUp(self):
        self.ep = TreatmentEpisode.objects.create(
            patient=Patient.objects.create(name="P", phone="1"),
            doctor=Doctor.objects.create(name="D", specialty="GP"),
        )

    def test_roundtrip(self):
        blob = crypto.encrypt_payload(self.ep, "1:user", 1, PAYLOAD)
        self.assertEqual(crypto.decrypt_payload(self.ep, "1:user", 1, blob), PAYLOAD)

    def test_ciphertext_hides_plaintext(self):
        blob = crypto.encrypt_payload(self.ep, "1:user", 1, PAYLOAD)
        self.assertNotIn(b"secret", blob)

    def test_bound_to_position(self):
        blob = crypto.encrypt_payload(self.ep, "1:user", 1, PAYLOAD)
        with self.assertRaises(InvalidTag):
            crypto.decrypt_payload(self.ep, "1:user", 2, blob)
        with self.assertRaises(InvalidTag):
            crypto.decrypt_payload(self.ep, "1:doctor", 1, blob)

    def test_tamper_detected(self):
        blob = bytearray(crypto.encrypt_payload(self.ep, "1:user", 1, PAYLOAD))
        blob[-1] ^= 1
        with self.assertRaises(InvalidTag):
            crypto.decrypt_payload(self.ep, "1:user", 1, bytes(blob))

    def test_one_wrapped_key_per_episode(self):
        crypto.encrypt_payload(self.ep, "1:user", 1, PAYLOAD)
        crypto.encrypt_payload(self.ep, "1:user", 2, PAYLOAD)
        self.assertEqual(EpisodeKey.objects.count(), 1)

    def test_wrong_master_key_cannot_unwrap(self):
        blob = crypto.encrypt_payload(self.ep, "1:user", 1, PAYLOAD)
        with self.settings(MEDCHAIN_MASTER_KEY=OTHER):
            with self.assertRaises(InvalidTag):
                crypto.decrypt_payload(self.ep, "1:user", 1, blob)

    def test_tx_hash_is_of_ciphertext(self):
        blob = crypto.encrypt_payload(self.ep, "1:user", 1, PAYLOAD)
        self.assertEqual(crypto.tx_hash(blob), crypto.ledger.sha256_hex(blob))
        self.assertEqual(len(crypto.tx_hash(blob)), 64)