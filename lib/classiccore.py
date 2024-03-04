#!/usr/bin/env python3
# coding: utf-8
import csv
import asyncio
import glob
import json
import os
import time
from datetime import datetime
from typing import Union
import signal
import threading
import requests
import itertools as it
import graphviz
# import sys
# the mock-0.3.1 dir contains testcase.py, testutils.py & mock.py
# sys.path.append('/Users/hesdx/Documents/piplines/tron-tool-py/tronpytool')
# defi pool reader:: https://github.com/dpneko/pyutil
from urllib3.exceptions import ReadTimeoutError
from lib.common.utils import Utils
from . import *

try:
    import tls_client
except:
    os.system('python -m pip install tls-client')
    import tls_client


def get_apikey():
    ctx = Utils(js_file_name='core/common/okapi.js').read_js_file()
    return ctx.call('getApiKey')


def multiple_file_types(*patterns):
    return it.chain.from_iterable(glob.iglob(pattern) for pattern in patterns)


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


class WithTags:

    def __init__(self):
        self.tags = {}
        self.swaps = {}
        self.black = []

    def tagPre(self):
        with open('tagged.json', newline='') as f:
            tags = json.loads(f.read())
            self.tags = tags["exchange"]
            self.swaps = tags["swap"]
            print("tagging is loaded.")

    def isDex(self, address: str) -> bool:
        try:
            name = self.swaps[address]
            return True
        except KeyError:
            return False

    def isTagged(self, address: str) -> bool:
        try:
            name = self.tags[address]
            return True
        except KeyError:
            return False

    def tagging(self, address: str) -> str:
        if self.isTagged is True:
            return self.tags[address]
        return ""

    def tagdex(self, address: str) -> str:
        if self.isTagged is True:
            return self.dex[address]
        return ""


def GetTOKEN():
    return ""


def requestTimeStamp():
    print("URL request : %s" % time.ctime())


