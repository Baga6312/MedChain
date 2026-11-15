from unittest.mock import patch

from django.test import TestCase, override_settings

from ..blockchain import anchoring
from ..models import Anchor, Block, Doctor, Patient, TreatmentEpisode, TreatmentEvent
from .test_chain import KEY, make_user


@override_settings(MEDCHAIN_MASTER_KEY=KEY, BLOCKCHAIN_DIFFICULTY=1)
class AnchorTests(TestCase):
    def setUp(self):
        pat, doc = make_user("pat", "patient"), make_user("doc", "doctor")
        d = Doctor.objects.create(user=doc, name="D", specialty="GP")
        p = Patient.objects.create(user=pat, name="P", phone="1")
        self.ep = TreatmentEpisode.objects.create(patient=p, doctor=d, status="active")
        TreatmentEvent.objects.create(
            treatment_episode=self.ep, author=pat, event_type="note", title="t", description="d"
        )
        self.head = Block.objects.filter(treatment_episode=self.ep, chain="user").order_by("-index").first()
        Anchor.objects.create(
            treatment_episode=self.ep, chain="user", block_index=self.head.index,
            block_hash=self.head.block_hash, tx_hash="0x" + "a" * 64, eth_block=1,
        )

    def good(self):
        return anchoring.anchor_data(self.head.chain_id, self.head.block_hash)

    def verify(self, onchain):
        with patch("healthcare.blockchain.anchoring._w3") as w3:
            w3.return_value.eth.get_transaction.return_value = {"input": onchain}
            return anchoring.verify_anchors(self.ep)

    def test_data_format(self):
        self.assertEqual(len(self.good()), 67)
        self.assertTrue(self.good().startswith(b"MC1"))

    def test_ok(self):
        self.assertEqual(self.verify(self.good()), [])

    def test_onchain_data_differs(self):
        self.assertTrue(self.verify(b"x" + self.good()[1:]))

    def test_rewritten_block_detected(self):
        Block.objects.filter(pk=self.head.pk).update(block_hash="e" * 64)
        self.assertTrue(self.verify(self.good()))
