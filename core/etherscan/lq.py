# !/usr/bin/env python
# coding: utf-8
import json
import os
import time
from urllib.parse import urlparse

from core import DATAPATH_BASE
from core.common.xscanutils import SCAN_X, generate_header
from core.etherscan.arbiscan import ArbiScan
from core.etherscan.sqlc.sqlhelper import LargeTransactionDb

from core.common.utils import CacheAddressRead, folder_paths, ExportCSV, ReadTxCombined, ReadTokenTxCombined, setfLock, \
    readfLock, \
    FolderBase

import requests
from bs4 import BeautifulSoup
from time import sleep

from core.reql import ReadHash

"""
This code base support large query data crawl from any of the 
1. etherscan - https://etherscan.io
            - https://cn.etherscan.com/
2. bscscan - https://bscscan.com/
3. arbiscan - https://arbiscan.io/
4. polygonscan - https://polygonscan.com/
5. basescan - https://basescan.org/

"""


class ScannerReq:
    underlying_endpoint_base: SCAN_X
    target_address: str
    starting_blocknumber: int
    page_count: int
    cpage: int
    enable_debug_page_parse: bool

    def enablePageLog(self):
        self.enable_debug_page_parse = True

    def setEndpointBase(self, url_endpoint: SCAN_X):
        self.underlying_endpoint_base = url_endpoint

    def setStartBlockNumber(self, bknum: int):
        self.starting_blocknumber = bknum

    def setStartPageAt(self, page_id: int):
        self.cpage = page_id

    def setTargetAddress(self, addr: str):
        self.target_address = addr

    def pageXFile(self, n: int) -> str:
        # return the file path
        return ""

    def pageIFile(self, n: int) -> str:
        # return the file path
        return ""

    def pageBlockscoutTxApi(self,
                            file_path_temp: str,
                            file_path_db: str,
                            q_addr: str,
                            blocknumber: int,
                            count: int) -> bool:
        """
        only applied for blockscout hash transaction apis
        use the browser data and convert the data back
        """
        endpoint = self.underlying_endpoint_base.endpoint
        try:
            with requests.get(
                    f"{endpoint}/address/{q_addr}/transactions",
                    params={
                        "block_number": blocknumber,
                        "id": q_addr,
                        "index": 0,
                        "items_count": count,
                        "type": "JSON",
                    },
                    headers=generate_header(),
                    stream=True
            ) as r:
                r.raise_for_status()
                with open(file_path_temp, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        f.write(chunk)
                with open(file_path_temp, 'r') as y:
                    ywy = json.loads(y.read())

                if "next_page_path" in ywy:
                    content_next = ywy["next_page_path"]
                    items = ywy["items"]
                    if len(items) == 0:
                        print("no more items")
                        return False

                    result_x = self.underlying_endpoint_base.json_blkscout(
                        file_path=file_path_db,
                        html_items=items,
                    )

                    if result_x is True:

                        if content_next is None:
                            print("finished1")
                            return False

                        crt = urlparse(content_next)
                        bl_number = 0
                        address_x = 0
                        cx_count = 0
                        for i in crt.query.split("&"):
                            pair = i.split("=")
                            if pair[0] == "block_number":
                                bl_number = int(pair[1])
                            if pair[0] == "id":
                                address_x = pair[1]
                            if pair[0] == "items_count":
                                cx_count = int(pair[1])

                        return self.pageBlockscoutTxApi(file_path_temp, file_path_db, q_addr, bl_number, cx_count)

        except requests.exceptions.ConnectionError:
            # if the error incurred for the connection problem then try again and wait.
            print("try again in 5 seconds")
            time.sleep(5)
            return self.pageBlockscoutTxApi(file_path_temp, file_path_db, q_addr, blocknumber, count)

    def pageEtherscanTxApi(self, file_path: str, q_addr: str, page: int, pages: int) -> bool:
        """
        only applied for etherscan and related product series.
        use the browser data and convert the data back to the useful data
        """
        endpoint = self.underlying_endpoint_base.endpoint

        with requests.get(f"{endpoint}/txs", params={
            "ps": pages,
            "p": page,
            "a": q_addr,
            "apikey": self.underlying_endpoint_base.api
        }, headers=generate_header(), stream=True) as r:
            r.raise_for_status()
            with open(file_path, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)

            with open(file_path, 'r') as fp:
                return self.underlying_endpoint_base.soup_em(
                    file_path=file_path,
                    soup_base=BeautifulSoup(fp, 'html.parser')
                )

    def pageEtherScanTokenTransferTableApi(self, file_path: str, q_addr: str, page: int) -> bool:
        """
        only applied for etherscan and related product series.
        use the browser data and convert the data back to the useful data
        """
        endpoint = self.underlying_endpoint_base.endpoint
        with requests.get(f"{endpoint}/tokentxns", params={
            "p": page,
            "a": q_addr
        }, headers=generate_header(), stream=True) as r:
            r.raise_for_status()
            with open(file_path, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)

            with open(file_path, 'r') as fp:
                return self.underlying_endpoint_base.soup_em_internal(
                    file_path=file_path,
                    soup_base=BeautifulSoup(fp, 'html.parser')
                )

    def pageEtherscanHolderApi(self, file_path: str, q_addr: str, page: int, addline: any) -> bool:
        """
        only applied for etherscan and related product series.
        use the browser data and convert the data back to the useful data
        """
        endpoint = self.underlying_endpoint_base.endpoint

        total_supply = "100000000000000000000000000"
        with requests.get(f"{endpoint}/token/generic-tokenholders2", params={
            "sid": "",
            "m": "dim",
            "p": page,
            "s": total_supply,
            "a": q_addr,
            "apikey": self.underlying_endpoint_base.api
        }, headers=generate_header(), stream=True) as r:
            r.raise_for_status()
            with open(file_path, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)

            with open(file_path, 'r') as fp:
                return self.underlying_endpoint_base.soup_token_holder(
                    addline=addline,
                    soup_base=BeautifulSoup(fp, 'html.parser')
                )


class ProcessZipper:
    keyword: str

    def process(self, keyword: str):
        self.keyword = keyword


class LargeTransactionQuery(ScannerReq, FolderBase):

    def __init__(self, case_name: str = "excel"):
        self.by_project_name(case_name)
        self.cpage = 1
        self.enable_debug_page_parse = False
        self.target_address = ""
        self.starting_blocknumber = 0
        self.underlying_endpoint_base: SCAN_X = ArbiScan()
        self.hash_file = os.path.join(DATAPATH_BASE, self.excelfolder, "relation_hash.txt")

    def process_blockscout_transaction(self):
        yh_path = os.path.join(DATAPATH_BASE, self.cachefolder, f"x-{self.target_address}-temp.json")
        db_file = self.hash_file

        if os.path.isfile(db_file) and os.path.getsize(db_file) > 10:
            print("-> the relation hash file is already exist.")

        self.pageBlockscoutTxApi(
            file_path_temp=yh_path,
            file_path_db=db_file,
            q_addr=self.target_address,
            blocknumber=self.starting_blocknumber,
            count=50
        )
        self.hash_file = db_file

    def collectHashes(self):
        cvsdb = ReadHash(self.project_name, self.hash_file)
        cvsdb.setFilePath(self.hash_file)
        ep = f"{self.underlying_endpoint_base.endpoint}/api"
        cvsdb.processBlockscoutBaseHashTx2SQL(ep, True)

    def hashCheckRefine(self):
        rehash = ReadHash(self.project_name)
        rehash.setFilePath(self.hash_file)
        _epkl = f"{self.underlying_endpoint_base.endpoint}/api"
        rehash.processRecheckFailedResult(_epkl)

    def pageXFile(self, n: int):
        _file = f"ps-{self.target_address}-{n}.csv"
        return os.path.join(self.cachefolder, _file)

    def pageIFile(self, n: int):
        _file = f"tn-{self.target_address}-{n}.csv"
        return os.path.join(self.cachefolder, _file)

    def process_trns_(self, _f: str = None):
        """
        _f: the tmp file for each page
        """
        try:
            return self.pageEtherscanTxApi(_f, self.target_address, self.cpage, 234)
        except (
                requests.ConnectionError,
                requests.exceptions.ReadTimeout,
                requests.exceptions.Timeout,
                requests.exceptions.HTTPError,
                requests.exceptions.ConnectTimeout,
                AttributeError
        ) as e:
            sleep(3)
            print("some error try again after 3 sec.")
            return self.process_trns_(_f)

    def process_get_internal_transactions(self, _f: str):
        try:
            return self.pageEtherScanTokenTransferTableApi(
                _f,
                self.target_address,
                self.cpage
            )
        except (
                requests.ConnectionError,
                requests.exceptions.ReadTimeout,
                requests.exceptions.Timeout,
                requests.exceptions.HTTPError,
                requests.exceptions.ConnectTimeout,
        ) as e:
            sleep(3)
            print("some error try again after 3 sec.")
            return self.process_get_internal_transactions(_f)

    def retrieve_pages_trx(self):
        h = 0
        self.cpage = 1
        print(self.target_address)
        self.underlying_endpoint_base.setHashRelationCacheFile(self.hash_file)
        while True:

            if self.enable_debug_page_parse is True:
                _f = self.pageXFile(self.cpage)
                if os.path.exists(_f) is False:
                    if self.process_trns_(_f) is True:
                        print(f"query txs page={h} for {self.target_address}", end="\r")
                    else:
                        os.remove(_f)
                        break
            else:
                yh_path = os.path.join(self.cachefolder, f"x-{self.target_address}-temp.json")
                if self.process_trns_(yh_path) is True:
                    print(f"query txs page={h} for {self.target_address}", end="\r")
                else:
                    break

            h += 1
            self.cpage += 1

    def retrieve_pages_internaltrx(self):
        h = 0
        self.cpage = 1
        print(self.target_address)
        while True:
            _f = self.pageIFile(self.cpage)
            if os.path.exists(_f) is False:
                if self.process_get_internal_transactions(_f) is True:
                    print(f"query internal token transaction page={h} for {self.target_address}", end="\r")
                else:
                    os.remove(_f)
                    break
            h += 1
            self.cpage += 1


class BatchScan(FolderBase):
    def __init__(self, case_name: str = "excel"):
        base_folder = f"data/{case_name}"
        base_cache = f"data/{case_name}/cache"
        base_input = f"data/{case_name}/inputs"
        base_mist = f"data/{case_name}/mist"
        base_mist_cache = f"data/{case_name}/mist/cache"
        folder_paths([base_folder, base_cache, base_input, base_mist])
        self.by_project_name(case_name)
        self.tmp = {}
        # -1 incoming, 0 None, 1 outflow
        self.only_flow = 0
        # self.cache = CacheMistApi(self.mistcachefolder)
        self.cache_read = CacheAddressRead(self.cachefolder)
        zip_csv_path = os.path.join(self.cachefolder, 'list_zip_internal.csv')
        self.zip_internal_export = ExportCSV(zip_csv_path)
        self.filter_date = None

    def scan_addresses(self, _file_name: str):
        """
        step 1 scan batch input files from ---
        """
        if readfLock(self.excelfolder, "scan_address") is False:
            setfLock(self.excelfolder, "scan_address", True)
        else:
            print("The process is not finished. or not closed correctly.")
            return

        try:
            path = os.path.join(self.inputfolder, _file_name)
            if os.path.isfile(path) is False:
                print(f"Error the source file {_file_name} is not found")
                return
            f = open(path, "r")
            lines = f.readlines()
            Ltq = LargeTransactionQuery()

            for address in lines:
                address = address.replace("\n", "")
                Ltq.setTargetAddress(address)
                Ltq.retrieve_pages_internaltrx()

        except KeyboardInterrupt:
            setfLock(self.excelfolder, "scan_address", False)
            print("stopped by ctrl c")

        setfLock(self.excelfolder, "scan_address", False)

    def combined_both_worker(self, base: str, tokentrans: str):
        path1 = os.path.join(self.excelfolder, base)
        path2 = os.path.join(self.excelfolder, tokentrans)
        t1 = ReadTxCombined(path1)
        t2 = ReadTokenTxCombined(path2)
        tempfile_internal = ExportCSV(f"{self.excelfolder}/combine_ff.csv")
        t1.crossReferenceFrom(t2, tempfile_internal)

    def callback_large_files_each_line(self, data: list):
        pass

    def callback_large_files_pre_setup(self):
        self.zip_internal_export.clear()

    def callback_large_files_post_setup(self):
        print("job is just completed. fantastic")

    def api_work_scan_hash(self, pro_name: str):
        # basically all the scan hash into the
        if readfLock(self.excelfolder, pro_name) is False:
            setfLock(self.excelfolder, pro_name, True)
        else:
            print("The process is not finished. or not closed correctly.")
            return
        try:
            self.callback_large_files_pre_setup()
            data = self.cache_read.scan_page_fold().address_list
            for l in data:
                self.zip_internal_export.add_line(l)
            self.callback_large_files_post_setup()
        except KeyboardInterrupt:
            setfLock(self.excelfolder, pro_name, False)
            print("stopped by ctrl c")

        setfLock(self.excelfolder, pro_name, False)

    def api_worker_all_dat(self, processing_name: str):
        # basic all to process all the files in cache and put them into a text as the relationship hash file
        if readfLock(self.excelfolder, processing_name) is False:
            setfLock(self.excelfolder, processing_name, True)
        else:
            print("The process is not finished. or not closed correctly.")
            return
        """
         step 2
           [Tx Hash,blockHeight,blockTime(UTC+8),blockTime(UTC),from,to,value,fee,status]
        """
        try:
            self.callback_large_files_pre_setup()
            data = self.cache_read.scan_page_fold().get_lines()
            for l in data:
                self.callback_large_files_each_line(l)
            self.callback_large_files_post_setup()
        except KeyboardInterrupt:
            setfLock(self.excelfolder, processing_name, False)
            print("stopped by ctrl c")

        setfLock(self.excelfolder, processing_name, False)

    def assembly_data(self):
        if readfLock(self.excelfolder, "assembly_data") is False:
            setfLock(self.excelfolder, "assembly_data", True)
        else:
            print("The process is not finished. or not closed correctly.")
            return
        """
         step 2
           [Tx Hash,blockHeight,blockTime(UTC+8),blockTime(UTC),from,to,value,fee,status]
        """
        try:
            self.zip_internal_export.clear()
            data = self.cache_read.scan().get_lines()
            for l in data:
                self.zip_internal_export.add_line(l)
            print("job is just completed. fantastic")
        except KeyboardInterrupt:
            setfLock(self.excelfolder, "assembly_data", False)
            print("stopped by ctrl c")

        setfLock(self.excelfolder, "assembly_data", False)


class ZipLargeQueryResult(BatchScan, ProcessZipper):
    """
    design for solve the problem from
    1. scan relation_hash.txt
    2. each line of the relation hash to get the parent-child info
    3. develop a chart
    """

    def process(self, keyword: str):
        self.pq_keyword = keyword
        self.api_worker_all_dat("zip_large_query_result")

    def callback_large_files_pre_setup(self):
        # setup a relation hash in text file and put all the potential transaction hash into the file
        self.clearCvs('relation_hash.txt')

    def callback_pre_al_hash(self):
        # setup and condense all the hash into one single big file as index.
        self.clearCvs('all_hash.txt')

    def clearCvs(self, file_name_in_tmp: str):
        path = os.path.join(self.excelfolder, file_name_in_tmp)
        self.zip_internal_export = ExportCSV(path)
        self.zip_internal_export.clear()

    def callback_large_files_each_line(self, data: str):
        g = data.split(",")
        eq_hash = g[0]
        pq_method = g[1]
        if pq_method == self.pq_keyword:
            self.zip_internal_export.add_line(
                eq_hash
            )

    def ScanRelationship(self, method_sig: str) -> "ZipLargeQueryResult":
        self.method_sig = method_sig
        return self

    def SlotAddress(self, slot: int) -> "ZipLargeQueryResult":
        self.slot(slot, 'address')

    def slot(self, slot_location: int, type_loc: str):
        pass


class ZipCombineAB(BatchScan, ProcessZipper, LargeTransactionDb):
    def process(self, keyword: str):
        self.init()
        self.response_from_etherscan({
            "sf": "sd"
        })


class TokenHolder(ScannerReq, FolderBase):
    def __init__(self, project: str):
        self.by_project_name(project)

    def pageXFile(self, n: int):
        _file = f"th-{self.target_address}-{n}.csv"
        return os.path.join(self.cachefolder, _file)

    def pageIFile(self, n: int):
        _file = f"th-{self.target_address}-{n}.csv"
        return os.path.join(self.cachefolder, _file)

    def _start_process(self, _f: str, cb):
        try:
            return self.pageEtherscanHolderApi(_f, self.target_address, self.cpage, cb)
        except (
                requests.ConnectionError,
                requests.exceptions.ReadTimeout,
                requests.exceptions.Timeout,
                requests.exceptions.HTTPError,
                requests.exceptions.ConnectTimeout,
                AttributeError
        ) as e:
            sleep(3)
            print("some error try again after 3 sec.")
            return self._start_process(_f, cb)

    def retrieve_pages_token_holders(self):
        h = 0
        self.cpage = 0
        print(self.target_address)
        path = os.path.join(self.excelfolder, "holderinfo.csv")
        tempfile = ExportCSV(path)
        tempfile.clear()

        def add_line_callback(x: str):
            tempfile.add_line(x)

        while True:
            _f = self.pageXFile(self.cpage)
            if os.path.exists(_f) is False:
                if self._start_process(_f, add_line_callback) is True:
                    print(f"query txs page={h} for {self.target_address}", end="\r")
                else:
                    os.remove(_f)
                    break
                os.remove(_f)
            h += 1
            self.cpage += 1