class TronscanAPI:
    """Deploy wrap contract in the deployment"""

    on_proxy = False

    def __init__(self):
        """

        folder_paths([
            "data/excel",
            "data/excel/cache"
        ])

        """

        self.outgoing = 0
        self.outcount = 0
        self.incoming = 0
        self.incount = 0
        self.records = 0
        self.outputfile = "report.txt"
        self.basefolder = ""
        self.next_link = ""
        self.fingerprint = ""
        self.logfile = ""
        self._m_address = ""
        self._m_balance = 0
        self.wallet_address = ""
        self.skip_dup = False
        self.page_at = 0

    @staticmethod
    def session_im():
        chrome_v = 112
        return tls_client.Session(
            client_identifier=f"chrome_{str(chrome_v)}",
            random_tls_extension_order=True
        )

    @staticmethod
    def writeFile(content, filename):
        fo = open(filename, "w")
        fo.write(content)
        fo.close()
        print(statement.format(time.ctime(), filename))

    def folderset(self, k: str) -> "TronscanAPI":
        self.basefolder = k
        return self

    def file(self, name: str) -> str:
        if self.basefolder != "":
            return os.path.join(self.basefolder, name)
        else:
            return name

    @staticmethod
    def t_proxy() -> str:
        test_proxy = "isp.proxiware.com:8080:115-167-97-95:MdjpI1GV6Gnd"
        proxy_set = test_proxy.split(":")
        test_proxy_y = f"http://{proxy_set[2]}:{proxy_set[3]}@{proxy_set[0]}:{proxy_set[1]}"

        result_p = None if TronscanAPI.on_proxy is True else test_proxy_y
        if TronscanAPI.on_proxy is True:
            TronscanAPI.on_proxy = False
        else:
            TronscanAPI.on_proxy = True
        return None

    @staticmethod
    def getTRC20Link(link: str):
        payload = {}
        headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:79.0) Gecko/20100101 Firefox/79.0',
                   'Accept': 'application/json, text/javascript, */*; q=0.01',
                   'Cookie': GetTOKEN(), 'Content-Type': 'application/json', 'Connection': 'keep-alive',
                   'Accept-Language': 'en-US,en;q=0.5', 'X-Requested-With': 'XMLHttpRequest'}

        requestTimeStamp()
        response = TronscanAPI.session_im().get(link, headers=headers, json=payload, proxy=TronscanAPI.t_proxy())
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
    def getTRC20List(account: str, trc20_address: str, limit: int, start_from: int):
        requestTimeStamp()

        response = TronscanAPI.get_pager_next(
            contract=account,
            start=start_from,
            limit=limit
        )

        if response.status_code == 200:
            try:
                dt = response.json()
                transfers_ok = []
                if "token_transfers" in dt:
                    transfers = dt["token_transfers"]
                    for h in transfers:
                        if "contract_address" in h:
                            if h["contract_address"] == trc20_address:
                                transfers_ok.append(h)

                    print(f"count usd: {len(transfers_ok)}, count total: {len(transfers)}")
                    """
                    if len(transfers) == 0:
                        print(dt)
                    """
                return transfers_ok
            except UnicodeEncodeError as e:
                print("please login first; %s;" % e)
                return 1
        else:
            print(response.content)
            print("connection problem occured")
            return 2

    @staticmethod
    def getOKLinkFile(account: str):
        request_url1 = "https://www.oklink.com/download/explorer/v1/tron/transactions/download/count"
        request_url2 = "https://www.oklink.com/download/explorer/v1/tron/transactions/download/"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 Firefox/114.0',
            "x-apiKey": get_apikey(),
        }
        payload_d = {
            "address": account,
            "contractAddress": account,
            "nonzeroValue": True,
            "tokenType": "TRC20",
            "transactionType": "TRC20",
            "t": int(time.time() * 1000)
        }
        print(payload_d)
        requestTimeStamp()
        # response = requests.request("GET", contract_get_api, headers=headers, data=payload)
        response = requests.request(
            "GET",
            request_url1,
            headers=headers,
            params=payload_d,
        )
        print(response)
        print(response.text)
        if response.status_code == 200:
            dat = response.json()
            if dat["code"] == 0:
                data = dat["data"]
                print(f"now need to see the data:: {data}")
                payload_d = {
                    "address": account,
                    "contractAddress": account,
                    "nonzeroValue": True,
                    "tokenType": "TRC20",
                    "transactionType": "TRC20"
                }

                response = requests.request(
                    "GET",
                    request_url2,
                    headers=headers,
                    params=payload_d,
                )
                print(response)
                if response.status_code == 200:
                    dispo = response.headers["content-disposition"].strip(";")
                    file_name = dispo.replace("attachment;filename=", "")
                    file_name = f"data/oklink/{file_name}"
                    TronscanAPI.writeFile(response.text, file_name)

            elif dat["code"] == 500:
                print("need to wait")
                time.sleep(10)
                return TronscanAPI.getOKLinkFile(account)

        else:
            print(response.content)
            print("connection problem occured")

    @staticmethod
    def getTRC20(account: str, trc20_address: str, limit: int):
        payload = {}
        headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:79.0) Gecko/20100101 Firefox/79.0',
                   'Accept': 'application/json, text/javascript, */*; q=0.01',
                   'Cookie': GetTOKEN(), 'Content-Type': 'application/json', 'Connection': 'keep-alive',
                   'Accept-Language': 'en-US,en;q=0.5', 'X-Requested-With': 'XMLHttpRequest'}

        contract_get_api = request_1_token.format(account, limit, trc20_address)
        requestTimeStamp()
        # response = requests.request("GET", contract_get_api, headers=headers, data=payload)

        response = TronscanAPI.session_im().get(
            contract_get_api,
            headers=headers,
            json=payload,
            proxy=TronscanAPI.t_proxy())

        if response.status_code == 200:
            try:
                return response.json()
            except UnicodeEncodeError as e:
                print("please login first; %s;" % e)
                return 1
        else:
            print(response.content)
            print("connection problem occured")
            return 2

    @staticmethod
    def get_pager_next(contract, start, limit):
        load_paylo = {
            "limit": limit,
            "start": start,
            "sort": "-timestamp",
            "count": True,
            "filterTokenValue": 0,
            "relatedAddress": contract
        }
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 Firefox/114.0',
            'Accept': 'application/json, text/plain, */*',
            'Content-Type': 'application/json',
            'Connection': 'keep-alive',
            'Cache-Control': 'no-cache',
            'Referer': 'https://tronscan.org/'
        }
        # contract_api = api_holders.format(limit, start, contract)
        requestTimeStamp()
        """
        response = TronscanAPI.session_im().get(
            API_PAGER,
            headers=headers,
            params=payload
        )
        """
        response = requests.request("GET", url=API_PAGER, params=load_paylo, headers=headers)
        print(response.status_code)
        if response.status_code == 200:
            try:
                return response
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
        # time.sleep(1)
        # response = requests.request("GET", url, headers=headers, data=payload)
        response = TronscanAPI.session_im().get(
            url,
            headers=headers,
            json=payload,
            proxy=TronscanAPI.t_proxy()
        )
        requestTimeStamp()
        if response.status_code == 200:
            try:
                return response.json()
            except UnicodeEncodeError as e:
                print("please login first; %s;" % e)
                return 1
            return 0
        else:
            print(response)
            print(response.text)
            return 2

    def checkTransaction(self, _id):
        print("hash id is {}".format(_id))

    def byOKlinkScan(self, trc20_address: str):
        grab_oklink(trc20_address, self.pre, self.Calcsum_OnceDone, self.EndLine)

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
        print(self.fingerprint)
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

    def pre(self, focus_address: str):
        self.outputfile = file_format.format(focus_address)
        self.logfile = filelog_format.format(focus_address)
        self.outgoing = 0
        self.outcount = 0
        self.incoming = 0
        self.incount = 0
        self.records = 0
        self.wallet_address = focus_address
        TronscanAPI.writeFile("", self.outputfile)

    def Calcsum_OnceDone(self, d) -> bool:
        if isinstance(d, list):
            from_address = d[4]
            to_address = d[5]
            transaction_id = d[0]
            readable = d[2]
            value_x = int(float(d[6]) * 10 ** 6)

            if from_address == self.wallet_address:
                self.outgoing = self.outgoing + value_x
                self.outcount += 1

            if to_address == self.wallet_address:
                self.incoming = self.incoming + value_x
                self.incount += 1

            self.records += 1

            data = [
                str(self.byValuei(value_x)),
                from_address,
                to_address,
                "USDT",
                transaction_id,
                readable, "\n"
            ]

            self.AppendLineTransaction(",".join(data))
            return True
        return False

    def Calcsum_op(self, json) -> bool:
        # print(f"items processing count {len(json)}")
        if isinstance(json, list):
            for row in json:
                if row["from_address"] == self.wallet_address:
                    self.outgoing = self.outgoing + int(row["quant"])
                    self.outcount += 1
                if row["to_address"] == self.wallet_address:
                    self.incoming = self.incoming + int(row["quant"])
                    self.incount += 1
                self.records += 1
                self.recordTransactionLine(row)
            return True
        return False

    def Calcal_op(self, json) -> bool:
        if isinstance(json, dict) and "data" in json:
            for row in json["data"]:
                if row["from"] == self.wallet_address:
                    self.outgoing = self.outgoing + int(row["value"])
                    self.outcount += 1
                if row["to"] == self.wallet_address:
                    self.incoming = self.incoming + int(row["value"])
                    self.incount += 1
                self.records += 1
                self.recordTransactionLine(row)
            return True
        return False

    def recordTransactionLine(self, row):
        # readable = datetime.datetime.fromtimestamp(row["block_timestamp"]).isoformat()
        ts = 0
        if "block_timestamp" in row:
            ts = int(row["block_timestamp"]) / 1000

        if "block_ts" in row:
            ts = int(row["block_ts"]) / 1000

        readable = datetime.utcfromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
        data = []

        if "value" in row:
            data = [
                str(self.byValue(row["value"])),
                row["from"],
                row["to"],
                "USDT",
                row["transaction_id"],
                readable, "\n"
            ]

        if "quant" in row:
            data = [
                str(self.byValue(row["quant"])),
                row["from_address"],
                row["to_address"],
                "USDT",
                row["transaction_id"],
                readable, "\n"
            ]

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
            statement_sum.format(
                self.wallet_address, value_out,
                self.outcount, value_in,
                self.incount, net
            )
        )

    def byValuei(self, amount: int) -> float:
        return float(amount) / float(1000000)

    def byValue(self, amount: str) -> float:
        return int(amount) / 1000000

    def skipDupFile(self) -> "TronscanAPI":
        self.skip_dup = True
        return self

    def getNextLoopList(self, address, contract, name):
        self.page_at += 1
        thread = 50
        start_x = self.page_at * thread
        json = self.getTRC20List(
            account=address,
            trc20_address=contract,
            limit=thread,
            start_from=start_x
        )
        if isinstance(json, int) and json == 2:
            print("retry in 20 seconds")
            time.sleep(20)
            self.getNextLoopList(address, contract, name)
        return json

    def looper(self, address: str, contract: str, name: str):
        if self.skip_dup is True and os.path.isfile(self.outputfile):
            if os.path.getsize(self.outputfile) > 1000:
                print(f"Found existing file {self.outputfile} and now skip the process")
                return

        TronscanAPI.writeFile("", self.outputfile)
        # json = self.getTRC20(address, contract, 100)
        json = self.getTRC20List(
            account=address,
            trc20_address=contract,
            limit=50,
            start_from=0
        )

        if isinstance(json, int) and json == 2:
            print("retry in 20 seconds")
            time.sleep(20)
            self.looper(address, contract, name)

        if isinstance(json, list):
            while True:
                if self.Calcsum_op(json) is False:
                    result = False
                else:
                    result = self.getNextLoopList(address, contract, name)

                if not result:
                    self.EndLine()
                    print("💒 Wrote report summary - complete.")
                    break

                print(statement_process.format(self.page_at, self.records))

        if isinstance(json, dict):
            p = 0
            while True:
                with GracefulInterruptHandler() as hp:
                    try:
                        if self.Calcal_op(json) is False:
                            result = False
                        else:
                            result = self.getNextLoop(json)

                    except TypeError as te:
                        print("☯︎ ", te)
                        continue

                    except requests.exceptions.Timeout as eg:
                        # Maybe set up for a retry, or continue in a retry loop
                        print("☯︎ request time out")
                        continue

                    except requests.exceptions.ConnectionError as ef:
                        # Maybe set up for a retry, or continue in a retry loop
                        print("☯︎ request time out")
                        continue

                    except requests.exceptions.TooManyRedirects as ep:
                        # Tell the user their URL was bad and try a different one
                        print("☯︎ too many requests now")
                        time.sleep(10)
                        continue

                    except requests.exceptions.HTTPError as eh:
                        print("☯︎ http error is now")
                        continue

                    except ReadTimeoutError as h:
                        print("☯︎ time out")
                        continue

                    except requests.exceptions.RequestException as ej:
                        # catastrophic error. bail.
                        print("☯︎ nothing but try again later")
                        continue

                    except requests.exceptions.SSLError:
                        print("☯︎ SSLError requests now")
                        time.sleep(10)
                        continue

                    if not result:
                        self.EndLine()
                        print("💒 Wrote report summary - complete.")
                        break

                    if isinstance(result, dict):
                        json = result

                    p += 1

                    print(statement_process.format(p, self.records))
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
        self.coin_name = ""

    def CollectionTransactionFromTronForUSDD(self, holder_address: str) -> None:
        self.coin_name = "USDD"
        self.forCoin(holder_address, "TPYmHEhy5n8TCEfYGqW2rPxsghSfzghPDn")

    def CollectionTransactionFromTronForBUSD(self, holder_address: str) -> None:
        self.coin_name = "BUSD"
        self.forCoin(holder_address, "TMz2SWatiAtZVVcH2ebpsbVtYwUPT9EdjH")

    def CollectionTransactionFromTronForTUSD(self, holder_address: str) -> None:
        self.coin_name = "TUSD"
        self.forCoin(holder_address, "TUpMhErZL2fhh4sVNULAbNKLokS4GjC1F4")

    def CollectionTransactionFromTronForUSDC(self, holder_address: str) -> None:
        self.coin_name = "USDC"
        self.forCoin(holder_address, "TEkxiTehnzSmSe2XqrBj4w32RUN966rdz8")

    def CollectionTransactionFromTronForUSDT(self, holder_address: str) -> None:
        self.coin_name = "USDT"
        self.forCoin(holder_address, "TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t")

    def CollectionOKLinkUSDT(self) -> None:
        self.coin_name = "USDT"
        self.oklinkCoin("TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t")

    def oklinkCoin(self, coin: str) -> None:
        self.byOKlinkScan(coin)

    def forCoin(self, holder: str, coin: str) -> None:
        self.wallet_address = holder
        self.outputfile = file_format.format(holder)
        self.logfile = filelog_format.format(holder)
        self.looper(holder, coin, self.coin_name)


