# _*_ coding: utf-8 _*_
# @Date:  5:56 下午
# @File: demo.py
# @Author: liyf
import json
import os
import time
import urllib

import requests
from lib.common.utils import folder_paths, FolderBase
from lib.etherscan.sqlc.mist import MistData


class MistException(Exception):
    ...


class NoProfileFound(MistException):
    ...


MISTBASE = "https://dashboard.misttrack.io"
WATCH_COIN = {
    "coin": "USDT-BEP20",
}


def enable_USDT_BEP20():
    WATCH_COIN.update({
        "coin": "USDT-BEP20"
    })


def enable_BNB():
    WATCH_COIN.update({
        "coin": "BNB"
    })


def enable_USDT_ERC20():
    WATCH_COIN.update({
        "coin": "USDT-ERC20"
    })


def enable_DAI_POLYGON():
    WATCH_COIN.update({
        "coin": "DAI-Polygon"
    })


def enable_TRX_TRON():
    WATCH_COIN.update({
        "coin": "TRX"
    })


def enable_USDT_TRC20():
    WATCH_COIN.update({
        "coin": "USDT-TRC20"
    })


def enable_USDT_ARB():
    WATCH_COIN.update({
        "coin": "USDT-Arbitrum"
    })


PROXY_ON = False


def getProxy():
    if PROXY_ON is True:
        return {
            'http': 'http://127.0.0.1:7890',
            'https': 'http://127.0.0.1:7890'
        }
    else:
        return None


try:
    response = requests.get(
        "http://www.google.com",
        proxies={
            'http': 'http://127.0.0.1:7890',
            'https': 'http://127.0.0.1:7890'
        }
    )
except IOError:
    print("Connection error! (Check proxy)")
    PROXY_ON = False
else:
    print("Proxy is ON")


def mist_header_api(token: str = "", address: str = ""):
    with open("data/mistcookie", "r") as r:
        cookie_content = r.read()

    if cookie_content == "":
        print("Error: no cookie is found. please make sure the updated cookie is acquired from the brower")
        return {
            'Cookie': "___",
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 Firefox/114.0'
        }

    cookie_content = cookie_content.rstrip("\n")
    basic = {
        'Cookie': cookie_content,
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 Firefox/114.0'
    }

    if address != "":
        basic.update({
            "Referer": f"https://dashboard.misttrack.io/address/{token}/{address}"
        })

    return basic


def get_json_address_overview(address: str, coin_type: str) -> dict:
    url = f'{MISTBASE}/api/v1/address_overview'
    print(address, coin_type)
    try:
        data_params = dict()
        if coin_type is None:
            data_params.update(WATCH_COIN)
        else:
            data_params.update({
                "coin": coin_type
            })
        data_params.update({
            "address": address
        })
        coin = WATCH_COIN["coin"] if coin_type is None else coin_type
        response = requests.get(
            url,
            params=data_params,
            headers=mist_header_api(coin, address),
            timeout=30,
            proxies=getProxy()
        )
    except (
            requests.ConnectionError,
            requests.exceptions.ReadTimeout,
            requests.exceptions.Timeout,
            requests.exceptions.ConnectTimeout,
    ) as e:
        print(f"req {url} timeout. try again.")
        return get_json_address_overview(address, coin_type)

    if response.status_code != 200:
        print(f"ERROR from server. got {response.status_code}")
        return {}

    return response.json()


class CacheMistApi:
    def __init__(self, transaction_cache: str):
        self.transaction_cache = transaction_cache

    def has_file_local(self, address: str) -> bool:
        path = os.path.join(self.transaction_cache, f"p_{address}.txt")
        return os.path.isfile(path)

    def read_file_data(self, address: str) -> str:
        path = os.path.join(self.transaction_cache, f"p_{address}.txt")
        openfile = open(path, "r")
        return openfile.read()

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
        print(f"⛱️ Get profile from - {address}")
        js = get_json_address_overview(address, None)
        openfile = open(path, "w")
        openfile.write(json.dumps(js))
        openfile.close()
        return js


