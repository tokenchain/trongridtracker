#!/usr/bin/env python3
import os.path

from lib.common.blockscout import ReqDatBlockScout
from lib.common.okapi import Cache, CacheLite
from lib.common.utils import FolderBase, ReadCombinedFile, ExportCSV
from lib.etherscan.sqlc.sqlhelper import LargeCacheTransferToDb
from lib.solver.contract_solver import solve_possible_call


class ReadHash(FolderBase):
    def __init__(self, project: str, file_name: str = 'relation_hash.txt'):
        self.by_project_name(project)
        relation_hash = os.path.join(self.excelfolder, file_name)
        self.cache = Cache(self.cachefolder)
        self.cache_db = CacheLite(self.cachefolder, project)
        self.read_files = ReadCombinedFile(relation_hash)
        self.lp = LargeCacheTransferToDb(self.project_name)

    def setFilePath(self, path_reset: str):
        self.cache = Cache(self.cachefolder)
        self.cache_db = CacheLite(self.cachefolder, self.project_name)
        self.read_files = ReadCombinedFile(path_reset)

    def processCacheDB(self):
        # process cache db for relations from each line of hash in the hash file
        self.cache_db.setRestart(self.processCacheDB)
        hashes = self.read_files.get_lines()
        while self.cache_db.check_resync(hashes) is False:
            self.cache_db.fetcher_bundle_hash(hashes)

    def processCacheFiles(self):
        hashes = self.read_files.get_lines()
        print(len(hashes))
        while self.cache.check_resync(hashes) is False:
            self.cache.fetcher_bundle_hash(hashes)

    def processBlockscoutBaseHashTx2SQL(self, apibasepoint: str, use_new_db: bool = False):
        """
        1. find the relation hash file
        2. loop for the hashes
        3. request the hashes from the given rpc or url.
        """
        hashes = self.read_files.get_hashes()
        blockscoutReq = ReqDatBlockScout()
        blockscoutReq.setBase(apibasepoint)

        if use_new_db is True and self.lp.isDbExist() is False:
            self.lp.newTable()

        print(f"Total hashes found {len(hashes)}")

        for x in hashes:
            if x[0:2] == "0x":
                if self.lp.find_in_cache(x) is False:
                    blockscoutReq.getHashTxAsDoc(x)
                    dat = blockscoutReq.result
                    self.lp.process(x, dat)

    def processRecheckFailedResult(self, apibasepoint: str):
        """
        1. check the failed json result
        2. fix the problem
        3. request the hashes from the given rpc or url.
        """
        hashes = self.read_files.get_hashes()
        blockscoutReq = ReqDatBlockScout()
        blockscoutReq.setBase(apibasepoint)
        for x in hashes:
            if x[0:2] == "0x":
                json_keep = self.lp.get_in_hash(x)
                if "status" not in json_keep:
                    
                    blockscoutReq.getHashTxAsDoc(x)
                    # dat = blockscoutReq.result
                    self.lp.processUpdate(x, blockscoutReq.result)

                elif json_keep["status"] == "0":
                    blockscoutReq.getHashTx(x)
                    if blockscoutReq.result["status"] == "0":
                        print(f"fail to get info again {x}")
                    else:
                        blockscoutReq.loadResAsDoc()
                        self.lp.processUpdate(x, blockscoutReq.result)

    def processTransferToSqlLite(self, newdb: bool = False):
        """
        1. read the relation file from the [relation_hash.txt]
        2. loop for the hashes and save them into the sqllite db
        """
        hashes = self.read_files.get_lines()
        if newdb is True:
            self.lp.newTable()
        for h in hashes:
            if self.cache.check_cache_validate(h) is True:
                dat_text = self.cache.cache_transaction_get_text(h)
                if dat_text == "":
                    print(".skip")
                    continue
                self.lp.process(h, dat_text)

        print("the data transfer is now done.")

    def processTransferRawToSqlLite(self, newdb: bool = False):
        """
        1. scan all files from the cache folder
        2. look for the hash tx result files
        3. read the correct hash and save them into the local sqllite db
        """
        hashes = self.cache.scan_all_files()

        if newdb is True:
            self.lp.newTable()
        for h in hashes:
            if self.cache.check_cache_validate(h) is True:
                dat_text = self.cache.cache_transaction_get_text(h)
                if dat_text == "":
                    print(".skip")
                    continue
                self.lp.process(h, dat_text)

        print("the data transfer is now done.")


def solve_possible_call(payload_methods: str, method_id: str, input_hex: str, hash: str) -> str:
    input_hex = input_hex.strip().replace("\n", "")
    name_call = input_hex[:10]
    value_call_ux = input_hex[10:len(input_hex)]
    x_inputs = len(value_call_ux) / 64

    address_get = ''
    if name_call.lower() != method_id.lower():
        raise Exception("method id not matched.")

    if int(x_inputs) == 0:
        print("there is no input", input_hex, hash)
    else:

        for i in range(int(x_inputs)):
            c = value_call_ux[i * 64:(i + 1) * 64]
            last_c = len(c)
            if payload_methods == 'address' or len(c.lstrip("0")) <= 40 and len(c.lstrip("0")) > 35:
                address_get = "0x" + c[64 - 40: last_c]
                # print(f"possible address {c}")
                break
    return address_get


class NetworkRelFromCacheRes(FolderBase):
    def __init__(self, project: str):
        self.by_project_name(project)
        self.cache_db = CacheLite(self.cachefolder, project)
        relation_hashes = os.path.join(self.excelfolder, 'relation_hash.txt')
        relation = os.path.join(self.excelfolder, 'relation.txt')
        self.zipped_file = ExportCSV(relation)
        self.read_files = ReadCombinedFile(relation_hashes)
        self.method_id = ''

    def processRelationOklinkTxs(self, method_id: str):
        """
        1. clear the files from zipped file
        2. read the given hash and read by the oklink hash result format
        """
        self.zipped_file.clear()
        self.method_id = method_id
        for u in self.read_files.get_lines():
            data = self.cache_db.cache_transaction_get(u)
            self.add_relation_from_oklink(data)

    def processRelationBlockscoutTxs(self, method_id: str):
        """
        1. clear the files from zipped file
        2. read the given hash and read by the blockscout hash result format
        """
        self.zipped_file.clear()
        self.method_id = method_id
        for u in self.read_files.get_lines():
            data = self.cache_db.cache_transaction_get(u)
            self.add_relation_from_blocksout_tx_format(data)

    def add_relation_from_blocksout_tx_format(self, tx: str):
        if isinstance(tx, dict) and "result" in tx:
            data_set = tx["result"]
            if "input" in data_set:
                input_line = data_set["input"]
                child = data_set["from"]
                try:
                    parent = solve_possible_call("address", self.method_id, input_line, tx)
                except Exception as e:
                    print(e)
                    return
                self.zipped_file.add_line(f"{child} - {parent}")

        else:
            print("wrong type")

    def add_relation_from_oklink(self, tx: any):
        if isinstance(tx, dict) and "data" in tx:

            data_set = tx["data"]
            for data_needle in data_set:
                child = data_needle["inputDetails"][0]["inputHash"]
                payload = data_needle["inputData"]
                trans_id = data_needle["txid"]
                try:
                    parent = solve_possible_call("address", self.method_id, payload, trans_id)
                except Exception as e:
                    print(e)
                    return
                self.zipped_file.add_line(f"{child} - {parent}")

        else:
            print("wrong type")