class Analysis(WithTags):
    def __init__(self):
        super().__init__()
        self.hodlr = []
        self.booklegerlist = []
        self.exchange_assoc_book = {
            "head": []
        }
        self.exchanges_wallets = []
        self.bookleger = dict()
        self.logfile = ""
        self.outfile = ""
        self.exchange_re = ""
        self.line_scan = 0
        self._indent = 4
        self._encoding = "utf-8"
        self.tags = {}
        self.swaps = {}
        self.tagPre()

    def tagging(self, address: str) -> str:
        if address in self.tags:
            return self.tags[address]
        return ""

    def add_exchange_to_list(self, depo_wallet: str):
        for n in self.exchanges_wallets:
            if n == depo_wallet:
                return

        self.exchanges_wallets.append(depo_wallet)

    def handle_history_find_exchange_related_trnx(self, case_name: str):
        files = self.report_list()
        print(f"total report files: {len(files)}")
        self.exchange_re = case_report_summary.format(case_name)
        self.exchanges_wallets = []
        self.exchange_assoc_book["head"] = [
            f"### SUMMARY of {case_name.upper()}",
            f"# Scanned total related addresses of {len(files)} from the top rankings and documented as below:",
            "",
            "",
            ""
        ]

        for f in files:
            self.exchange_assoc(f)

        content_ex = ""

        for v in self.exchange_assoc_book:
            if v == "head":
                continue

            total = self.bookleger[v]["bal"]
            totalhit = self.bookleger[v]["hit"]
            mark = self.tagging(v)
            if total > 0:
                action = "transfer to"
            else:
                action = "received from"
            head = f"\n\n## Transactions: {totalhit}, total USDT {abs(total)} {action} {mark}\n"
            content = "\n".join(self.exchange_assoc_book[v])
            content_ex += head + content

        heX = ",".join(self.exchanges_wallets)
        LineX = f"The associated exchanges are: {heX}"
        self.exchange_assoc_book["head"].insert(3, LineX)

        with open(self.exchange_re, 'w') as f:
            write_daa = "\n".join(self.exchange_assoc_book["head"])
            f.write(write_daa + content_ex)
            f.close()

        print(help.format(FILENAME=self.exchange_re))

    def handle_history(self):
        files = self.report_list()
        print(f"total files: {len(files)}")
        for f in files:
            self.start(f)

    def report_list(self) -> list:
        os.chdir("data/reports")
        file_head = "report"
        tmp = []
        for file in multiple_file_types("*.txt"):
            key_len = len(file_head)
            if file[:key_len] == file_head:
                test_ep = file[key_len:(len(file) - len(".txt"))]
                gidchan = str(test_ep).split("_")
                address = gidchan[1]
                tmp.append(address)

        parent_folder = os.path.join("../..")
        # parent_folder = os.path.join("/Users/hesdx/Documents/piplines/trongridtracker")
        os.chdir(parent_folder)
        return tmp

    def _predat(self, address: str):
        # print("Current directory:", os.getcwd())
        self.logfile = file_format.format(address)
        self.outfile = file_analysis.format(address)
        self.hodlr = []
        self.booklegerlist = []
        self.bookleger = dict()
        self.line_scan = 0

    def get_analysis(self, holder_address: str) -> dict:
        self._predat(holder_address)
        path = os.path.join(os.getcwd(), self.outfile)
        if os.path.isfile(path) is False:
            return {}
        with open(path, newline='') as f:
            analysis_open = json.loads(f.read())

        return analysis_open

    def check_valid_data(self, file: str) -> bool:

        fix_last_line = False
        file1 = open(file, 'r')
        _lines = file1.readlines()
        _sum = len(_lines)
        net_count = 0
        _end_line = 0
        ll = 0

        for line in _lines:
            ll += 1
            if "Net" in line and line[0] == "N" and _end_line == 0:
                net_count += 1
                _end_line = ll

                op = line.split(".")
                if len(op) > 0:
                    _lines[ll - 1] = f"{op[0]}.000"
                    fix_last_line = True

        if _sum > _end_line or fix_last_line:
            with open(file, "w") as f:
                new_content = "".join(_lines[:_end_line + 1])
                print("fixed content")
                f.write(new_content)

        return net_count == 1

    def exchange_assoc(self, holder_address: str):
        self._predat(holder_address)
        print(self.logfile)
        self.line_scan = 0
        ok = self.check_valid_data(self.logfile)
        if ok is False:
            print(f"❌ File {self.logfile} is invalid! will need to remove contain now.")
            TronscanAPI.writeFile("", self.logfile)
            return
        file1 = open(self.logfile, 'r')
        _lines = file1.readlines()
        _sum = len(_lines)
        # Strips the newline character
        if _sum == 0:
            return
        pag = {
            "net_balance": 0,
            "out": 0,
            "in": 0,
        }
        print(f"start line - sum {_sum}")
        for line in _lines:
            self.line_scan += 1
            if self.isFooter(line, pag) is True:
                continue
            try:
                self.processLine(holder_address, line)
                self.processExchange_read(line)
            except IndexError:
                print("index erro. skip")
                continue

    def start(self, holder_address: str):
        self._predat(holder_address)
        print(self.logfile)
        self.line_scan = 0
        ok = self.check_valid_data(self.logfile)
        if ok is False:
            print(f"❌ File {self.logfile} is invalid! will need to remove contain now.")
            TronscanAPI.writeFile("", self.logfile)
            return
        file1 = open(self.logfile, 'r')
        _lines = file1.readlines()
        _sum = len(_lines)
        # Strips the newline character
        if _sum == 0:
            return
        # print(f"total lines -> {_sum}")
        pag = {
            "net_balance": 0,
            "out": 0,
            "in": 0,
        }
        print(f"start line - sum {_sum}")

        for line in _lines:
            self.line_scan += 1
            if self.isFooter(line, pag) is True:
                continue

            try:
                self.processLine(holder_address, line)
            except IndexError:
                print("index erro. skip")
                continue
        self.ender(pag)

    def isFooter(self, line: str, net_data: dict) -> bool:

        if "Total outgoing" in line:
            a = "Total outgoing USDT: "
            b = line.replace(a, "").split("/")
            net_data["out"] = int(float(b[0].strip()))
            return True

        if "Total incoming" in line:
            a = "Total incoming USDT: "
            b = line.replace(a, "").split("/")
            net_data["in"] = int(float(b[0].strip()))
            return True

        if "Net" in line and line[0] == "N":
            net_data["net_balance"] = int(float(line.replace("Net ", "")))
            return True

        if len(line) == 0:
            return True
        return False

    def ender(self, reader_net: dict):
        self.hodlr = []
        net_balance = reader_net["net_balance"]
        out = reader_net["out"]
        inflo = reader_net["in"]
        # self book ledger list book yes
        balance_temp = 0
        for k, v in self.bookleger.items():
            if k not in self.hodlr:
                self.hodlr.append(k)
                self.booklegerlist.append({
                    "address": k,
                    "bal": v["bal"],
                    "hit": v["hit"],
                    "mark": self.tagging(k)
                })
                balance_temp += v["bal"]

        self.booklegerlist = sorted(self.booklegerlist, key=lambda x: -x["bal"])

        with open(self.outfile, 'w') as f:
            json_str = json.dumps({
                "net_balance": balance_temp if net_balance == 0 else net_balance,
                "out": out,
                "in": inflo,
                "ranks": self.booklegerlist
            }, indent=self._indent)
            # data = jsonStr.encode(self._encoding)
            f.write(json_str)
            f.close()

        print(help.format(FILENAME=self.outfile))

    def processExchange_read(self, line: str, withDeposit: bool = False):
        p = line.strip().split(",")
        fromadd = p[1]
        toadd = p[2]
        val = p[0]
        hash = p[4]
        time = p[5]
        if self.isTagged(fromadd) is False and self.isTagged(toadd) is False:
            return
        line_r = ""

        if self.isTagged(fromadd):
            which = self.tagging(fromadd)
            line_r = f"\n   🏦 Withdrawal made from {which} {fromadd} with {val} to {toadd} at {time}\n"
            line_r += f"   - HashID [{hash}]"
            self.add_exchange_to_list(which)
            if fromadd not in self.exchange_assoc_book:
                self.exchange_assoc_book[fromadd] = []
            self.exchange_assoc_book[fromadd].append(
                line_r
            )

        if self.isTagged(toadd) and withDeposit:
            which = self.tagging(toadd)
            line_r = f"    🏦 Deposit made to {which} {toadd} from exchange personal account {fromadd} for {val} at {time}\n"
            line_r += f"    - HashID [{hash}]\n"
            self.add_exchange_to_list(which)
            if toadd not in self.exchange_assoc_book:
                self.exchange_assoc_book[toadd] = []
            self.exchange_assoc_book[toadd].append(
                line_r
            )

    def processLine(self, exclude_address: str, line: str):
        p = line.strip().split(",")
        # from
        fromadd = p[1]
        # to
        toadd = p[2]
        # value
        val = p[0]
        if fromadd == toadd == exclude_address:
            return

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


