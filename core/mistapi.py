# _*_ coding: utf-8 _*_
# @Date:  5:56 下午
# @File: demo.py
# @Author: liyf
import json
import os

import requests
from .lib import TronscanAPI
from .utils import folder_paths

MISTBASE = "https://dashboard.misttrack.io"


def getMistHeaders():
    with open("data/mistcookie.txt", "r") as r:
        cookie_content = r.read()

    if cookie_content == "":
        print("Error: no cookie is found. please make sure the updated cookie is acquired from the brower")
        return {
            'Cookie': "___",
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 Firefox/114.0'
        }
    cookie_content = cookie_content.replace("\n", "")

    return {
        'Cookie': cookie_content,
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 Firefox/114.0'
    }


def get_json_address_overview(address: str) -> dict:
    url = f'{MISTBASE}/api/v1/address_overview'
    try:
        response = requests.get(url, params={
            "coin": "USDT-TRC20",
            "address": address
        }, headers=getMistHeaders(), timeout=30)
    except (
            requests.ConnectionError,
            requests.exceptions.ReadTimeout,
            requests.exceptions.Timeout,
            requests.exceptions.ConnectTimeout,
    ) as e:
        print(f"req {url} timeout. try again.")
        return get_json_address_overview(address)

    if response.status_code != 200:
        print(f"ERROR from server. got {response.status_code}")
        return {}

    return response.json()


class CacheMistApi:
    def __init__(self, transaction_cache: str):
        self.transaction_cache = transaction_cache

    def cache_transaction_get(self, address: str) -> dict:
        path = os.path.join(self.transaction_cache, f"p_{address}.txt")
        if os.path.isfile(path):
            openfile = open(path, "r")
            data = openfile.read()
            check = json.loads(data)
            if "msg" in check and check['msg'] == "NotLoggedIn":
                print("data needs to be updated now.")
                return self.cachable_req(path, address)

            if data.strip() == "" or data == {}:
                return self.cachable_req(path, address)
            return json.loads(data)
        else:
            return self.cachable_req(path, address)

    def cachable_req(self, path: str, address: str) -> dict:
        print(f"⛱️  Get profile from - {address}")
        js = get_json_address_overview(address)
        openfile = open(path, "w")
        openfile.write(json.dumps(js))
        openfile.close()
        return js


def getPer(j: dict) -> str:
    if "success" in j and j["success"] is False:
        print(j)
        return ""
    else:
        text = f'\nBalance: {j["balance"]}'
        text += f'\ntx_count: {j["tx_count"]}'
        text += f'\nfirst_tx_time: {j["first_tx_time"]}'
        text += f'\nlast_tx_time: {j["last_tx_time"]}'
        text += f'\ntotal received: {j["total_received"]}'
        text += f'\ntotal spent: {j["total_spent"]}'
        text += f'\nreceived count: {j["received_count"]}'
        text += f'\nspent_count: {j["spent_count"]}'
        return text


def get_mist_graph_api(address: str, data_params: dict):
    data_params.update({
        "coin": "USDT-TRC20",
        "address": address
    })
    url = f'https://dashboard.misttrack.io/api/v1/address_graph_analysis'
    try:
        print(data_params)
        response = requests.get(
            url,
            params=data_params,
            headers=getMistHeaders(),
            stream=True,
            timeout=600
        )
    except (
            requests.ConnectionError,
            requests.exceptions.ReadTimeout,
            requests.exceptions.Timeout,
            requests.exceptions.ConnectTimeout,
            requests.RequestException,
            requests.ReadTimeout,
            ConnectionResetError
    ) as e:
        print(f"errors or timeout from doing request from {url} ->")
        return get_mist_graph_api(address, data_params)

    if response.status_code == 200:
        response.raw.decode_content = True
        j = response.json()
        if "success" in j and j["success"] is False:
            print(j)
            return ""
        else:
            return response.text
    else:

        return ""


class MistAcquireDat:
    def __init__(self):
        folder_paths([
            "data/mist",
            "data/inputs",
            "data/mist/cache"
        ])
        self.folder = "data/mist"
        self.inputfolder = "data/inputs"
        self.tmp = {}
        # -1 incoming, 0 None, 1 outflow
        self.only_flow = 0
        self.cache = CacheMistApi("data/mist/cache")

    def scan_addresses(self, file: str):
        path = os.path.join(self.inputfolder, file)
        if os.path.isfile(path) is False:
            print(f"Error the source file {file} is not found")
            return
        f = open(path, "r")
        lines = f.readlines()
        ma = MistAcquireDat()
        for address in lines:
            address = address.replace("\n", "")
            ma.save(address)

    def save(self, address: str, filter: list = []):
        filter_list = []
        if len(filter) > 0:
            filter_list = f"{filter[0]}%2000:00:00~{filter[1]}%2000:00:00"

        data_fs = {
            "time_filter": filter
        }

        if self.only_flow < 0:
            data_fs["only_out"] = 0

        if self.only_flow > 0:
            data_fs["only_out"] = 1

        content = get_mist_graph_api(address, data_fs)
        if content == "":
            return
        file_name = f"{address}-{filter}.json"
        file = os.path.join(self.folder, file_name)
        TronscanAPI.writeFile(content, file)

    def onlyIncoming(self):
        self.only_flow = -1
        return self

    def onlyOutcoming(self):
        self.only_flow = 1
        return self

    def overviewdict(self, address: str) -> dict:
        k = f"dict_{address}"
        if k not in self.tmp:
            payload = self.cache.cache_transaction_get(address)
            self.tmp[k] = payload
        return self.tmp[k]

    def overview(self, address: str) -> str:

        if address not in self.tmp:
            payload = self.cache.cache_transaction_get(address)

            self.tmp[address] = getPer(payload)

        return self.tmp[address]
