import hashlib

from django.conf import settings
from web3 import Web3
from web3.exceptions import TransactionNotFound

from ..models import Anchor, Block

PREFIX = b"MC1"


def _w3():
    return Web3(Web3.HTTPProvider(settings.CHAIN_RPC_URL, request_kwargs={"timeout": 15}))


def anchor_data(chain_id, block_hash):
    return PREFIX + hashlib.sha256(chain_id.encode()).digest() + bytes.fromhex(block_hash)


def anchor_head(episode, chain):
    head = Block.objects.filter(treatment_episode=episode, chain=chain).order_by("-index").first()
    if head is None or head.index == 0:
        return None  # nothing beyond genesis
    if Anchor.objects.filter(treatment_episode=episode, chain=chain, block_hash=head.block_hash).exists():
        return None  # already anchored

    w3 = _w3()
    acct = w3.eth.account.from_key(settings.ANCHOR_PRIVATE_KEY)
    tx = {
        "from": acct.address,
        "to": acct.address,
        "value": 0,
        "data": anchor_data(head.chain_id, head.block_hash),
        "nonce": w3.eth.get_transaction_count(acct.address),
        "gasPrice": w3.eth.gas_price,
        "chainId": w3.eth.chain_id,
    }
    tx["gas"] = w3.eth.estimate_gas(tx)
    signed = acct.sign_transaction(tx)
    raw = getattr(signed, "raw_transaction", None) or signed.rawTransaction
    tx_hash = w3.eth.send_raw_transaction(raw)
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=30)
    return Anchor.objects.create(
        treatment_episode=episode, chain=chain, block_index=head.index,
        block_hash=head.block_hash, tx_hash=w3.to_hex(tx_hash), eth_block=receipt["blockNumber"],
    )


def verify_anchors(episode):
    errors = []
    w3 = _w3()
    for a in Anchor.objects.filter(treatment_episode=episode):
        blk = Block.objects.filter(treatment_episode=episode, chain=a.chain, index=a.block_index).first()
        if blk is None or blk.block_hash != a.block_hash:
            errors.append(f"{a.chain}: block {a.block_index} differs from what was anchored")
            continue
        try:
            onchain = bytes(w3.eth.get_transaction(a.tx_hash)["input"])
        except TransactionNotFound:
            errors.append(f"{a.chain}: anchor tx {a.tx_hash[:12]} not found on the blockchain")
            continue
        if onchain != anchor_data(blk.chain_id, blk.block_hash):
            errors.append(f"{a.chain}: on-chain data does not match block {a.block_index}")
    return errors