class OKLinkSubData:

    def __init__(self):
        self.booklegerlist = []
        self.jsonfile = ""
        self.holdself = " "
        self.scan_top = 4
        self.scan_at = 0
        self.scan_task = {}
        self.queue_list = []

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
        asyncio.run(self.corstart(address, 10000))

    def loop_run_coin_marlke(self, address_t: str):
        if self.scan_at < self.scan_top:
            USDTApp().getOKLinkFile(address_t)
            self.scan_at -= 1
            self.scan_task[address_t].join()
        else:
            self.queue_list.append(address_t)
            if isinstance(self.scan_task[address_t], threading.Thread):
                self.scan_task[address_t].join()

    async def corstart(self, holder_address: str, val_scope: int = 1000):
        self.holdself = holder_address
        self.jsonfile = file_analysis.format(holder_address)

        if os.path.exists(self.jsonfile) is False:
            return

        # if os.path.exists(self.jsonfile) is False:
        #    Path(self.jsonfile).touch()

        with open(self.jsonfile, newline='') as f:
            self.booklegerlist = json.loads(f.read())
            if "ranks" in self.booklegerlist:
                self.booklegerlist = self.booklegerlist["ranks"]

        if len(self.booklegerlist) == 0:
            return

        for ob in self.booklegerlist:
            if abs(ob["bal"]) > val_scope and ob["address"] != self.holdself and self.scan_at < self.scan_top:
                target_address = ob["address"]
                print(f"on task for scanning address {target_address}")
                # loop = asyncio.new_event_loop()
                # Start a background thread
                x = threading.Thread(target=self.loop_run_coin_marlke, args=[target_address])
                self.scan_task[target_address] = x
                self.scan_at += 1
                x.start()

        # self.find_task()
        # await asyncio.gather([v for k, v in self.scan_task.items()])

        # for k, v in self.scan_task.items():
        #    v.join()


