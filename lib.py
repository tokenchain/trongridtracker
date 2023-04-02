#!/usr/bin/env python
# coding: utf-8
import asyncio
import csv
import json
import os
import signal
import time
from datetime import datetime
from typing import Union

import requests

# import sys
# the mock-0.3.1 dir contains testcase.py, testutils.py & mock.py
# sys.path.append('/Users/hesdx/Documents/piplines/tron-tool-py/tronpytool')
from urllib3.exceptions import ReadTimeoutError

NETWORK = "mainnet"
ROOT = os.path.join(os.path.dirname(__file__))
statement = 'End : {}, IO File {}'
file_format = 'report_{}.txt'
file_analysis = 'analysis_{}.json'
file_hold_format = 'rehold_{}.txt'
filelog_format = 'log_{}.txt'
statement_process = 'Processed page: {} {}, {}'
statement_log = 'Log {}, FP: {}\n'
statement_sum = '\nReport for address {}\nTotal outgoing USDT: {} / count: {}\nTotal incoming USDT: {} / count: {}\nNet {}'
request_1_token = "https://api.trongrid.io/v1/accounts/{}/transactions/trc20?limit={}&contract_address={}"
api_holders = "https://apilist.tronscan.org/api/tokenholders?sort=-balance&limit={}&start={}&count=true&address={}"

help = """
Please note that the json file {FILENAME} gives the following explaination:
address:  the address transfered to
bal: the total amount to be transfered, positive is the collection address, negative is the upper level collection.
hit: the amount of transactions that is associated to this address
"""


class GracefulInterruptHandler(object):

    def __init__(self, sig=signal.SIGINT):
        self.sig = sig

    def __enter__(self):
        self.interrupted = False
        self.released = False

        self.original_handler = signal.getsignal(self.sig)

        def handler(signum, frame):
            self.release()
            self.interrupted = True

        try:
            signal.signal(self.sig, handler)
        except ValueError:
            pass

        return self

    def __exit__(self, type, value, tb):
        self.release()

    def release(self):
        if self.released:
            return False
        try:
            signal.signal(self.sig, self.original_handler)
        except ValueError:
            pass

        self.released = True
        return True


def GetTOKEN():
    return ""


def requestTimeStamp():
    print("URL request : %s" % time.ctime())


