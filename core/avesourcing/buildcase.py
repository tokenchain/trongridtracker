#!/usr/bin/env python3
# coding: utf-8
import glob
import json

from core.common.okapi import CacheLite
from core.common.utils import FolderBase, ReadCombinedFile, find_key
from core.etherscan.sqlc.sqlhelper import LargeCacheTransferToDb
from core.graphz.mistapi import MistAcquireDat, enable_BNB


class CaseBuilder(FolderBase):
    def __init__(self, project: str = "AVE.SOURCE"):
        self.by_project_name(project)
        self.handle_address = ""
        self.rendered = False
        self.scope = 500
        self._main_address = ""
        self.edges = 0
        self.use_from = False
        self.use_to = False
        self.is_independence = False
        self.enable_sidenote = False
        self.api = MistAcquireDat(project)
        self.lp = LargeCacheTransferToDb(self.project_name)
        self.cachelite = CacheLite(self.cachefolder, self.project_name)
        self.api.folder = self.mist_folder
        self.api.inputfolder = self.inputfolder
        self.project_name = project
        self.meta_bank = {}
        self.meta_label = {}
        self.check_hashes = []

    def exchange_tracer(self, from_project_deposit: str):
        enable_BNB()
        file_x = self.api.getFile(from_project_deposit)
        self.process_address2(file_x)

    def process_address2(self, file: str):
        self.processHashes(True)

    def process_address(self, file: str):
        with open(file, newline='') as f:
            self.rf = json.loads(f.read())
        nodes = self.rf["graph_dic"]["node_list"]
        edges = self.rf["graph_dic"]["edge_list"]
        for v in nodes:
            _id = v["id"]
            _add = v["addr"]
            _lab = v["addr"]
            if "shape" in v:
                _shape = v["shape"]
            else:
                _shape = "box"
            if "..." in v["label"]:
                _lab = v["addr"]
                print(f"label in {_lab} {v['label']}")
            else:
                _lab = f"[{v['label']}]\n{v['addr']}"
                if "star" in _shape:
                    # side_note = self.api.overview(_add)
                    # _lab = _lab + side_note
                    print(f"label in start -> ... ")

                self.meta_bank[_id] = _add
                self.meta_label[_id] = _lab

        for h in edges:
            if h["from"] in self.meta_bank:
                _id = h["from"]
                tx_list_po = h["tx_hash_list"]
                address = self.meta_bank[_id]
                label = self.meta_label[_id]
                print(f"address is {address} from {label}")
                self.append_tx(tx_list_po)
        self.processHashes(True)
        for h in edges:
            if h["from"] in self.meta_bank:
                _id = h["from"]
                tx_list_po = h["tx_hash_list"]
                address = self.meta_bank[_id]
                label = self.meta_label[_id]
                if label is not None:
                    print(f"address is {address} from {label}")
                    self.append_tx(tx_list_po)

    def processHashes(self, newdb: bool):
        if newdb is True and self.lp.isDbExist() is False:
            self.lp.newTable()
        tx_ls =  self.check_hashes
        while self.cachelite.check_resync(tx_ls) is False:
            self.cachelite.fetcher_bundle_hash(tx_ls)



    def append_tx(self, tx_list):
        for xx in tx_list:
            self.check_hashes.append(xx)