class SubLayerAnalysis:
    def __init__(self):
        self.booklegerlist = []
        self.jsonfile = ""
        self.holdself = " "
        self.scan_top = 4
        self.scan_at = 0
        self.scan_task = {}
        self.queue_list = []

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
        asyncio.run(self.corstart(address, 10000))

    async def corstart(self, holder_address: str, val_scope: int = 1000):
        self.holdself = holder_address
        self.jsonfile = file_analysis.format(holder_address)

        if os.path.exists(self.jsonfile) is False:
            return

        # if os.path.exists(self.jsonfile) is False:
        #    Path(self.jsonfile).touch()

        with open(self.jsonfile, newline='') as f:
            self.booklegerlist = json.loads(f.read())
            if "ranks" in self.booklegerlist:
                self.booklegerlist = self.booklegerlist["ranks"]

        if len(self.booklegerlist) == 0:
            return

        for ob in self.booklegerlist:
            if abs(ob["bal"]) > val_scope and ob["address"] != self.holdself and self.scan_at < self.scan_top:
                target_address = ob["address"]
                print(f"on task for scanning address {target_address}")
                # loop = asyncio.new_event_loop()
                # Start a background thread
                x = threading.Thread(target=self.loop_run_coin_marlke, args=[target_address])
                self.scan_task[target_address] = x
                self.scan_at += 1
                x.start()

        # self.find_task()
        # await asyncio.gather([v for k, v in self.scan_task.items()])

        # for k, v in self.scan_task.items():
        #    v.join()

    def signal_handler(self, signum, frame):
        print(f"Signal {signum} received.")

    def loop_run_coin_marlke(self, address_t: str):
        if self.scan_at < self.scan_top:
            USDTApp().skipDupFile().CollectionTransactionFromTronForUSDT(address_t)
            Analysis().start(address_t)
            SubLayerAnalysis().start(address_t)
            self.scan_at -= 1
            self.scan_task[address_t].join()
        else:
            self.queue_list.append(address_t)
            if isinstance(self.scan_task[address_t], threading.Thread):
                self.scan_task[address_t].join()

    def fillReport(self):
        m = grab_reports()
        for a in m:
            USDTApp().CollectionTransactionFromTronForUSDT(a)


