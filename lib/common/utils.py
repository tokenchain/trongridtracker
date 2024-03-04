# _*_ coding: utf-8 _*_
# @Date:  4:37 下午
# @File: utils.py
# @Author: liyf
import glob
import json
import os.path
from json import JSONDecodeError

import execjs
import hashlib
import pandas as pd
from pandas import DataFrame

from lib import DATAPATH_BASE


# ocr = ddddocr.DdddOcr(show_ad=False)
# https://github.com/liyf-code/reverse_practice/tree/master
class Utils:
    def __init__(self, js_file_name=None, origin_md5_str=None):
        '''
        初始化参数
        :param js_file_name: 需要读取的js文件名称
        :param origin_md5_str: 需要进行md5加密的字符串
        '''
        self.js_file_name = js_file_name
        self.origin_md5_str = origin_md5_str

    def read_js_file(self):
        f = open(self.js_file_name, 'r')
        js_str = f.read()
        ctx = execjs.compile(''.join(js_str))
        return ctx

    def encrypt_md5(self) -> str:
        md5 = hashlib.md5()
        md5.update(self.origin_md5_str.encode('utf8'))
        return md5.hexdigest()


def readALlLines(file_path: str) -> list:
    openfile = open(file_path, "r")
    lines = openfile.readlines()
    openfile.close()
    return [h.replace("\n", "") for h in lines]


class JsonFileB:
    def __init__(self, _f):
        self.f = _f
        self.j = dict()
        if os.path.isfile(_f) is False:
            file_object = open(self.f, 'w')
            file_object.write("{}")
            file_object.close()
        else:
            self.read()

    def read(self):
        file_object = open(self.f, 'r', newline="")
        data = file_object.read()
        file_object.close()
        try:
            self.j = json.loads(data)
        except JSONDecodeError:
            print("malformed file data.")

        return self

    def save(self):
        file_object = open(self.f, 'w')
        file_object.write(json.dumps(self.j))
        file_object.close()

    def dumpdict(self, w: dict):
        file_object = open(self.f, 'w')
        file_object.write(json.dumps(w))
        file_object.close()

    def clear(self):
        file_object = open(self.f, 'w')
        file_object.write("{}")
        file_object.close()

    def put(self, key: str, val):
        self.j[key] = val
        self.save()

    def readflag(self, key: str) -> bool:
        if key in self.j:
            return self.j[key]
        else:
            return False


class ExportCSV:
    def __init__(self, _file):
        self.file = _file
        if os.path.isfile(_file) is False:
            self.clear()

    def clear(self):
        file_object = open(self.file, 'w')
        file_object.write("")
        file_object.close()

    def add_line(self, line: str):
        file_object = open(self.file, 'a')
        file_object.write(line + "\n")
        file_object.close()

    def delete(self):
        os.remove(self.file)


class ReadCombinedFile:
    """
    Only Read Hash file
    """

    def __init__(self, _file):
        self.file = _file

    def get_lines(self) -> list:
        """
        the all the lines from the file
        """
        storage = []
        lines = readALlLines(file_path=self.file)
        storage += lines
        records = len(lines)
        print(f"Read total tx: {records} from {self.file}")
        return storage

    def get_hashes(self) -> list:
        """
        read the first item from the given series
        the result is the hash of the transaction itself
        """
        lines = self.get_lines()
        index_hash = []
        for l in lines:
            r = l.split(",")
            index_hash.append(r[0])

        return index_hash


class ReadTokenTxCombined(ReadCombinedFile):
    def __init__(self, f: str):
        super().__init__(f)

    def captureTransactions(self):
        pass


class ReadTxCombined(ReadCombinedFile):
    def __init__(self, f: str):
        self.product = []
        super().__init__(f)

    def crossReferenceFrom(self, o: ReadTokenTxCombined, f: ExportCSV):
        data = o.get_lines()
        base_dat = self.get_lines()
        h = 0
        index_hash = []
        for l in base_dat:
            r = l.split(",")
            index_hash.append(r[0])

        for l2 in data:
            r2 = l2.split(",")
            try:
                found = index_hash.index(r2[0])
                method = base_dat[found].split(",")[1]
                print(f"matched item = {h} {method}", end="\r")
                cache = l2 + f",{method}"
                f.add_line(cache)
                h += 1
            except KeyboardInterrupt:
                exit(3)
            except ValueError:
                pass


class PersonalBank:
    def __init__(self):
        self.price = 0
        self.sum_usdt = 0
        self.sum_lk = 0
        self.lk_amount = 0
        self.usdt_amount = 0
        self.usdt_sell_sum = 0

    def set_usdt(self, usd: float):
        self.usdt_amount = usd
        self.sum_usdt += usd

    def set_lk(self, coin: float):
        self.lk_amount = coin
        self.sum_lk += coin

    def set_sell(self):
        self.usdt_sell_sum += self.usdt_amount

    def conclusion(self):
        print(f"Total USD {self.sum_usdt}, total LK {self.sum_lk}, total sold USD {self.usdt_sell_sum}")