class TronscanAPI:
    """Deploy wrap contract in the deployment"""

    def __init__(self):
        self.outgoing = 0
        self.outcount = 0
        self.incoming = 0
        self.incount = 0
        self.records = 0
        self.outputfile = "report.txt"
        self.next_link = ""
        self.fingerprint = ""
        self.logfile = ""
        self._m_address = ""
        self._m_balance = 0
        self.wallet_address = ""

    @staticmethod
    def writeFile(content, filename):
        fo = open(filename, "w")
        fo.write(content)
        fo.close()
        print(statement.format(time.ctime(), filename))

    @staticmethod
    def getTRC20Link(link: str):
        payload = {}
        headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:79.0) Gecko/20100101 Firefox/79.0',
                   'Accept': 'application/json, text/javascript, */*; q=0.01',
                   'Cookie': GetTOKEN(), 'Content-Type': 'application/json', 'Connection': 'keep-alive',
                   'Accept-Language': 'en-US,en;q=0.5', 'X-Requested-With': 'XMLHttpRequest'}

        requestTimeStamp()
        response = requests.request("GET", link, headers=headers, data=payload)
        if response.status_code == 200:
            try:
                # TronscanAPI.writeFile(response.text, filename)
                data = response.json()
                return data
            except UnicodeEncodeError as e:
                print("please login first; %s;" % e)
                return 1
            return 0
        else:
            print(response.content)
            print("connection problem occured")
            return 2

    @staticmethod
    def getTRC20(account: str, trc20_address: str, limit: int):
        payload = {}
        headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:79.0) Gecko/20100101 Firefox/79.0',
                   'Accept': 'application/json, text/javascript, */*; q=0.01',
                   'Cookie': GetTOKEN(), 'Content-Type': 'application/json', 'Connection': 'keep-alive',
                   'Accept-Language': 'en-US,en;q=0.5', 'X-Requested-With': 'XMLHttpRequest'}

        contract_get_api = request_1_token.format(account, limit, trc20_address)

        requestTimeStamp()
        response = requests.request("GET", contract_get_api, headers=headers, data=payload)
        if response.status_code == 200:
            try:
                return response.json()
            except UnicodeEncodeError as e:
                print("please login first; %s;" % e)
                return 1
            return 0
        else:
            print(response.content)
            print("connection problem occured")
            return 2

    @staticmethod
    def getHoldersAt(contract, start, limit):
        payload = {}
        headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:79.0) Gecko/20100101 Firefox/79.0',
                   'Accept': 'application/json, text/javascript, */*; q=0.01',
                   'Cookie': GetTOKEN(), 'Content-Type': 'application/json', 'Connection': 'keep-alive',
                   'Accept-Language': 'en-US,en;q=0.5', 'X-Requested-With': 'XMLHttpRequest'}
        contract_api = api_holders.format(limit, start, contract)

        requestTimeStamp()
        response = requests.request("GET", contract_api, headers=headers, data=payload)
        if response.status_code == 200:
            try:
                return response.json()
            except UnicodeEncodeError as e:
                print("please login first; %s;" % e)
                return 1
            return 0
        else:
            # print(response.status_code)
            return 2

    @staticmethod
    def byNext(url: str) -> Union[dict, int]:
        headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:79.0) Gecko/20100101 Firefox/79.0',
                   'Accept': 'application/json, text/javascript, */*; q=0.01',
                   'Cookie': GetTOKEN(), 'Content-Type': 'application/json', 'Connection': 'keep-alive',
                   'Accept-Language': 'en-US,en;q=0.5', 'X-Requested-With': 'XMLHttpRequest'}
        payload = {}
        time.sleep(2)
        response = requests.request("GET", url, headers=headers, data=payload)
        requestTimeStamp()
        if response.status_code == 200:
            try:
                return response.json()
            except UnicodeEncodeError as e:
                print("please login first; %s;" % e)
                return 1
            return 0
        else:
            return 2

    def checkTransaction(self, _id):
        print("hash id is {}".format(_id))

    def byCVS(self):
        with open('export.csv', newline='') as csvfile:
            spamreader = csv.reader(csvfile, delimiter=',', quotechar='|')
            for row in spamreader:
                hash = row[0]
                self.checkTransaction(hash)

    def getNextLoop(self, json: dict) -> Union[bool, dict]:
        self.next_link = None
        if "meta" in json:
            if "fingerprint" in json["meta"]:
                self.fingerprint = json["meta"]["fingerprint"]
            if "links" in json["meta"]:
                if "next" in json["meta"]["links"]:
                    self.next_link = json["meta"]["links"]["next"]

        if self.next_link is None:
            return False

        if self.fingerprint is not None and self.next_link is not None:
            response = TronscanAPI.byNext(self.next_link)
            if response == 1 or response == 0 or response == 2:
                return False
            else:
                return response

        return False

    def handleMetadata(self, data: dict) -> None:
        self.fingerprint = ""
        if "meta" in data:
            if "links" in data["meta"]:
                if "next" in data["meta"]["links"]:
                    self.next_link = data["meta"]["links"]["next"]
            if "fingerprint" in data["meta"]:
                self.fingerprint = data["meta"]["fingerprint"]
            self.recordLog()
        else:
            self.recordLogError("there is no such data -- {}".format(data))

    def readTrc20Data(self, json: dict):
        if "data" in json:
            response = TronscanAPI.byNext(json["data"])

    def Calc(self, json):
        if "data" in json:

            for row in json["data"]:
                if row["from"] == self.wallet_address:
                    self.outgoing = self.outgoing + int(row["value"])
                    self.outcount = self.outcount + 1

                if row["to"] == self.wallet_address:
                    self.incoming = self.incoming + int(row["value"])
                    self.incount = self.incount + 1

                self.records = self.records + 1
                self.recordTransactionLine(row)

        return False

    def recordTransactionLine(self, row):
        # readable = datetime.datetime.fromtimestamp(row["block_timestamp"]).isoformat()
        ts = int(row["block_timestamp"]) / 1000
        readable = datetime.utcfromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
        data = [str(self.byValue(row["value"])), row["from"], row["to"], "USDT", row["transaction_id"], readable, "\n"]
        self.AppendLineTransaction(",".join(data))

    def addressRecordLog(self):
        line = [self._m_address, str(self._m_balance), "\n"]
        self.AppendLineTransaction(",".join(line))

    def recordLog(self):
        self.AppendLineLog(statement_log.format(self.records, self.fingerprint))

    def recordLogError(self, error: str):
        self.AppendLineLog(error)

    def EndLine(self):
        value_out = self.byValuei(self.outgoing)
        value_in = self.byValuei(self.incoming)
        net = value_in - value_out

        self.AppendLineTransaction(
            statement_sum.format(self.wallet_address, value_out, self.outcount, value_in, self.incount, net)
        )

    def byValuei(self, amount: int) -> float:
        return amount / 1000000

    def byValue(self, amount: str) -> float:
        return int(amount) / 1000000

    def looper(self, address: str, contract: str):
        TronscanAPI.writeFile("", self.outputfile)
        json = self.getTRC20(address, contract, 100)
        if json == 2:
            print("retry in 20 seconds")
            time.sleep(20)
            self.looper(address, contract)

        result = dict()
        p = 0
        while True:
            with GracefulInterruptHandler() as hp:
                self.Calc(json)
                try:
                    result = self.getNextLoop(json)

                except TypeError as te:
                    print("☯︎ ", te)
                    continue

                except requests.exceptions.Timeout as eg:
                    # Maybe set up for a retry, or continue in a retry loop
                    print("☯︎ request time out", eg)
                    continue

                except requests.exceptions.ConnectionError as ef:
                    # Maybe set up for a retry, or continue in a retry loop
                    print("☯︎ request time out", ef)
                    continue

                except requests.exceptions.TooManyRedirects as ep:
                    # Tell the user their URL was bad and try a different one
                    print("☯︎ too many requests now", ep)
                    continue

                except requests.exceptions.HTTPError as eh:
                    print("☯︎ http error is now", eh)
                    continue

                except ReadTimeoutError as h:
                    print("☯︎ time out", h)
                    continue

                except requests.exceptions.RequestException as ej:
                    # catastrophic error. bail.
                    print("☯︎ nothing but try again later", ej)
                    continue

                if not result:
                    print("finished..")
                    self.EndLine()
                    break

                if isinstance(result, dict):
                    json = result

                p += 1

                print('\n' + statement_process.format(p, self.records, self.next_link))

                if hp.interrupted:
                    raise TypeError("Program exit")

    def AppendLineLog(self, content: str):
        file_object = open(self.logfile, 'a')
        file_object.write(content)
        file_object.close()

    def AppendLineTransaction(self, content: str):
        file_object = open(self.outputfile, 'a')
        file_object.write(content)
        file_object.close()


