# _*_ coding: utf-8 _*_
# @Date:  5:56 下午
# @File: demo.py
# @Author: liyf
import glob
from json import JSONDecodeError
from typing import Tuple

import requests
import json

from lib.common.multidown import DownloadWorker
from lib.common.utils import Utils, ExportCSV, folder_paths, readfLock, setfLock, RestartStrike
import logging
import os
from queue import Queue
from time import time, sleep

from lib.etherscan.sqlc.sqlhelper import LargeCacheTransferToDb

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

logger = logging.getLogger(__name__)


def get_apikey():
    ctx = Utils(js_file_name='core/common/okapi.js').read_js_file()
    return ctx.call('getApiKey')


OKBASE = "https://www.oklink.com"


def generate_header():
    __headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36',
        'x-apiKey': get_apikey(),
        "OK-ACCESS-KEY": "63169dd7-c0d9-4db4-970f-c5f378265338"
    }
    return __headers


def get_json_data():
    url = f'{OKBASE}/api/explorer/v1/btc/transactionsNoRestrict'
    response = requests.get(url, params={
        "t": str(int(time.time()) * 1000),
        "limit": 20,
        "offset": 0
    }, headers=generate_header())
    return response.json()


def get_query_address_tx(file_path: str, q_addr: str, chain: str, page: int) -> bool:
    url = f'{OKBASE}/api/v5/explorer/address/transaction-list'
    with requests.get(url, params={
        "address": q_addr,
        "chainShortName": chain,
        "page": page,
        "limit": 100,
    }, headers=generate_header(), stream=True) as r:
        r.raise_for_status()
        with open(file_path, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
            return True


def get_csv_token_history(file_path: str, check_wallet: str, chain: str):
    chain = chain.lower()
    url = f'{OKBASE}/download/explorer/v1/{chain}/transactions/download'
    with requests.get(url, params={
        "address": check_wallet,
        "direction": 3,
        "end": "",
        "start": "",
        "value": "",
        "valueUpperLimit": "",
        "tokenType": "BEP20",
        "transactionType": "BEP20",
        "nonzeroValue": True,
        "otherAddress": ""
    }, headers=generate_header(), stream=True) as r:
        r.raise_for_status()
        with open(file_path, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)


def get_json_transactions(hash: str, chain: str):
    url = f'{OKBASE}/api/v5/explorer/transaction/transaction-fills'
    response = requests.get(url, params={
        "txid": hash,
        "chainShortName": chain
    }, headers=generate_header(), timeout=30)

    if response.status_code == 429:
        print('too many request ', end="\r")
        return ""

    if response.status_code != 200:
        print(f"ERROR from server.  {response.status_code}")
        return ""

    return response.json()


def get_json_tag_address(address_bip: str, chain: str):
    url = f'{OKBASE}/api/v5/tracker/tag/entity-tag'
    response = requests.get(url, params={
        "address": address_bip,
        "chainShortName": chain
    }, headers=generate_header())
    if response.status_code != 200:
        print(f"ERROR from server. got {response.status_code}")
        return ""

    return response.json()


def parse():
    result = get_json_data()
    data_list = result['data']['hits']
    for data in data_list:
        print(
            f'交易哈希: {data["hash"]}\n所在区块: {data["blockHeight"]}\n输入: {data["inputsCount"]}\n输出: {data["outputsCount"]}\n数量(BTC): {data["realTransferValue"]}')
        print('***' * 30)


class CacheAddressRead:
    """
    Read the regular CSV files from oklink and do the basic analysis
    """

    def __init__(self, fpath: str):
        self.transaction_folder = fpath
        self.address_list = []

    def scan_common_address(self):
        file_pattern = "*.csv"  # Replace with your specific file name pattern
        # Use glob to search for files with the specified name pattern
        search_f = os.path.join(self.transaction_folder, file_pattern)
        file_list = glob.glob(search_f)
        # Loop over each file and perform some operation
        for file_path in file_list:
            file_name = os.path.basename(file_path)
            address = file_name
            if address[0:2] == "0x":
                self.address_list.append({
                    "address": address,
                    "file": file_name
                })
        print("scan complete")
        return self

    def scan(self):
        file_pattern = "*.csv"  # Replace with your specific file name pattern
        # Use glob to search for files with the specified name pattern
        search_f = os.path.join(self.transaction_folder, file_pattern)
        file_list = glob.glob(search_f)
        # Loop over each file and perform some operation
        k = 0
        for file_path in file_list:
            file_name = os.path.basename(file_path)
            address = file_name.split("-")[1]
            if address[0:2] == "0x":
                self.address_list.append({
                    "address": address,
                    "file": file_name
                })
                k += 1
        print(f"scan complete with total wallet addresses of {k}")
        return self

    def get_wallet_addresses(self) -> list:
        """
        get the wallet addresses in here
        """
        return [a["address"] for a in self.address_list]

    def get_lines(self) -> list:
        """
        get the line addresses
        """
        storage = []
        records = 0
        for ob in self.address_list:
            addr = ob["address"]
            addr_file = ob["file"]
            loc_file = os.path.join(self.transaction_folder, addr_file)
            openfile = open(loc_file, "r")
            lines = openfile.readlines()
            lines = lines[1:]
            lines = [h.replace("\n", "") for h in lines]
            storage += lines
            records += len(lines)
        print(f"read total tx: {records}")
        return storage


class AddressIncomeExpenses:
    def __init__(self, token: str, main_wallet: str):
        self.token_addr = token
        self.wallet_addr = main_wallet
        self.expense_address = []
        self.income_address = []
        self.expense_details = {}
        self.income_details = {}
        self.full_sum = 0
        self.full_expense = 0
        self.full_income = 0

    def expense_hit(self, benefitiary: str, amount: float):
        if benefitiary not in self.expense_address:
            self.expense_address += benefitiary
            self.expense_details[benefitiary] = {"total": 0, "count": 0}

        self.expense_details[benefitiary]["total"] += amount
        self.expense_details[benefitiary]["count"] += 1
        self.full_sum += amount
        self.full_expense += amount

    def income_hit(self, benefitiary: str, amount: float):
        if benefitiary not in self.income_address:
            self.income_address += benefitiary
            self.income_details[benefitiary] = {"total": 0, "count": 0}

        self.income_details[benefitiary]["total"] += amount
        self.income_details[benefitiary]["count"] += 1
        self.full_sum += amount
        self.full_income += amount

    def print(self, token_name: str):
        print(f"data from {self.wallet_addr}")
        print(f"total expense: {self.full_expense} {token_name}")
        print(f"total income: {self.full_income} {token_name}")

    def print_address(self):
        for h in self.expense_details:
            print(h)

    def list_expenses_addresses(self) -> list:
        return [h for h in self.expense_details]

    def list_incomes_addresses(self) -> list:
        return [h for h in self.income_details]


class Cache:
    def __init__(self, trans_cache: str):
        self.transaction_cache = trans_cache
        self.address_cache_file = os.path.join(self.transaction_cache, "tags_bsc.json")
        if os.path.isfile(self.address_cache_file):
            try:
                with open(self.address_cache_file, newline='') as f:
                    self.address_cache = json.loads(f.read())
                    if self.address_cache is None:
                        self.address_cache = []
                    f.close()
            except (
                    FileNotFoundError,
                    JSONDecodeError
            ):
                print(f"error in opening. {self.address_cache_file}")
        self.chain = "BSC"
        self.progress_count = 0
        self.total_count = 0
        self.restart_strikes = RestartStrike()

    def scan_all_files(self) -> list:
        hashes = []
        file_pattern = "*.res"  # Replace with your specific file name pattern
        # Use glob to search for files with the specified name pattern
        search_f = os.path.join(self.transaction_cache, file_pattern)
        file_list = glob.glob(search_f)
        # Loop over each file and perform some operation
        for file_path in file_list:
            file_name = os.path.basename(file_path)
            hash = file_name
            if hash[0:2] == "0x":
                line = hash.replace(".res", "")
                hashes.append(line)

        print("scan complete", len(hashes))
        return hashes

    def setRestart(self, call_back):
        self.progress_count = 0
        self.total_count = 0
        self.restart_strikes.setRestartCallback(call_back)

    def setChain(self, c: str):
        self.chain = c

    def check_cache_validate(self, hash: str) -> bool:
        path = os.path.join(self.transaction_cache, f"{hash}.res")
        if os.path.isfile(path):
            if os.path.getsize(path) <= 5:
                return False
            else:
                return True
        else:
            return False

    def cache_transaction_get_text(self, hash: str) -> str:
        if hash[:2] != "0x":
            return ""
        content = ''
        path = os.path.join(self.transaction_cache, f"{hash}.res")
        if os.path.isfile(path):
            with open(path, newline='') as f:
                content = f.read()
                f.close()

        return content

    def cache_transaction_get(self, hash: str):
        if hash[:2] != "0x":
            return ""

        path = os.path.join(self.transaction_cache, f"{hash}.res")
        if os.path.isfile(path):
            if os.path.getsize(path) <= 5:
                return self.cachable_req(path, hash)

            openfile = open(path, "r")
            data = openfile.read()
            try:
                ssjson = json.loads(data)
            except JSONDecodeError:
                print(f"error in opening. {hash} file-> try again.")
                sleep(1)
                return self.cachable_req(path, hash)
            return ssjson
        else:
            return self.cachable_req(path, hash)

    def one_req(self, hash: str):
        path = os.path.join(self.transaction_cache, f"{hash}.res")
        self.cachable_req(path, hash)

    def cachable_req(self, path: str, hash: str) -> dict:
        js = get_json_transactions(hash, self.chain)
        openfile = open(path, "w")
        openfile.write(json.dumps(js))
        openfile.close()
        self.progress_count += 1
        return js

    def check_tag(self, address_dp: str) -> dict:
        for h in self.address_cache:
            if h["address"].lower() == address_dp.lower():
                return h

        jsst = get_json_tag_address(address_dp, self.chain)
        items = jsst.get("data")
        if len(items) > 0:
            self.address_cache.append(items[0])
        else:
            self.address_cache.append({
                "address": address_dp,
                "entityTagList": []
            })

        openfile = open(self.address_cache_file, "w")
        openfile.write(json.dumps(self.address_cache))
        openfile.close()

    def check_resync(self, hashls: list) -> bool:
        """
        this is the more advanced batch processing hash files
        """
        print("recheck completion")
        for hash in hashls:
            if self.check_cache_validate(hash) is False:
                print("found incomplete")
                return False
        return True

    def fetcher_bundle_hash(self, hashls: list):
        ts = time()
        self.total_count = len(hashls)

        # Create a queue to communicate with the worker threads
        queue = Queue()
        m = 0
        # Put the tasks into the queue as a tuple
        for hash in hashls:
            if hash[:2] != "0x":
                print(hash[:66])
                continue

            if self.check_cache_validate(hash) is False:
                print(f'Queueing {hash} ')
                queue.put((hash, self.one_req))
                # print(f'Queueing {hash} ', end="\r")
                m += 1
            else:
                self.progress_count += 1

        if m == 0:
            logging.info('Took %s', time() - ts)
            return

        # Create 8 worker threads
        for x in range(2):
            worker = DownloadWorker(queue)
            # Setting daemon to True will let the main thread exit even though the workers are blocking
            worker.daemon = True
            worker.start()

        while self.total_count > self.progress_count:
            percent = float(self.progress_count) / float(self.total_count)
            percentage = "{:.2%}".format(percent)
            self.restart_strikes.watch(percent)
            sleep(1)
            print(f"Wait in process {percentage} {self.progress_count} / {self.total_count}                ", end="\r")

        # Causes the main thread to wait for the queue to finish processing all the tasks
        queue.join()
        logging.info('Took %s', time() - ts)


class CacheLite:
    def __init__(self, trans_cache_folder: str, project: str):
        self.transaction_cache = trans_cache_folder
        self.address_cache_file = os.path.join(self.transaction_cache, "tags_bsc.json")
        if os.path.isfile(self.address_cache_file):
            try:
                with open(self.address_cache_file, newline='') as f:
                    self.address_cache = json.loads(f.read())
                    if self.address_cache is None:
                        self.address_cache = []
                    f.close()
            except (
                    FileNotFoundError,
                    JSONDecodeError
            ):
                print(f"error in opening. {self.address_cache_file}")
        self.chain = "BSC"
        self.progress_count = 0
        self.total_count = 0
        self.lp = LargeCacheTransferToDb(project)
        self.restart_strikes = RestartStrike()

    def setOKLinkChainSymbol(self, name: str):
        self.chain = name

    def setRestart(self, call_back):
        self.progress_count = 0
        self.total_count = 0
        self.restart_strikes.setRestartCallback(call_back)

    def cachable_req(self, hash: str) -> Tuple[str, dict]:
        js = get_json_transactions(hash, self.chain)
        return (json.dumps(js), js)

    def cache_transaction_get(self, hash: str) -> dict:
        if self.lp.isDbExist() is False:
            self.lp.newTable()

        if hash[:2] != "0x":
            raise Exception("not a valid hash address.")

        found = self.lp.find_in_cache(hash)

        if found is True:
            return self.lp.get_in_hash(hash)
        else:
            context, js = self.cachable_req(hash)
            if self.lp.process(hash, context) is True:
                pass
            return js

    def db(self) -> LargeCacheTransferToDb:
        return self.lp

    def check_resync(self, hashls: list) -> bool:
        """
        this is the more advanced batch processing hash files
        """
        print("recheck completion")
        for hash in hashls:
            if self.lp.find_in_cache(hash) is False:
                print("found incomplete")
                return False
        return True

    def one_req(self, hash: str):
        context, js = self.cachable_req(hash)
        if len(context) > 10 and isinstance(js, dict):
            if self.lp.process(hash, context) is True:
                self.progress_count += 1

    def fetcher_bundle_hash(self, hashls: list):
        ts = time()
        self.total_count = len(hashls)
        # Create a queue to communicate with the worker threads
        queue = Queue()
        m = 0
        # Put the tasks into the queue as a tuple
        for hash in hashls:
            if hash[:2] != "0x":
                print(hash[:66])
                continue

            if self.lp.find_in_cache(hash) is False:
                print(f'Queueing {hash} ')
                queue.put((hash, self.one_req))
                m += 1
            else:
                self.progress_count += 1

        if m == 0:
            logging.info('Took %s', time() - ts)
            return

        # Create 8 worker threads
        for x in range(2):
            worker = DownloadWorker(queue)
            # Setting daemon to True will let the main thread exit even though the workers are blocking
            worker.daemon = True
            worker.start()

        while self.total_count > self.progress_count:
            percent = float(self.progress_count) / float(self.total_count)
            percentage = "{:.2%}".format(percent)
            self.restart_strikes.watch(percent)
            sleep(1)
            print(f"Wait in process {percentage} {self.progress_count} / {self.total_count}                ", end="\r")

        # Causes the main thread to wait for the queue to finish processing all the tasks
        queue.join()
        logging.info('Took %s', time() - ts)


class AssembleOKLink:
    def __init__(self, case_name: str = "excel"):
        base_folder = f"data/{case_name}"
        base_cache = f"data/{case_name}/cache"
        base_input = f"data/{case_name}/inputs"
        temp_fil = f"data/{case_name}/combine.csv"
        folder_paths([base_folder, base_cache, base_input])
        self.inputfolder = base_input
        self.excelfolder = base_folder
        self.cache_read = CacheAddressRead(base_cache)
        self.cache = Cache(base_cache)
        self.usdt_in = 0
        self.usdt_out = 0
        self.usdt_invest = 0
        self.usdt_to_cex = 0
        self.usdt_from_other = 0
        self.find_usd_output = False
        self.tempfile = ExportCSV(temp_fil)

    def action(self):
        pass

    def action_start(self):
        if readfLock(self.excelfolder, "action_analysis") is False:
            setfLock(self.excelfolder, "action_analysis", True)
        else:
            print("The process is not finished. or not closed correctly.")
            exit(3)

    def action_end(self):
        setfLock(self.excelfolder, "action_analysis", False)

    def test_transaction(self, hash: str):
        dat = self.cache.cache_transaction_get(hash)

    def assembly_data(self):
        """
           [Tx Hash,blockHeight,blockTime(UTC+8),blockTime(UTC),from,to,value,fee,status]
        """
        data = self.cache_read.scan().get_lines()
        for l in data:
            self.tempfile.add_line(l)

    def check_unique_address(self):
        data = self.cache_read.scan().get_lines()
        show_add = []
        for l in data:
            txdetail = l.split(",")
            xfrom = txdetail[4].lower()
            xto = txdetail[5].lower()
            method = txdetail[1].lower()
            hash_transactions = txdetail[0].lower()
            if xfrom not in show_add:
                show_add.append(xfrom)
        for x in show_add:
            print(x)

    def get_section_data(self, hash: str) -> Tuple[list, str, dict]:
        dat = self.cache.cache_transaction_get(hash)
        if "code" in dat and int(dat["code"]) > 0:
            print(f"error from code {dat['code']}")
            return ([], "", {})

        if "data" in dat and len(dat['data']) >= 1:
            for section in dat['data']:
                input_data = section["inputData"]
                if "tokenTransferDetails" not in section:
                    continue
                details = section['tokenTransferDetails']
                return (details, input_data, section)

        return ([], "", {})

    def logicFindOutGetUSDOut(self):
        self.find_usd_output = True
        return self

    def sign_checker_0x(self, list_4bytes: list, data_input: str) -> bool:
        for h in list_4bytes:
            if h == data_input[:10]:
                return True
        return False

    def single_check_0x(self, sign: str, data_input: str) -> bool:
        return sign == data_input[:10]

    def transfer_check(self, data_input: str) -> bool:
        return self.single_check_0x("0xa9059cbb", data_input)

    def coin_by_listing(self, coin_list: list, input_data: str) -> int:
        for b in coin_list:
            s = input_data.find(b[2:])
            if s > 0:
                return s
        return 0


if __name__ == '__main__':
    parse()
