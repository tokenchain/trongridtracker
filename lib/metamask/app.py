# ----
# !/usr/bin/env python
# coding: utf-8

from typing import Tuple
# Press ⌃R to execute it or replace it with your code.
# Press Double ⇧ to search everywhere for classes, files, tool windows, actions, and settings.
from eth_account.messages import SignableMessage, encode_defunct
from .mask import EthereumBaseWallet


# ----

class AppMetamask(EthereumBaseWallet):
    def __init__(self):
        self.ercwallet_init__uni()

    def action_collect_treasure(self, adventure_contract: str):
        if self.pk == "":
            print("no private key is setup")
            return ""
        hex_data = "0x9b7d30dd0000000000000000000000000000000000000000000000000000000000000001"
        self._transaction(adventure_contract, hex_data)

    def action_adventure(self, adventure_contract: str):
        hex_data = "0x9b7d30dd0000000000000000000000000000000000000000000000000000000000000002"
        self._transaction(adventure_contract, hex_data)

    def sign_message_test5(self, msg: str = "....") -> Tuple[str, dict]:
        ss: SignableMessage = encode_defunct(text=msg)
        signature = self.w.eth.account.sign_message(ss, self.pk)
        signature_text = signature.signature.hex()
        eth_verification = {
            "signature": signature_text,
            "wallet_address": self.address
        }
        print(signature)
        print("double check on @ https://app.mycrypto.com/verify-message")
        print(eth_verification)
        return signature_text, eth_verification
