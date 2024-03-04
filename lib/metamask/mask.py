# !/usr/bin/env python
# coding: utf-8
import os
import random
import time
from typing import Tuple

import web3
# Press ⌃R to execute it or replace it with your code.
# Press Double ⇧ to search everywhere for classes, files, tool windows, actions, and settings.
from hdwallet import BIP44HDWallet
from hdwallet.cryptocurrencies import EthereumMainnet
from hdwallet.symbols import ETH as SYMBOL
from web3.gas_strategies.time_based import medium_gas_price_strategy
from web3 import Web3, middleware

from lib.metamask.bolt import read_file_lines, read_file_total_lines, read_file_at_line


class NoReminderNote(Exception):
    ...


NOTE_MEM = "funny capital shop hockey twelve asset abstract popular ankle reopen crawl civil"
DATAPATH_BASE = ""
EVM_RPC = ""


class EthereumBaseWallet:
    hd_wallet: BIP44HDWallet
    address_list: list[str]
    by_file: bool
    is_key_file: bool
    __addr: str
    pk: str
    file_name: str
    reminder: str
    at_index: int
    account_limit: int
    w: Web3

    @property
    def hdd_index(self) -> int:
        return self.at_index

    @property
    def address(self) -> str:
        if isinstance(self.__addr, str):
            return self.__addr
        return ""

    def fromAddressFile(self, file_name: str = "xie.txt"):
        path = os.path.join(DATAPATH_BASE, file_name)
        self.by_file = True
        self.is_key_file = False
        self.file_name = path
        self.address_list = read_file_lines(path)
        self.account_limit = read_file_total_lines(path)
        return self

    def fromKeysFile(self, file_name: str = "ordz.02.txt"):
        path = os.path.join(DATAPATH_BASE, file_name)
        self.file_name = path
        self.by_file = True
        self.is_key_file = True
        note_list = read_file_lines(path)
        self.address_list = self._address_in_list_by_file(note_list)
        self.account_limit = read_file_total_lines(path)
        return self

    def fromMnmenoicPhrase(self, content_text: str):
        self.reminder = content_text
        self.by_file = False
        self.file_name = ""
        short = f"{content_text[:8]}...{content_text[len(content_text) - 8:]}"
        print(f"wallet is now using HD with one single phrase {short}")
        return self

    def ercwallet_init__uni(self):
        self.reminder = "..."
        self.__addr = ""
        self.by_file = False
        self.is_key_file = False
        self.file_name = ""
        self.address_list = []
        self.account_limit = 0
        self.at_index = 0
        self.w = Web3(Web3.HTTPProvider(EVM_RPC))
        self.w.eth.set_gas_price_strategy(medium_gas_price_strategy)
        self.w.middleware_onion.add(middleware.time_based_cache_middleware)
        self.w.middleware_onion.add(middleware.latest_block_based_cache_middleware)
        self.w.middleware_onion.add(middleware.simple_cache_middleware)

    def _address_in_list_by_file(self, notes: list) -> list:
        f = []
        for note in notes:
            (addr, _) = self._erc_address(note, 0)
            f.append(addr)
        return f

    def fromWalletIndex(self, n: int):
        if self.by_file is False:
            if self.reminder == "...":
                raise NoReminderNote()
            self.at_index = n
            (address, _private) = self._erc_address(self.reminder, n)
            self.__addr = address
            self.pk = _private
        else:
            if self.is_key_file is True:
                k = n % self.account_limit
                self.at_index = k
                self.reminder = read_file_at_line(self.file_name, k)
                (address, _private) = self._erc_address(self.reminder, 0)
                self.__addr = address
                self.pk = _private
            else:
                k = n % self.account_limit
                self.at_index = k
                self.reminder = "..."
                self.__addr = read_file_at_line(self.file_name, k)
                self.pk = ""

    def _erc_address(self, mnemonic: str, at_index: int = 0) -> Tuple[str, str]:
        try:
            bwl: BIP44HDWallet = BIP44HDWallet(cryptocurrency=EthereumMainnet, symbol=SYMBOL)
            bwl.from_mnemonic(mnemonic=mnemonic, language="english", passphrase=None)
            bwl.from_index(at_index)
            erc_address = bwl.address()
            main_pk = bwl.private_key()
            self.hd_wallet = bwl
            return (erc_address, main_pk)
        except ValueError as e:
            print("error on taproot creation")
            return ("", "")

    def is_ready(self) -> bool:
        return self.pk != ""

    def from_private_key(self, k: str):
        PA = self.w.eth.account.from_key(k)
        self.pk = k
        self.__addr = PA.address

    def from_new_random_private_key(self):
        n = random.randrange(100, 10000)
        wallet: BIP44HDWallet = BIP44HDWallet(cryptocurrency=EthereumMainnet, symbol=SYMBOL)
        wallet.from_mnemonic(mnemonic=NOTE_MEM, language="english", passphrase=None)
        wallet.from_index(n)
        ok_private_key = wallet.private_key()
        print(f"use HD index {n} - private key {ok_private_key}")
        self.from_private_key(ok_private_key)

    def in_asset(self, detect_balance: float) -> bool:
        address = Web3.to_checksum_address(self.address)
        bal = self.w.eth.get_balance(address)
        save = detect_balance * 10 ** 18
        return bal > save

    def sweep_asset(self, nft: str, nft_id: int, next_address: str):
        # sweep NFT
        safe_transfer = "0x42842e0e"
        from_address = self.input_addr_code(self.address)
        to_address = self.input_addr_code(next_address)
        token_id = self.input_integer_code(nft_id)
        hex_data = f"{safe_transfer}{from_address}{to_address}{token_id}"
        self._transaction(nft, hex_data)
        # sweep balance

    def sweep_balance(self, small_balance: float, next_address: str):
        gas = 210000
        gas_price = self.w.eth.gas_price
        # gas_price = 10008
        address = Web3.to_checksum_address(self.address)
        bal = self.w.eth.get_balance(address)
        save = small_balance * 10 ** 18
        # balance_after_fee = bal
        # balance_after_fee = bal - int(save)
        # balance_after_fee = bal - int(gas) * gas_price
        balance_after_fee = bal - int(save)
        # print(f"save wei {int(save)}")
        # print(f"balance save {bal} - {int(save)} = {balance_after_fee}, gas:{gas}, gas price:{gas_price}")
        # print(f"balance save {balance_after_fee}, gas:{gas}, gas price:{gas_price}")
        # print(f"gas * price + value = {gas} x {gas_price} + {balance_after_fee} = {bal}")
        if balance_after_fee <= 0:
            print(f"Please add fund to the account {self.address} in order to sweep balance")
            return

        # next_address = Web3.to_checksum_address(next_address)
        # nonce = self.w.eth.get_transaction_count(address)
        nonce = self.w.eth.get_transaction_count(address, 'pending')

        transaction = {
            'nonce': nonce,
            "to": next_address,
            "from": self.address,
            "value": balance_after_fee,
            'gasPrice': gas_price,
            "gas": gas
        }
        signed_txn = self.w.eth.account.sign_transaction(transaction, self.pk)
        tx_hash = self.w.eth.send_raw_transaction(signed_txn.rawTransaction)
        print(f"Transaction Hash: {self.w.to_hex(tx_hash)}")
        ok = self.w.eth.wait_for_transaction_receipt(tx_hash, 5)
        print(f"Transaction Confirmed: {ok}")

    def input_integer_code(self, id: int):
        return hex(id)[2:].zfill(64)

    def input_addr_code(self, address: str):
        return address.lower()[2:].zfill(64)

    def _transaction(self, contract, hex_data):
        try:
            self._tx(contract, hex_data)
        except web3.exceptions.TimeExhausted as timeout:
            print("time out after 10s its okay. lets it be..", timeout)
        except ValueError as e:
            if "nonce too low" in str(e):
                print("retry... nonce too low")
                time.sleep(3)
                self._tx(contract, hex_data)
            else:
                print(e)
                exit(0)

    def _tx(self, contract, hex_data):
        address = Web3.to_checksum_address(self.address)
        self.nonce = self.w.eth.get_transaction_count(address)
        transaction = {
            'nonce': self.nonce,
            'to': contract,
            'value': 0,  # Amount of ETH to send (in Wei)
            'gas': 2000000,  # Adjust gas limit as needed
            'gasPrice': self.w.eth.gas_price,
            'data': hex_data,
            'chainId': self.w.eth.chain_id
        }
        signed_txn = self.w.eth.account.sign_transaction(transaction, self.pk)
        tx_hash = self.w.eth.send_raw_transaction(signed_txn.rawTransaction)
        # print(f"Transaction Hash: {self.w.to_hex(tx_hash)}")
        ok = self.w.eth.wait_for_transaction_receipt(tx_hash, 10)
        print(f"Transaction Confirmed: {ok}")