def handleResponseApi(j: dict) -> str:
    if "success" in j and j["success"] is False:
        print(j)
        raise NoProfileFound()
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
        "address": address
    })
    data_params.update(WATCH_COIN)
    url = f'{MISTBASE}/api/v1/address_graph_analysis'
    try:
        coin = WATCH_COIN["coin"]
        response = requests.get(
            url,
            params=data_params,
            headers=mist_header_api(coin, address),
            stream=True,
            timeout=600,
            proxies=getProxy()
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
        print(f"Errors or timeout from doing request from {url}->{e}")
        return get_mist_graph_api(address, data_params)

    if response.status_code == 200:
        response.raw.decode_content = True
        j = response.json()
        if "success" in j and j["success"] is False:
            print(f"Skip graph analysis {address} due to server busy or expired trails")
            time.sleep(5)
            return {}
        else:
            return j
    else:
        print("not 200", response.status_code)

        return {}


class MistAcquireDat(FolderBase):
    def __init__(self, project: str = ""):
        if project == "":
            folder_paths([
                "data/mist",
                "data/inputs",
                "data/mist/cache"
            ])
            self.mist_folder = "data/mist"
            self.inputfolder = "data/inputs"
            self.cache = CacheMistApi("data/mist/cache")
        else:
            self.by_project_name(project)
            self.cache = CacheMistApi(self.mistcachefolder)
        self.tmp = {}
        # -1 incoming, 0 None, 1 outflow
        self.only_flow = 0
        self.filter_date = None
        self.sql = MistData(project)

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

    def dateRange(self, from_d: str, to_d: str):
        self.filter_date = [from_d, to_d]
        return self

    def save_map(self, filepath: str, address: str):
        fo = open(filepath, "r")
        content = fo.read()
        fo.close()
        if content != "":
            self.sql.sync_coin_report(address, WATCH_COIN.get("coin"), json.loads(content))

    def save(self, _address: str, check_double: bool = False):
        if self.sql.is_report_found(_address, WATCH_COIN.get("coin")) is True and check_double is True:
            return

        content = get_mist_graph_api(_address, self.time_filter())
        if content != {}:
            self.sql.sync_coin_report(_address, WATCH_COIN.get("coin"), content)

    def time_filter(self) -> dict:
        filter_list = []
        if self.filter_date is not None and len(self.filter_date) > 0:
            filter_list = f"{self.filter_date[0]} 00:00:00~{self.filter_date[1]} 00:00:00"

        data_fs = {
            "time_filter": filter_list
        }

        if self.only_flow < 0:
            data_fs["only_out"] = 0

        if self.only_flow > 0:
            data_fs["only_out"] = 1
        return data_fs

    def getFile(self, address: str) -> str:
        self.save(address)
        file_name = f"{address}.json"
        _file_save = os.path.join(self.mist_folder, file_name)
        return _file_save

    def onlyIncoming(self):
        self.only_flow = -1
        return self

    def onlyOutcoming(self):
        self.only_flow = 1
        return self

    def calculateOverview(self, address: str):
        file_ = f"{address}-timed.json"
        path = os.path.join(self.mist_folder, file_)

        if os.path.isfile(path) is False:
            print(f"The file for {address} with time range is not found.")
            return

        f = open(path, "r")
        lines = f.read()
        ok = json.loads(lines)
        main_id = ""
        for s in ok["graph_dic"]["node_list"]:
            main_address = s["addr"]
            if main_address.lower() == address.lower():
                main_id = s["id"]
                break

        expense = 0
        income = 0

        for edges in ok["graph_dic"]["edge_list"]:
            val = int(edges["val"])
            if edges["from"] == main_id:
                expense += val

            if edges["to"] == main_id:
                income += val

        first = ok["graph_dic"]["first_tx_datetime"]
        latest = ok["graph_dic"]["latest_tx_datetime"]
        txcount = ok["graph_dic"]["tx_count"]
        line = f"First {first} - Last {latest}|tx_count:{txcount}|income: {income}|expense:{expense}"
        line = line.replace("|", "\n")
        print(line)

    def overview(self, address_ps: str, coin_type: str) -> str:
        try:
            if self.cache.has_file_local(address_ps) is True:
                print("find from the folder.")

                jk = self.cache.read_file_data(address_ps)
                self.sql.update_profile(address_ps, {
                    "coin_type": coin_type,
                    "file": jk})
                content = json.loads(jk)
                return handleResponseApi(content)
            else:
                if self.sql.has_profile(address_ps) is True:
                    print("find from the db yes.")
                    content = self.sql.read_profile(address_ps, coin_type)
                    if "InvalidAddress" in content:
                        if isinstance(content, dict):
                            return handleResponseApi(content)
                        else:
                            return ''
                    else:
                        d_j = get_json_address_overview(address_ps, coin_type)
                        self.sql.update_profile(address_ps, {
                            "coin_type": coin_type,
                            "file": json.dumps(d_j)})
                        return handleResponseApi(d_j)
                else:

                    d_j = get_json_address_overview(address_ps, coin_type)
                    self.sql.update_profile(address_ps, {"file": json.dumps(d_j)})
                    return handleResponseApi(d_j)

        except NoProfileFound:
            print("no profile is found for this address")
            print(address_ps, coin_type)
            print("=====================================")
            return ""

        except KeyError:
            print(f"No data found for this address {address_ps} - {coin_type}")
            return ""

        except Exception:
            return ""

    def overview_n_dict(self, address_ps: str, coin_type: str) -> dict:
        if self.cache.has_file_local(address_ps) is True:
            pro_hen = self.cache.read_file_data(address_ps)
            self.sql.update_profile(address_ps, {"file": pro_hen, "coin_type": coin_type})
            return json.loads(pro_hen)
        else:
            if self.sql.has_profile(address_ps) is True:
                content = self.sql.read_profile(address_ps, coin_type)
                if isinstance(content, dict):
                    return content
                else:
                    return {}
            else:
                try:
                    dict_pro = get_json_address_overview(address_ps, coin_type)
                    self.sql.update_profile(address_ps, {"file": json.dumps(dict_pro), "coin_type": coin_type})
                    return dict_pro
                except Exception:
                    return {}
