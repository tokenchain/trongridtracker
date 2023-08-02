# _*_ coding: utf-8 _*_
# @Date:  5:56 下午
# @File: demo.py
# @Author: liyf

import time
import requests

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


def parse():
    result = get_json_data()
    data_list = result['data']['hits']
    for data in data_list:
        print(
            f'交易哈希: {data["hash"]}\n所在区块: {data["blockHeight"]}\n输入: {data["inputsCount"]}\n输出: {data["outputsCount"]}\n数量(BTC): {data["realTransferValue"]}')
        print('***' * 30)


if __name__ == '__main__':
    parse()