class USDTApp(TronscanAPI):

    def __init__(self):
        super().__init__()

    def _resetZero(self):
        self.outgoing = 0
        self.outcount = 0
        self.incoming = 0
        self.incount = 0
        self.records = 0

    def CollectionTransactionFromTronForUSDD(self, holder_address: str) -> None:
        self.wallet_address = holder_address
        self._resetZero()
        self.outputfile = file_format.format(holder_address)
        self.logfile = filelog_format.format(holder_address)
        self.looper(holder_address, "TPYmHEhy5n8TCEfYGqW2rPxsghSfzghPDn")

    def CollectionTransactionFromTronForBUSD(self, holder_address: str) -> None:
        self.wallet_address = holder_address
        self._resetZero()
        self.outputfile = file_format.format(holder_address)
        self.logfile = filelog_format.format(holder_address)
        self.looper(holder_address, "TMz2SWatiAtZVVcH2ebpsbVtYwUPT9EdjH")

    def CollectionTransactionFromTronForTUSD(self, holder_address: str) -> None:
        self.wallet_address = holder_address
        self._resetZero()
        self.outputfile = file_format.format(holder_address)
        self.logfile = filelog_format.format(holder_address)
        self.looper(holder_address, "TUpMhErZL2fhh4sVNULAbNKLokS4GjC1F4")

    def CollectionTransactionFromTronForUSDC(self, holder_address: str) -> None:
        self.wallet_address = holder_address
        self._resetZero()
        self.outputfile = file_format.format(holder_address)
        self.logfile = filelog_format.format(holder_address)
        self.looper(holder_address, "TEkxiTehnzSmSe2XqrBj4w32RUN966rdz8")

    def CollectionTransactionFromTronForUSDT(self, holder_address: str) -> None:
        self.wallet_address = holder_address
        self._resetZero()
        self.outputfile = file_format.format(holder_address)
        self.logfile = filelog_format.format(holder_address)
        self.looper(holder_address, "TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t")


class CustomToken(TronscanAPI):

    def handlemeHolder(self, data: dict):
        if "data" in data:
            for row in data["data"]:
                self._m_address = row["address"]
                self._m_balance = row["balance"]
                self.addressRecordLog()

    def looperHolderAddress(self, contract: str, deci: int):
        start = 0
        limit = 50

        result = dict()
        while True:
            with GracefulInterruptHandler() as hp:
                result = self.getHoldersAt(contract, start, limit)
                if result == 2:
                    print("retry in 20 seconds")
                    time.sleep(20)
                    self.looperHolderAddress(contract, deci)

                if not result:
                    print("finished..")
                    self.EndLine()
                    break

                if isinstance(result, dict):
                    self.handlemeHolder(result)
                    self.records = self.records + 1

                start = start + limit
                if hp.interrupted:
                    raise TypeError("Program exit")

    def CheckTokenHolderAddress(self, token_address, decimal):
        self.wallet_address = ""
        contract = token_address
        self.records = 0
        self.outputfile = file_hold_format.format(token_address)
        self.logfile = filelog_format.format(token_address)
        self.looperHolderAddress(contract, decimal)


