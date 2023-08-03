#!/usr/bin/env python3
# coding: utf-8
import csv
import asyncio
import glob
import json
import os
from openpyxl.styles import PatternFill
from .lib import build_bot_tpl
import pandas as pd
from pandas import DataFrame
import openpyxl as ox
from .utils import ExcelBase, folder_paths
from .okapi import Cache


class ExcelGraphviz(ExcelBase):
    """
    https://graphviz.org/doc/info/shapes.html

    """

    def __init__(self):
        folder_paths([
            "data/excel",
            "data/excel/cache"
        ])

        self.folder = "data/excel"
        self.cache = Cache("data/excel/cache")
        self.handle_address = ""
        self.metadata = {
            "LINK": {},
            "IDS": {},
            "SUM": {},
            "USE_NODE": [],
            "ADD_LIST": [],
            "block_sheet": None
        }
        self._excel_header = []
        self._excel_file = ""
        self.rendered = False
        self.scope = 500
        self.dot = build_bot_tpl(
            "collection",
            self.scope
        )
        self._main_address = ""
        self.edges = 0
        self.use_from = False
        self.use_to = False
        self.is_independence = False
        self.enable_sidenote = False

    def start_chart(self, filex: str):
        path = os.path.join(self.folder, filex)
        self._excel_factory(path)

    def _excel_factory(self, excel_file: str) -> "ExcelGraphviz":
        SUMMARY_HEAD = [
            # 2         3         4       5        6         7     8          9            10
            "交易时间", "转出地址",
            "转入地址", "姓名", "交易额（LIZ)", "当日收盘价格", "LIZ分配实时价格（USDT）", "当日美元汇率",
            "人民币价格", "hash"
        ]
        BLOCK_SH = ["Tx Hash", "blockHeight"]
        self.setExcelFile(excel_file)
        try:
            _df = self._readDF(excel_file, "summary", SUMMARY_HEAD)
            self.metadata["block_sheet"] = self._readDF(excel_file, "blocks", BLOCK_SH)
            list_sheet = self._sheets(excel_file)
            self.pre_chart()
            for i, row in _df.iterrows():
                self.df_row_first_transactions(row)
            self.post_nodes(list_sheet)
            self.post_chart()

        except FileNotFoundError:
            print("file not found.")

        return self

    def handle_node(self, address: str, liz: int, rmb: int, bh: int):
        if address not in self.metadata["ADD_LIST"]:
            self.metadata["ADD_LIST"].append(address)

        if address not in self.metadata["SUM"]:
            self.metadata["SUM"][address] = {"liz": 0, "rmb": 0, "last_bh": 0, "usdt": 0, "sold_token": 0}

        self.metadata["SUM"][address]["liz"] += liz
        self.metadata["SUM"][address]["rmb"] += rmb
        self.metadata["SUM"][address]["usdt"] = 0
        self.metadata["SUM"][address]["sold_token"] = 0
        # get the last block height
        # if self.metadata["SUM"][address]["last_bh"] < bh:
        # save the earliest block height
        if self.metadata["SUM"][address]["last_bh"] == 0:
            self.metadata["SUM"][address]["last_bh"] = bh
        elif bh < self.metadata["SUM"][address]["last_bh"]:
            self.metadata["SUM"][address]["last_bh"] = bh

    def post_nodes(self, list_sheet: list):
        """
        shape ref: https://graphviz.org/doc/info/shapes.html
        """
        fillcolor = "lightcoral:#ff880022"
        ob = {
            "shape": "Mcircle",
            "fillcolor": "#ff880022",
            "fontcolor": "darkslategrey",
            "label": "box",
        }
        ob2 = {
            "shape": "Mdiamond",
            "shapec": "Mcircle",
            "fillcolor": "#ff880022",
            "fontcolor": "darkslategrey",
        }

        first_node = "任见红非法所得|从 2021/5/2 18:05 - 2022/7/9 16:35|共 169,267 Liz|0xdd31d81fe923713f3cc1c6b7546997696da747c4"
        first_node = first_node.replace("|", "\n")
        origin = "0xdd31d81fe923713f3cc1c6b7546997696da747c4"
        usdt_get = 0

        temp = self.metadata["ADD_LIST"]

        for yh in temp:
            if yh[:3] == "dev":
                continue
            lastbh = self.metadata["SUM"][yh]["last_bh"]
            self.proc_node_address(yh, list_sheet, lastbh)

        for dev_x in self.metadata["ADD_LIST"]:
            if self.is_dev(dev_x):
                x = self.deiv_back_addr(dev_x)
                # print(x, self.metadata["SUM"][x])

                sold = self.metadata["SUM"][x]["sold_token"]
                usdt = self.metadata["SUM"][x]["usdt"]

                usdt = f"Gain +{usdt:,.2f} USDT 💵"
                sold = f"Sold -{sold:,.2f} LIZ"

                label_x = f"DEX Transactions Summary|{sold}|{usdt}|{x}"
                label_x = label_x.replace("|", "\n")

                self.dot.node(
                    dev_x,
                    shape=ob2["shape"],
                    fillcolor=ob2["fillcolor"],
                    style="filled",
                    fontcolor=ob2["fontcolor"],
                    # gradientangle="270",
                    label=label_x
                )
            else:
                original_address = dev_x
                liz = self.metadata["SUM"][original_address]["liz"]
                gain_liz = f"共 +{liz:,.2f} LIZ 获得"
                label_x = f"{gain_liz}|{original_address}"
                label_x = label_x.replace("|", "\n")
                self.dot.node(
                    original_address,
                    shape=ob["shape"],
                    fillcolor=ob["fillcolor"],
                    style="filled",
                    fontcolor=ob["fontcolor"],
                    # gradientangle="270",
                    label=label_x
                )
                usdt_get += self.metadata["SUM"][original_address]["usdt"]

            self.dot.node(
                origin,
                shape="star",
                fillcolor=ob["fillcolor"],
                style="filled",
                fontcolor=ob["fontcolor"],
                gradientangle="270",
                label=first_node
            )

            gain_usd = f"共 +{usdt_get:,.2f} USDT 获得"
            end_node = f"任见红非法所得|从 2021/5/2 18:05 - 2022/7/9 16:35|{gain_usd}"
            end_node = end_node.replace("|", "\n")
            self.dot.node(
                "ending",
                shape="star",
                fillcolor=ob["fillcolor"],
                style="filled",
                fontcolor=ob["fontcolor"],
                gradientangle="270",
                label=end_node
            )

    def checkMethodAllow(self, method) -> bool:
        if method.strip() == "swapExactTokensForTokensSupportingFeeOnTransferTokens":
            return True
        if method.strip() == "swapExactTokensForTokens":
            return True
        return False

    def proc_node_address(self, x: str, sheets: list, last_bh: int):
        sheet = self.find_sheet(x, sheets)
        if sheet == "":
            print(f"This address {x} is not found in sheets")
            return
        _df = self._get_sheet(
            sheet, ["Tx Hash", "blockHeight", "blockTime(UTC+8)", "blockTime(UTC)", "from", "to", "status"]
        )
        for i, row in _df.iterrows():
            bh = int(row["blockHeight"])
            amountliz = 0
            amountusdt = 0
            if bh > last_bh:
                hash = row["Tx Hash"]
                method = row["status"]
                if self.checkMethodAllow(method) is False:
                    continue

                print(f"dex transaction from {x} - {hash}")
                dat = self.cache.cache_transaction_get(hash)

                if "code" in dat and int(dat["code"]) > 0:
                    print(f"error from code {dat['code']}")
                    return

                if "data" in dat and len(dat['data']) >= 1:
                    for section in dat['data']:
                        if "tokenTransferDetails" in section:
                            details = section['tokenTransferDetails']
                            for token in details:
                                if token['tokenContractAddress'] == "0xfcb520b47f5601031e0eb316f553a3641ff4b13c":
                                    amountliz = float(token['amount'])
                                if token['tokenContractAddress'] == "0x55d398326f99059ff775485246999027b3197955":
                                    amountusdt = float(token['amount'])

                            if amountliz > 0 and amountusdt > 0:
                                self.df_row_second_level_dex(section, x, amountliz, amountusdt)

        # token_f = self.metadata["SUM"][x]["sold_token"]
        # print(f"total coins - {token_f}")

    def pre_chart(self):
        text = f"下图显示了所有被 XX 或以下忽略的记录交易"
        with self.dot.subgraph(name='legend') as c:
            c.attr(color='blue')
            c.node_attr['style'] = 'filled'
            c.attr(label=text)

    def get_block_height(self, hash: str) -> int:
        _df = self.metadata["block_sheet"]
        for i, row in _df.iterrows():
            if row["Tx Hash"] == hash:
                bh = int(row["blockHeight"])

                return bh

        return 0

    def deiv_address(self, x: str) -> str:
        return f"devi_{x}"

    def is_dev(self, x: str) -> bool:
        return True if "devi_" in x else False

    def deiv_back_addr(self, fx: str) -> str:
        fx = fx.replace("devi_", "")
        return fx

    def df_row_second_level_dex(self, dat: dict, x: str, tokenA: float, tokenB: float):
        txid = dat["txid"]
        bh = dat["height"]

        print(f"work on {x} - {tokenA}, {tokenB}")
        self.metadata["SUM"][x]["sold_token"] += tokenA
        self.metadata["SUM"][x]["usdt"] += tokenB

        to_dest = self.deiv_address(x)

        tokenB = f"{tokenB:,.2f} USDT"
        tokenA = f"{tokenA:,.2f} LIZ"

        _label = f"{tokenA} -> {tokenB}|TX:{txid}|Block Height:{bh}"
        _label = _label.replace("|", "\n")
        _color = "green"

        self.dot.edge(
            x,
            to_dest,
            color=_color,
            label=_label,
            labeldistance='1.2',
            labelangle='30',
        )

        self.dot.edge(
            to_dest,
            "ending",
            color="red",
            labeldistance='1.2',
            labelangle='30',
        )

        self.edges += 2

        if to_dest not in self.metadata["ADD_LIST"]:
            self.metadata["ADD_LIST"].append(to_dest)

    def df_row_first_transactions(self, dfrow: dict):
        date = dfrow["交易时间"]
        add_from = dfrow["转出地址"]
        to_from = dfrow["转入地址"]
        amount_liz = int(dfrow["交易额（LIZ)"])
        rmb_sum = int(dfrow["人民币价格"])
        hash = dfrow["hash"]
        _color = "blue"

        self.handle_node(to_from, amount_liz, rmb_sum, self.get_block_height(hash))

        rmb_sum = f"{rmb_sum:,.2f} rmb"
        amount_liz = f"{amount_liz:,.2f} liz"
        _label = f"{amount_liz}#{date}#TX:{hash}"
        _label = _label.replace("#", "\n")

        self.dot.edge(
            tail_name=add_from,
            head_name=to_from,
            color=_color,
            label=_label,
            labeldistance='1.2',
            labelangle='60',
        )

        self.edges += 1

    def post_chart(self):
        self.dot.render(
            filename=f"LiZ-rel.{self.edges}",
            directory='data/charts').replace('\\', '/')