def capPattern(s: str) -> str:
    return f"*.{s}"


def p2f(x: str) -> float:
    return float(x.strip('%')) / 100


def grab_oklink(token, prepare, reader_item, read_end) -> list:
    os.chdir("data/oklink")
    tmp = []

    for file in multiple_file_types("*.csv"):
        a1 = file.replace("TRON-tokenTransaction-", "")
        focus_address = a1.split("--")[0]
        file1 = open(file, 'r')
        tmp.append({
            "address": focus_address,
            "file": file1
        })

    parent_folder = os.path.join("../..")
    os.chdir(parent_folder)

    for obj in tmp:
        focus_address = obj["address"]
        file1 = obj["file"]
        prepare(focus_address)
        _lines = file1.readlines()
        _sum = len(_lines)
        s = 0
        for line in _lines:
            if s > 0:
                data_entry = line.split(",")
                if token != data_entry[8]:
                    continue
                reader_item(data_entry)
            s += 1
        read_end()

    return tmp


def grab_reports() -> list:
    os.chdir("data/reports")
    tmp = []
    for file in multiple_file_types("*.txt"):
        file1 = open(file, 'r')
        _lines = file1.readlines()
        _sum = len(_lines)
        checked = False
        for line in _lines:
            if "Net" in line and line[0] == "N":
                checked = True
                continue

        if checked is True:
            continue

        if os.path.getsize(file) > 0 or checked is False:
            TronscanAPI.writeFile("", file)

        address = file.replace(".txt", "").replace("report_", "")
        tmp.append(address)

    parent_folder = os.path.join("../..")
    os.chdir(parent_folder)

    return tmp