class Stats:
    def __init__(self):
        self.usdt = []

    def set_sell_usdt(self, hash: str, amount: float, price: float):
        self.usdt.append({
            "tx": hash,
            "amount": amount,
            "price": price
        })

    def flood(self):
        sorted_amounts = sorted(self.usdt, key=lambda y: -y["amount"])
        for x in sorted_amounts:
            hash = x["tx"]
            amt = x["amount"]
            price = x["price"]
            print(f"{hash}, price {price} amount {amt}")


class ExcelBase:
    def _readDF(self, excel_file: str, sheet: str, header: list) -> DataFrame:
        data = pd.read_excel(excel_file, sheet_name=sheet)
        df = pd.DataFrame(data, columns=header)

        return df

    def _sheets(self, excel_file: str) -> list:
        sheetsf = []
        with pd.ExcelFile(excel_file) as f:
            sheets = f.sheet_names
            for sht in sheets:
                # df = f.parse(sht)
                sheetsf.append(sht)
        return sheetsf

    def find_sheet(self, full: str, list_sheets: list):
        h1 = len(full)
        for sh in list_sheets:
            h = len(sh)
            if full[h1 - h:h1] == sh.lower():
                return sh
        return ""

    def _get_sheet(self, sheet: str, header: list) -> DataFrame:
        return self._readDF(self._excel_file, sheet, header=header)

    def setExcelFile(self, path: str):
        self._excel_file = path

    def setHeader(self, header: list):
        self._excel_header = header


def folder_paths(folders: list):
    """
    prepare the system structures
    """
    for f in folders:
        start_fx = os.path.join(DATAPATH_BASE, f)
        if os.path.isdir(start_fx) is False:
            os.makedirs(start_fx)


def setfLock(base: str, status: str, action: bool):
    file_ = "unf_meta.lock"
    lock_f = os.path.join(base, file_)
    jf = JsonFileB(lock_f)
    jf.put(status, action)


def readfLock(base: str, status: str) -> bool:
    file_ = "unf_meta.lock"
    lock_f = os.path.join(base, file_)
    jf = JsonFileB(lock_f)
    return jf.readflag(status)


def find_key(dictsx: list, address: str) -> int:
    for i, item in enumerate(dictsx):
        if item["up"] == address:
            return i
    return -1


class FolderBase:
    mist_folder: str = ''
    inputfolder: str = ''
    cachefolder: str = ''
    mistcachefolder: str = ''
    excelfolder: str = ''
    project_name: str = ''

    def by_project_name(self, case_name: str):
        base_folder = f"data/{case_name}"
        base_cache = f"data/{case_name}/cache"
        base_input = f"data/{case_name}/inputs"
        base_mist = f"data/{case_name}/mist"
        base_charts = f"data/{case_name}/charts"
        base_mist_cache = f"data/{case_name}/mist/cache"
        folder_paths([base_folder, base_cache, base_input, base_mist, base_mist_cache])

        self.mist_folder = base_mist
        self.inputfolder = base_input
        self.cachefolder = base_cache
        self.mistcachefolder = base_mist_cache
        self.excelfolder = base_folder
        self.project_name = case_name
        self.chart_folder = base_charts


class RestartStrike:
    def __init__(self):
        self.strikes: int = 10
        self.check_perc: float = 0.0
        self.restart_call = None

    def setRestartCallback(self, func: any):
        self.restart_call = func

    def watch(self, perc: float):
        if perc == self.check_perc:
            self.strikes -= 1
        else:
            self.check_perc = perc

        if self.strikes <= 0:
            if self.restart_call != None:
                self.restart_call()
                self.strikes = 10
                print("restart progress.")
            else:
                print("there is nothing to call for restarting.")


class CacheAddressRead:
    """
    Read the regular CSV files from oklink and do the basic analysis
    """

    def __init__(self, fpath: str):
        self.baseFolder = fpath
        self.address_list = []

    def scan_page_fold(self):
        pattern_x = "*.csv"
        # Use glob to search for files with the specified name pattern
        search_f = os.path.join(self.baseFolder, pattern_x)
        file_list = glob.glob(search_f)
        # Loop over each file and perform some operation
        for file_path in file_list:
            file_name = os.path.basename(file_path)
            if file_name[0:2] == "ps":
                file_x = os.path.join(self.baseFolder, file_name)
                lines = readALlLines(file_x)
                lines = [h.split(",")[0] for h in lines]
                self.address_list = lines

        print("scan complete")
        return self

    def scan_common_address(self):
        pattern_x = "*.csv"  # Replace with your specific file name pattern
        # Use glob to search for files with the specified name pattern
        search_f = os.path.join(self.baseFolder, pattern_x)
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
        pattern_x = "*.csv"  # Replace with your specific file name pattern
        # Use glob to search for files with the specified name pattern
        search_f = os.path.join(self.baseFolder, pattern_x)
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
            loc_file = os.path.join(self.baseFolder, addr_file)
            lines = readALlLines(loc_file)
            lines = lines[1:]
            storage += lines
            records += len(lines)
        print(f"read total tx: {records}")
        return storage
