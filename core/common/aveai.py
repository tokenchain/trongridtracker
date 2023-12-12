import codecs
import json

import requests

import base64
import urllib.parse

from core.common.utils import JsonFileB, folder_paths


def aveai_header() -> dict:
    with open("data/avecookie", "r") as r:
        cookie_content = r.read()

    return {
        'Referer': 'https://ave.ai/',
        'Origin': 'https://ave.ai',
        'Accept': 'application/json, text/plain, */*',
        'ave-udid': cookie_content,
        'X-auth': '465e2a2cbc5d40d703e3a6e80c4a3cdd1694095767549794097',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 Firefox/117.0'
    }


# https://api.fgsasd.org/v1api/v3/pairs/0x6401bb570ebfc35b304900916d9a2dd7b54e2c48-bsc/txs?address=


def get_ave_overview(token_address: str):
    print(f'get side note from {token_address}')
    url = f'https://api.fgsasd.org/v1api/v3/pairs/{token_address}-bsc/txs?address='
    response = requests.get(url, headers=aveai_header())
    if response.status_code == 200:
        j = response.json()
        if 'status' in j:
            if j['status'] == 1:
                completion = j['encode_data']
                decode_d1 = base64.b64decode(completion).decode('utf-8')
                dat = urllib.parse.unquote(decode_d1)
                return json.loads(dat)

            elif j['status'] == 0:
                raise Exception(j['msg'])


    else:
        raise Exception("No Data")


class AveAnalysis:
    def __init__(self, case_name: str):
        base_folder = f"data/{case_name}"
        base_cache = f"data/{case_name}/cache"
        base_input = f"data/{case_name}/inputs"
        temp_fil = f"data/{case_name}/combine.csv"
        trading_avi = f"data/{case_name}/trading_avi.json"
        folder_paths([base_folder, base_cache, base_input])
        self.file_name = JsonFileB(trading_avi)
        self.array_sender = []

    def save_pair(self, pair: str):
        self.workdata = get_ave_overview(pair)
        self.file_name.dumpdict(self.workdata)
        print("file saved.")

    def check_involves(self):
        for n in self.workdata:
            if 'wallet_address' in n:
                address_sender = n['wallet_address']
                if address_sender not in self.array_sender:
                    self.array_sender.append(address_sender)

        for h in self.array_sender:
            print(h)
        print(f'total people: {len(self.array_sender)}')