class AnalysisMacro:
    def __init__(self):
        self.folder = "data/analysis"
        self.handle_address = ""
        self.metadata = {}
        self.rendered = False

    def start(self):
        file_pattern = "analysis_*.json"  # Replace with your specific file name pattern
        # Use glob to search for files with the specified name pattern
        # search = os.path.join(os.path.dirname(__file__), self.folder, file_pattern)
        search = os.path.join(self.folder, file_pattern)
        file_list = glob.glob(search)
        # Loop over each file and perform some operation
        for file_path in file_list:
            file_name = os.path.basename(file_path)
            self.handle_address = file_name.replace("analysis_", "").replace(".json", "")
            self._inside(file_path)

    def _inside(self, file):
        self.rendered = False
        self.metadata = {
            "from": [],
            "to": []
        }
        with open(file, newline='') as f:
            self.rf = json.loads(f.read())

            if "ranks" in self.rf:
                self.rf = self.rf["ranks"]
                for r in self.rf:
                    if r['mark'] != "":
                        if int(r['bal']) > 0:
                            self.metadata["to"].append(r['mark'])
                            self.rendered = True
                        if int(r['bal']) < 0:
                            self.metadata["from"].append(r['mark'])
                            self.rendered = True

            if self.rendered is True:
                print(f"{self.handle_address} deals with ")
                # print(self.metadata)
                if len(self.metadata['to']) > 0:
                    print(
                        f"It is possible the address is generated by the exchange {self.metadata['to'][0]}  for deposit")
                else:
                    print("exchange find withdrawals")


