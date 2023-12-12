# !/usr/bin/env python
# coding: utf-8
import codecs
import json
from http.client import IncompleteRead

import requests
import urllib3
import urllib.request as urlrq
import ssl
import pandas as pd
import csv
import json
import re
import subprocess
import time
from typing import Callable, Any, Iterable
import requests

from core.common.utils import ExcelBase

BASE_DOMAIN = "https://scan.etnd.pro/api"
HOST = "scan.etnd.pro"


def shorten(address: str) -> str:
    return address[:5] + "..." + address[len(address) - 5: -1]


class Excel(ExcelBase):
    def __init__(self):
        self.datastruct = {
            "blockNumber": [],
            "blockHash": [],
            "contractAddress": [],
            "from": [],
            "to": [],
            "hash": [],
            "input": [],
            "isError": [],
            "nonce": [],
            "timeStamp": [],
            "transactionIndex": [],
            "txreceipt_status": [],
            "value": [],
        }
        self.tokenset = {
            "blockNumber": [],
            "blockHash": [],
            "contractAddress": [],
            "hash": [],
            "from": [],
            "to": [],
            "timeStamp": [],
            "value": [],
        }
        self.labels = []
        self.r = 0
        self.df_row_first_transactions = None

    def label_up(self):
        self.r += 1
        self.labels.append(self.r)

    def insertBlockJson(self, oc: dict):
        self.datastruct["blockNumber"].append(oc["blockNumber"])
        self.datastruct["blockHash"].append(oc["blockHash"])
        self.datastruct["contractAddress"].append(oc["contractAddress"])
        self.datastruct["from"].append(oc["from"])
        self.datastruct["to"].append(oc["to"])
        self.datastruct["hash"].append(oc["hash"])
        self.datastruct["input"].append(oc["input"])
        self.datastruct["isError"].append(oc["isError"])
        self.datastruct["nonce"].append(oc["nonce"])
        self.datastruct["timeStamp"].append(oc["timeStamp"])
        self.datastruct["transactionIndex"].append(oc["transactionIndex"])
        self.datastruct["txreceipt_status"].append(oc["txreceipt_status"])
        self.datastruct["value"].append(oc["value"])
        # self.label_up()

    def insertTokenTx(self, oc: dict):
        if oc["contractAddress"] != "":
            contract = oc["contractAddress"]
            tokenName = ""
            self.datastruct["blockNumber"].append(oc["blockNumber"])
            self.datastruct["blockHash"].append(oc["blockHash"])
            self.datastruct["from"].append(oc["from"])
            self.datastruct["to"].append(oc["to"])
            self.datastruct["hash"].append(oc["hash"])
            self.datastruct["timeStamp"].append(oc["timeStamp"])
            self.datastruct["value"].append(oc["value"])
            self.datastruct["token"].append(tokenName)

    def writeBlock(self, ep: int, title_address: str):
        df = pd.DataFrame(data=self.datastruct)
        title_address = shorten(title_address)
        df.to_excel(f"data{ep}.xlsx", sheet_name=f"rel-{title_address}")

    def readFileRes(self, metadata: dict):
        if len(metadata["result"]) > 0:
            print("ok got some listing here")
            for n in metadata["result"]:
                self.insertBlockJson(n)

    def readTokenTx(self, metadata: dict):
        if len(metadata["result"]) > 0:
            print("ok got some listing here")
            for n in metadata["result"]:
                self.insertTokenTx(n)

    def df_row_first_transactions(self, dfrow: dict, header: list):

        date = dfrow["交易时间"]
        add_from = dfrow["转出地址"]
        to_from = dfrow["转入地址"]
        amount_liz = int(dfrow["交易额（LIZ)"])
        rmb_sum = int(dfrow["人民币价格"])
        hash = dfrow["hash"]
        _color = "blue"

        self.handle_node(to_from, amount_liz, rmb_sum, self.get_block_height(hash))

        rmb_sum = f"{rmb_sum:,.2f} rmb"
        amount_liz = f"{amount_liz:,.2f} liz"
        _label = f"{amount_liz}#{date}#TX:{hash}"
        _label = _label.replace("#", "\n")

        self.dot.edge(
            tail_name=add_from,
            head_name=to_from,
            color=_color,
            label=_label,
            labeldistance='1.2',
            labelangle='60',
        )

        self.edges += 1

    def setReader(self, pointer_reader: Callable):
        self.df_row_first_transactions = pointer_reader

    def readFile(self, file_path_excel: str, header: list, sheet_label: str):
        if self.df_row_first_transactions is None:
            print("the reader function is not set, use setReader to define a function.")
            return
        self.setExcelFile(file_path_excel)
        try:
            _df = self._readDF(file_path_excel, sheet_label, header)
            for i, row in _df.iterrows():
                self.df_row_first_transactions(row, header)
        except FileNotFoundError:
            print("file not found.")

        return self


