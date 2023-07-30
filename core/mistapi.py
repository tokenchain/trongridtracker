# _*_ coding: utf-8 _*_
# @Date:  5:56 下午
# @File: demo.py
# @Author: liyf
import json
import os

import requests
from .lib import TronscanAPI


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


def personal_overview_file(address: str) -> str:
    address_p = f"p_{address}.txt"
    return address_p


def get_mist_cache_dict(address: str) -> dict:
    print(f"🏖️ Get profile from - {address}")
    url = f'https://dashboard.misttrack.io/api/v1/address_overview?coin=USDT-TRC20&address={address}'
    path = os.path.join("data/mist", personal_overview_file(address))

    if os.path.isfile(path) is True:
        with open(path, newline='') as f:
            analysis_open = json.loads(f.read())
            return analysis_open
    try:
        response = requests.get(url, headers=getMistHeaders())
    except (
            requests.ConnectionError,
            requests.exceptions.ReadTimeout,
            requests.exceptions.Timeout,
            requests.exceptions.ConnectTimeout,
    ) as e:
        print(e)
        return {}
    if response.status_code == 200:
        return response.json()
    else:
        return {}


def get_mist_overview(address: str):
    print(f"⛱️ Get profile from - {address}")
    url = f'https://dashboard.misttrack.io/api/v1/address_overview?coin=USDT-TRC20&address={address}'
    path = os.path.join("data/mist", personal_overview_file(address))

    if os.path.isfile(path) is True:
        with open(path, newline='') as f:
            analysis_open = json.loads(f.read())
            return getPer(analysis_open)

    try:
        response = requests.get(url, headers=getMistHeaders())
    except (
            requests.ConnectionError,
            requests.exceptions.ReadTimeout,
            requests.exceptions.Timeout,
            requests.exceptions.ConnectTimeout,
    ) as e:
        print(e)
        return ""

    if response.status_code == 200:
        path = os.path.join("data/mist", personal_overview_file(address))
        TronscanAPI.writeFile(response.text, path)
        return getPer(response.json())
    else:
        return ""


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
        response = requests.get(url, params=data_params, headers=getMistHeaders(), stream=True, timeout=600)
    except (
            requests.ConnectionError,
            requests.exceptions.ReadTimeout,
            requests.exceptions.Timeout,
            requests.exceptions.ConnectTimeout,
            requests.RequestException,
            requests.ReadTimeout,
            ConnectionResetError
    ) as e:
        print(e)
        return ""

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


def find_transactions():
    path = os.path.join("data", "inputs", "list_scans.txt")
    f = open(path, "r")
    lines = f.readlines()
    ma = MistAcquireDat()
    for address in lines:
        address = address.replace("\n", "")
        ma.save(address)


class MistAcquireDat:
    def __init__(self):
        self.folder = "data/mist"
        self.tmp = {}
        # -1 incoming, 0 None, 1 outflow
        self.only_flow = 0

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
            self.tmp[k] = get_mist_cache_dict(address)
        return self.tmp[k]

    def overview(self, address: str) -> str:
        if address not in self.tmp:
            self.tmp[address] = get_mist_overview(address)

        return self.tmp[address]