def build_bot_tpl(name: str, iter: int):
    dot = graphviz.Digraph(
        f"{name}-{iter}",
        comment='Blockchain address tracking',
        engine='dot',
        format='pdf'
    )
    dot.attr(
        ordering='out',
        showboxes='true',
        concentrate='true',
        compound='true',
        rankdir='LR',
        searchsize='10',
        ranksep='4.2 equally',
        size='1000,925'
    )
    return dot


def build_chart_relational(name: str):
    dot = graphviz.Digraph(
        "PhiloDilemma",
        engine='neato',
        format='pdf',
    )

    dot.attr(
        showboxes='true',
        ranksep='4.2 equally',
        size='1000,925'
    )


class GraphTron(WithTags):
    def __init__(self):
        super().__init__()
        self.exchange_user_deposits = []
        self.tagPre()

    def save_ex(self, deposit: str):
        for n in self.exchange_user_deposits:
            if n == deposit:
                return

        self.exchange_user_deposits.append(deposit)

    def show_all(self):
        if len(self.exchange_user_deposits) == 0:
            print("There is no exchange associated account found.")
            return
        for n in self.exchange_user_deposits:
            print(f"exchange user address: {n}")

    def tron_analysis_read(self, project_name: str, scope: int = 1000):
        a = Analysis()
        addresses = a.report_list()
        edges = 0
        file_count = 0
        sum_edges = 0
        dot = build_bot_tpl(project_name, file_count)

        for from_address in addresses:
            data = a.get_analysis(from_address)
            balance_net = in_balance = out_balance = 0
            if "balance" in data:
                balance_net = data["balance"]
            if "net_balance" in data:
                balance_net = data["net_balance"]
            if "out" in data:
                out_balance = data["out"]
            if "in" in data:
                in_balance = data["in"]

            if "ranks" in data:
                ranks = data["ranks"]
                if len(ranks) > 0:
                    for m in ranks:
                        to_address = m["address"]
                        balance = m["bal"]
                        hit = m["hit"]
                        special = m["mark"]

                        if to_address == from_address and balance > 0:
                            continue

                        if abs(balance) < scope:
                            continue

                        content_label = f"{hit} 笔, {abs(balance)}"
                        line_color = "black"

                        if balance > 0:

                            if self.isTagged(to_address):
                                # from_address = special + " user \n" + from_address
                                content_label += "\nTo " + special
                                line_color = "red"
                                dot.node(from_address, shape='box', fillcolor="firebrick1", style="filled",
                                         fontcolor="white")
                                self.save_ex(from_address)

                            a1 = from_address
                            a2 = to_address
                        else:

                            if self.isTagged(to_address):
                                content_label += "\nFrom " + special
                                line_color = "blue"
                                dot.node(to_address, shape='box', fillcolor="deepskyblue1", style="filled")

                            a1 = to_address
                            a2 = from_address

                        dot.edge(a1, a2, color=line_color, label=content_label)
                        edges += 1

            if out_balance == 0:
                final_box = f"{from_address}\n Total Balance: ${in_balance}"
                """dot.node(
                    from_address,
                    shape='box',
                    fillcolor="green",
                    style="filled",
                    fontcolor="blue",
                    label=final_box
                )"""

            if edges > 3000:
                print("Over 3000 edges will now need to cut off for another chart")
                dot.render(directory='data/charts').replace('\\', '/')
                file_count += 1
                sum_edges += edges
                edges = 0
                dot = build_bot_tpl(name=project_name, iter=file_count)

            # if edges > 10:
            #    break
        if edges > 0:
            print("end game final chart.")
            dot.render(directory='data/charts').replace('\\', '/')
            sum_edges += edges

        print(f"The total edges is {sum_edges}")
        self.show_all()