class ReqDatBlockScout:
    def __init__(self):
        self.g = ""
        self.file = "tmp_req.json"
        self.result = dict()

    def loadResAsJson(self):
        try:
            self.result = json.load(codecs.open(self.file, 'r', 'utf-8-sig'))
        except Exception as e:
            print("Problems from loading items from the file: ", e)

    def loadResAsDoc(self):
        try:
            writer_as = codecs.open(self.file, 'r', 'utf-8-sig')
            self.result = writer_as.read()
        except Exception as e:
            print("Problems from loading items from the file: ", e)

    def setBase(self, endpoint: str):
        self.base_endpoint = endpoint
        print(f"set endpoint api path: {endpoint}")

    def getResult(self) -> dict:
        return self.result

    def getHashListByAddress(self, from_account_address: str) -> dict:
        q = f"{self.base_endpoint}?module=account&action=txlist&address={from_account_address}"
        self.pull_block_history(q)
        return self.getResult()

    def getBalance(self, address_owner: str) -> dict:
        q = f"{self.base_endpoint}?module=account&action=balance&address={address_owner}"
        self.pull_block_history(q)
        return self.getResult()

    def getHashTx(self, tx_hash: str) -> dict:
        q = f"{self.base_endpoint}?module=transaction&action=gettxinfo&txhash={tx_hash}"
        print(f"=>: {q}")
        self.req_simple(q)
        return self.getResult()

    def getHashTxAsDoc(self, tx_hash: str) -> str:
        q = f"{self.base_endpoint}?module=transaction&action=gettxinfo&txhash={tx_hash}"
        print(f"=>: {q}")
        self.req_simple(q)
        self.loadResAsDoc()
        return self.result

    def req_simple(self, q: str):
        with requests.get(q, stream=True) as r:
            r.raise_for_status()
            with open(self.file, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)

        self.loadResAsJson()

    def pull_block_history(self, q: str):
        cert_reqs = ssl.CERT_NONE
        urllib3.disable_warnings()
        host = self.base_endpoint.replace("/api", "").replace("https://", "")
        c = urllib3.HTTPSConnectionPool(
            host=host,
            timeout=65,
            maxsize=10,
            block=True,
            cert_reqs=cert_reqs,
            assert_hostname=False
        )

        u = c.request('GET', q, decode_content=False, preload_content=False)

        file_size = u.headers["Content-Length"]
        print(f"Downloading: {self.file} Bytes: {file_size}")

        file_size_dl = 0
        block_sz = 4 * 1024

        with open(self.file, 'wb') as f:
            if int(file_size) > block_sz:
                for chunk in u.stream(block_sz):
                    file_size_dl += len(chunk)
                    status = r"%10d  [%3.2f%%]" % (file_size_dl, file_size_dl * 100. / float(file_size))
                    status = status + chr(8) * (len(status) + 1)
                    f.write(chunk)
                    print(status, end="\r")
                u.release_conn()
                f.close()
                print("next ready lines")
            else:
                print("not supported.")

        self.loadResAsJson()


def getTxDetail(addressHash: str):
    u = ReqDatBlockScout()
    q = f"{BASE_DOMAIN}?module=account&action=txlist&address={addressHash}"
    print(q)
    u.pull_block_history(q)
    ex = Excel()
    metadata = u.getResult()
    ex.readFileRes(metadata)
    ex.writeBlock(1, addressHash)
