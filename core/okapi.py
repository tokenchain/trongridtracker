# _*_ coding: utf-8 _*_
# @Date:  5:56 下午
# @File: demo.py
# @Author: liyf
import glob
import time
import requests
import os
import json
from .utils import Utils


def get_apikey():
    ctx = Utils(js_file_name='core/okapi.js').read_js_file()
    return ctx.call('getApiKey')


OKBASE = "https://www.oklink.com"
"GET /api/v5/explorer/transaction/transaction-fills?chainShortName=btc"


def get_json_data():
    url = f'{OKBASE}/api/explorer/v1/btc/transactionsNoRestrict'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36',
        'x-apiKey': get_apikey()
    }
    response = requests.get(url, params={
        "t": str(int(time.time()) * 1000),
        "limit": 20,
        "offset": 0

    }, headers=headers)
    return response.json()


def get_json_transactions(hash: str, chain: str):
    url = f'{OKBASE}/api/v5/explorer/transaction/transaction-fills'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36',
        'x-apiKey': get_apikey(),
        "OK-ACCESS-KEY": "63169dd7-c0d9-4db4-970f-c5f378265338"
    }
    response = requests.get(url, params={
        "txid": hash,
        "chainShortName": chain
    }, headers=headers)
    if response.status_code != 200:
        print(f"ERROR from server. got {response.status_code}")
        return ""

    return response.json()


def get_json_tag_address(address_bip: str, chain: str):
    url = f'{OKBASE}/api/v5/tracker/tag/entity-tag'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36',
        'x-apiKey': get_apikey(),
        "OK-ACCESS-KEY": "63169dd7-c0d9-4db4-970f-c5f378265338"
    }
    response = requests.get(url, params={
        "address": address_bip,
        "chainShortName": chain
    }, headers=headers)
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
    def __init__(self, fpath: str):
        self.transaction_folder = fpath
        self.address_list = []

    def scan(self):
        file_pattern = "*.csv"  # Replace with your specific file name pattern
        # Use glob to search for files with the specified name pattern
        search_f = os.path.join(self.transaction_folder, file_pattern)
        file_list = glob.glob(search_f)
        # Loop over each file and perform some operation
        for file_path in file_list:
            file_name = os.path.basename(file_path)
            address = file_name.split("-")[1]
            if address[0:2] == "0x":
                self.address_list.append({
                    "address": address,
                    "file": file_name
                })
        print("scan complete")
        return self

    def capture_data(self) -> list:
        storage = []
        for ob in self.address_list:
            addr = ob["address"]
            addrfile = ob["file"]
            loc_file = os.path.join(self.transaction_folder, addrfile)
            openfile = open(loc_file, "r")
            lines = openfile.readlines()
            lines = lines[1:]
            lines = [h.replace("\n", "") for h in lines]
            # total = len(lines)
            # print(f"total of tx {total} from - {addrfile}")
            storage += lines
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
        # print(self.expense_details)
        # print(self.income_details)
        # print(self.full_sum)
        print(f"total expense: {self.full_expense} {token_name}")
        print(f"total income: {self.full_income} {token_name}")


class Cache:
    def __init__(self, transaction_cache: str):
        self.transaction_cache = transaction_cache
        self.address_cache_file = os.path.join(self.transaction_cache, "tags_bsc.json")
        if os.path.isfile(self.address_cache_file):
            with open(self.address_cache_file, newline='') as f:
                self.address_cache = json.loads(f.read())
                if self.address_cache is None:
                    self.address_cache = []
                f.close()

    def cache_transaction_get(self, hash: str):
        path = os.path.join(self.transaction_cache, f"{hash}.res")
        if os.path.isfile(path):
            openfile = open(path, "r")
            data = openfile.read()
            if data.strip() == "":
                return self.cachable_req(path, hash)

            # print("get file data")
            return json.loads(data)
        else:
            # print("get file")
            return self.cachable_req(path, hash)

    def cachable_req(self, path: str, hash: str) -> dict:
        js = get_json_transactions(hash, "BSC")
        openfile = open(path, "w")
        openfile.write(json.dumps(js))
        openfile.close()
        return js

    def check_tag(self, address_dp: str) -> dict:
        for h in self.address_cache:
            if h["address"].lower() == address_dp.lower():
                return h

        jsst = get_json_tag_address(address_dp, "BSC")
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


if __name__ == '__main__':
    parse()
