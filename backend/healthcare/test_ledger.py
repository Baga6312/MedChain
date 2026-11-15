from django.test import SimpleTestCase

from . import ledger


class LedgerTests(SimpleTestCase):
    def test_merkle_deterministic_and_order_sensitive(self):
        a, b = ledger.sha256_hex(b"a"), ledger.sha256_hex(b"b")
        self.assertEqual(ledger.merkle_root([a, b]), ledger.merkle_root([a, b]))
        self.assertNotEqual(ledger.merkle_root([a, b]), ledger.merkle_root([b, a]))

    def test_mine_meets_difficulty_and_verifies(self):
        kw = dict(chain_id="1:user", index=1, prev_hash=ledger.GENESIS_PREV_HASH,
                  merkle_root=ledger.sha256_hex(b"tx"), timestamp=1700000000)
        nonce, h = ledger.mine(**kw, diff=2)
        self.assertTrue(h.startswith("00"))
        self.assertEqual(h, ledger.header_hash(**kw, nonce=nonce))

    def test_tamper_changes_hash(self):
        kw = dict(chain_id="1:user", index=1, prev_hash="0" * 64,
                  merkle_root="a" * 64, timestamp=1, nonce=5)
        original = ledger.header_hash(**kw)
        for field, value in [("index", 2), ("prev_hash", "1" * 64), ("merkle_root", "b" * 64),
                             ("timestamp", 2), ("nonce", 6), ("chain_id", "1:doctor")]:
            self.assertNotEqual(original, ledger.header_hash(**{**kw, field: value}))