class Analysis:
    def __init__(self):
        self.hodlr = []
        self.booklegerlist = []
        self.bookleger = dict()
        self.logfile = ""
        self.outfile = ""
        self.line_scan = 0
        self._indent = 4
        self._encoding = "utf-8"
        self.tags = {}
        self.tagPre()

    def tagPre(self):
        with open('tagged.json', newline='') as f:
            tags = json.loads(f.read())
            self.tags = tags

    def tagging(self, address: str) -> str:
        if address in self.tags:
            return self.tags[address]
        return ""

    def start(self, holder_address: str):
        self.logfile = file_format.format(holder_address)
        self.outfile = file_analysis.format(holder_address)
        file1 = open(self.logfile, 'r')
        _lines = file1.readlines()
        _sum = len(_lines)
        print(f"total lines should be {_sum}")
        # Strips the newline character

        for line in _lines:
            self.line_scan += 1
            # print("Line{}: {} \n".format(self.line_scan, line.strip()), end="\r")
            try:
                self.processLine(line)
            except IndexError:
                pass

            if self.line_scan == _sum:
                self.ender()

    def ender(self):
        self.hodlr = []
        # self book ledger list book yes
        for k, v in self.bookleger.items():
            if k not in self.hodlr:
                self.hodlr.append(k)
                self.booklegerlist.append({
                    "address": k,
                    "bal": v["bal"],
                    "hit": v["hit"],
                    "mark": self.tagging(k)
                })

        self.booklegerlist = sorted(self.booklegerlist, key=lambda x: -x["bal"])

        with open(self.outfile, 'w') as f:
            json_str = json.dumps({
                "ranks": self.booklegerlist
            }, indent=self._indent)
            # data = jsonStr.encode(self._encoding)
            f.write(json_str)
            f.close()

        print(help.format(FILENAME=self.outfile))

    def processLine(self, line: str):
        p = line.strip().split(",")
        # from
        fromadd = p[1]
        # to
        toadd = p[2]
        # value
        val = p[0]

        if fromadd not in self.hodlr:
            self.hodlr.append(fromadd)

        if toadd not in self.hodlr:
            self.hodlr.append(toadd)

        if fromadd not in self.bookleger:
            self.bookleger[fromadd] = {
                "bal": 0,
                "hit": 0
            }

        if toadd not in self.bookleger:
            self.bookleger[toadd] = {
                "bal": 0,
                "hit": 0
            }

        self.bookleger[fromadd]["bal"] -= float(val)
        self.bookleger[fromadd]["hit"] += 1
        self.bookleger[toadd]["bal"] += float(val)
        self.bookleger[toadd]["hit"] += 1


import signal
import threading
import pysigset


class SubLayerAnalysis:
    def __init__(self):
        self.booklegerlist = []
        self.jsonfile = ""
        self.holdself = " "
        self.scan_top = 4
        self.scan_at = 0
        self.scan_task = {}

    def find_task(self):
        n = 0
        while len(self.scan_task.items()) > 0:
            for k, t in self.scan_task.items():
                if t.done():
                    del self.scan_task[k]
                    print(f"processed address {k} from the listed")
            print(f"wait - {n}")
            n += 1
            time.sleep(3)

        print("sub layer is not done")

    def start(self, address: str):
        asyncio.run(self.corstart(address))

    async def corstart(self, holder_address: str):
        self.holdself = holder_address
        self.jsonfile = file_analysis.format(holder_address)
        with open(self.jsonfile, newline='') as f:
            self.booklegerlist = json.loads(f.read())
            if "ranks" in self.booklegerlist:
                self.booklegerlist = self.booklegerlist["ranks"]

        if len(self.booklegerlist) == 0:
            return

        for ob in self.booklegerlist:
            print(ob)
            if int(ob["bal"]) > 0 and ob["address"] != self.holdself and self.scan_at < self.scan_top:
                address = ob["address"]
                print(f"on task for scanning address {address}")
                # loop = asyncio.new_event_loop()
                # Set the new event loop as the current event loop for the current thread
                # asyncio.set_event_loop(loop)
                # set the new event in here
                # ft = loop.create_task(self.newUsdtRun(address))
                # ft = await asyncio.to_thread(self.newUsdtRun, address)
                # Start a background thread
                thread = threading.Thread(target=self.newUsdtRun, args=[address])
                thread.start()
                self.scan_task[address] = thread
                self.scan_at += 1

        # self.find_task()
        # await asyncio.gather([v for k, v in self.scan_task.items()])

        for k, v in self.scan_task.items():
            v.join()

    def signal_handler(self, signum, frame):
        print(f"Signal {signum} received.")

    def newUsdtRun(self, address_t: str):
        USDTApp().CollectionTransactionFromTronForUSDT(address_t)
        Analysis().start(address_t)
