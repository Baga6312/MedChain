import base64

from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings

from ..blockchain import chain
from ..models import Block, Doctor, Patient, TreatmentEpisode, TreatmentEvent, UserProfile

KEY = base64.b64encode(bytes(range(32))).decode()
U = get_user_model()


def make_user(name, role):
    user = U.objects.create_user(**{U.USERNAME_FIELD: f"{name}@test.local"}, password="Pass12345!x")
    UserProfile.objects.create(user=user, role=role)
    return user


@override_settings(MEDCHAIN_MASTER_KEY=KEY, BLOCKCHAIN_DIFFICULTY=1)
class ChainTests(TestCase):
    def setUp(self):
        self.doc = make_user("doc", "doctor")
        self.pat = make_user("pat", "patient")
        d = Doctor.objects.create(user=self.doc, name="D", specialty="GP")
        p = Patient.objects.create(user=self.pat, name="P", phone="1")
        self.ep = TreatmentEpisode.objects.create(patient=p, doctor=d, status="active")

    def ev(self, user, event_type="note"):
        return TreatmentEvent.objects.create(
            treatment_episode=self.ep, author=user, event_type=event_type,
            title="secret title", description="d",
        )

    def blocks(self, name):
        return list(Block.objects.filter(treatment_episode=self.ep, chain=name).order_by("index"))

    def test_routing_by_author_role(self):
        self.ev(self.pat)
        self.ev(self.doc)
        self.assertEqual(len(self.blocks("user")), 2)    # genesis + 1
        self.assertEqual(len(self.blocks("doctor")), 2)

    def test_linked_and_valid(self):
        self.ev(self.pat)
        self.ev(self.pat)
        b = self.blocks("user")
        self.assertEqual([x.index for x in b], [0, 1, 2])
        self.assertEqual(b[2].prev_hash, b[1].block_hash)
        self.assertEqual(chain.verify_episode(self.ep), [])

    def test_payload_is_encrypted(self):
        self.ev(self.pat)
        self.assertNotIn(b"secret", bytes(self.blocks("user")[1].payload_enc))

    def test_tampered_header_detected(self):
        self.ev(self.pat)
        self.ev(self.pat)
        Block.objects.filter(treatment_episode=self.ep, chain="user", index=1).update(merkle_root="f" * 64)
        self.assertTrue(chain.verify_episode(self.ep))

    def test_tampered_payload_detected(self):
        self.ev(self.pat)
        Block.objects.filter(treatment_episode=self.ep, chain="user", index=1).update(payload_enc=b"x")
        self.assertTrue(chain.verify_episode(self.ep))

    def test_deleted_block_detected(self):
        e = self.ev(self.pat)
        Block.objects.filter(event=e).delete()
        self.assertTrue(chain.verify_episode(self.ep))