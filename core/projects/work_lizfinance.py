#!/usr/bin/env python3
# coding: utf-8
import os
from typing import Tuple
from .lib import build_bot_tpl
from core.common.utils import ExcelBase, folder_paths, ExportCSV, ReadTokenTxCombined
from core.common.okapi import Cache, AssembleOKLink

BEP20_USDT = "0x55d398326f99059ff775485246999027b3197955"
USD_CONTRACT = BEP20_USDT
BEP20_LIZ = "0xfcb520b47f5601031e0eb316f553a3641ff4b13c"
BEP20_LIT = "0xB88911bEE18BB8D2168d185B9A42E56704d821F8"
BEP20_LIB = "0xd91efaae19836f13e2035543576c363d6ed06239"
BEP20_LIM = "0xc994c96a378d144f475a1e12302acf06eec43c1f"
"""
From the above calculations we are based on these factors, that we assume to have the following coins purchased with USDT:
BEP20_LIZ : 0xfcb520b47f5601031e0eb316f553a3641ff4b13c
BEP20_LIT : 0xB88911bEE18BB8D2168d185B9A42E56704d821F8
BEP20_LIB : 0xd91efaae19836f13e2035543576c363d6ed06239
BEP20_LIM : 0xc994c96a378d144f475a1e12302acf06eec43c1f

Investment interaction from spending USDT with the below pools:
LIZ_POOL : 0x714d0260317f73805d5babf56c647433105b6c36
LIZ_POOL2 : 0xA88C636894e7340254E1352439903830b0E492cc
LIZ_POOL3 : 0xd5be574bfbe7974a2abd8080da2880d652798373
LIZ_POOL4 : 0x2539f1d49e90c7441eeb618f90702b7a80a9a019
LIZ_POOL5 : 0xa0c3d93bc79fae77f408d3c65fc74d73ebfc4033
LIZ_POOL6 : 0xf68850b0bb13975b5dc8f4ce44fa4ffb5597b9b1
LIZ_POOL7 : 0xfb8c2a4b05ffe28a13166050d2625f687a026363
LIZ_POOL8 : 0xcb2cbfbdfaef20e89db8855a08929e9dc8a2c6df

The transfer on-chain interaction is filtered by the contract USDT, we are looking into the receiver of the usdt and decide rather the money is recognized as income or expenses.

"""
# --- now it works
LIZ_POOL = "0x714d0260317f73805d5babf56c647433105b6c36"
LIZ_POOL2 = "0xA88C636894e7340254E1352439903830b0E492cc"
LIZ_POOL3 = "0xd5be574bfbe7974a2abd8080da2880d652798373"
LIZ_POOL4 = "0x2539f1d49e90c7441eeb618f90702b7a80a9a019"
LIZ_POOL5 = "0xa0c3d93bc79fae77f408d3c65fc74d73ebfc4033"
LIZ_POOL6 = "0xf68850b0bb13975b5dc8f4ce44fa4ffb5597b9b1"
LIZ_POOL7 = "0xfb8c2a4b05ffe28a13166050d2625f687a026363"
LIZ_POOL8 = "0xcb2cbfbdfaef20e89db8855a08929e9dc8a2c6df"

# ---- now it is not work
s1 = "0x61b761d5"
s2 = "0xe2550d63"
# stake
s3 = "0xdc9031c4"
s4 = "0x53cfc9a7"
s5 = "0xb7fd3001"
s6 = "0xa4441df5"
s7 = "0x8dd06adc"
s8 = "0xe8dbbc5b"
s9 = "0x12d94235"

# swapExactTokensForTokensSupportingFeeOnTransferTokens(uint256 amountIn, uint256 amountOutMin, address[] path, address to, uint256 deadline)
s88 = "0x5c11d795"
# swapExactTokensForTokens(uint256 amountIn, uint256 amountOutMin, address[] path, address to, uint256 deadline)
s85 = "0x38ed1739"
# swapExactTokensForETH(uint256 amountIn, uint256 amountOutMin, address[] path, address to, uint256 deadline)
s86 = "0x18cbafe5"
# transfer(address recipient, uint256 amount)
s87 = "0xa9059cbb"

coins = [BEP20_LIZ, BEP20_LIT, BEP20_LIB, BEP20_LIM]
pools = [LIZ_POOL, LIZ_POOL2, LIZ_POOL3, LIZ_POOL4, LIZ_POOL5, LIZ_POOL6, LIZ_POOL7, LIZ_POOL8]
signatures_call = [s1, s2, s3, s4, s5, s6, s7]
trade_hash = [s88, s85]
trade_calls = ["swapExactTokensForTokens", "swapExactTokensForTokensSupportingFeeOnTransferTokens"]


class ScanFromCombineRead(AssembleOKLink):
    def __init__(self, f: str):
        self.readtoken = ReadTokenTxCombined(f"data/excel/{f}")
        super().__init__()

    def captureTransactions(self):
        # hashes = self.readtoken.get_hashes()
        data = self.readtoken.get_lines()
        for l in data:
            txdetail = l.split(",")
            xfrom = txdetail[2].lower()
            xto = txdetail[3].lower()
            hash = txdetail[0]
            self.cache.cache_transaction_get(hash)


class ScanFolderOk(AssembleOKLink):
    def action(self):
        data = self.cache_read.scan().get_lines()
        tx_ls = [l.split(",")[0].lower() for l in data]
        self.cache.fetcher_bundle_hash(tx_ls)

        tx_contract_interaction = []
        tx_trades = []
        tx_cex = []

        for l in data:
            txdetail = l.split(",")
            hx = txdetail[0].lower()
            details, input_data, section = self.get_section_data(hx)
            for token in details:
                pass

            xto = txdetail[5].lower()

            if self.contract_interaction_check(xto):
                tx_contract_interaction.append(hx)
                continue

            if self.tradable_check(input_data):
                tx_trades.append(hx)
                continue

            if self.transfer_check(input_data):
                tx_cex.append(hx)
                continue

        print("A) total tx_contract_interaction tx- ", len(tx_contract_interaction))
        print("B) total tx_trades tx- ", len(tx_trades))
        print("C) total tx_cex tx- ", len(tx_cex))

        for ef in tx_contract_interaction:
            self.staking_invest(ef)

        for rf in tx_trades:
            self.swapTypes(rf)

        for f in tx_cex:
            self.cexTypes(f)

        print(f"1. Investing USDT {self.usdt_invest}")
        print(f"2. Transfer to CEX or Others {self.usdt_to_cex}")
        print(f"3. Transfer from other to list {self.usdt_from_other}")
        print(f"4. BUY coin {self.usdt_in}")
        print(f"5. SELL coin {self.usdt_out}")

    def cexTypes(self, hash: str):
        """
        transfer to the cex type
        """
        details, input_data, section = self.get_section_data(hash)
        for token in details:
            if token['tokenContractAddress'] == USD_CONTRACT:
                to_address = token['to']
                kamount = float(token['amount'])
                if self.check_address_in_list(to_address) is True:
                    self.usdt_from_other += kamount
                else:
                    self.usdt_to_cex += kamount

    def swapTypes(self, hash: str):
        amountliz = 0
        amountusdt = 0
        details, input_data, section = self.get_section_data(hash)
        for token in details:
            if token['tokenContractAddress'] == USD_CONTRACT:
                amountusdt = float(token['amount'])

            if self.contract_coincheck(token['tokenContractAddress']) is True:
                amountliz = float(token['amount'])

        if amountusdt > 0 and amountliz > 0:
            p1 = input_data.find(USD_CONTRACT[2:])
            p2 = self.coin_position(input_data)
            # p2 = input_data.find(BEP20_LIZ[2:])
            # print("sold", p1, p2)
            if p1 > p2:
                # sold for usd
                # self.df_row_second_level_dex2(section, amountliz, amountusdt)
                self.usdt_out += amountusdt
            else:
                self.usdt_in += amountusdt
                # self.df_row_second_level_dex1(section, amountliz, amountusdt)

    def staking_invest(self, hash: str):
        amountusdt = 0
        details, input_data, section = self.get_section_data(hash)
        if self.signature_checks(input_data) is True:
            for token in details:
                if token['tokenContractAddress'] == USD_CONTRACT:
                    if self.contract_interaction_check(token['to']) is True:
                        amountusdt = float(token['amount'])

            if amountusdt > 0:
                # print("staking or invest")
                self.df_staking_count(section, amountusdt)

    def check_address_in_list(self, addr: str) -> bool:
        for n in self.cache_read.get_wallet_addresses():
            if n == addr:
                return True
        return False

    def method_call_checks(self, method_signature: str) -> bool:
        for h in trade_calls:
            if method_signature.lower() == h.lower():
                return True
        return False

    def transfer_check(self, data_input: str) -> bool:
        return self.sign_checker_0x([s87], data_input)

    def tradable_check(self, data_input: str) -> bool:
        return self.sign_checker_0x(trade_hash, data_input)

    def signature_checks(self, data_input: str) -> bool:
        return self.sign_checker_0x(signatures_call, data_input)

    def contract_coincheck(self, coin_contract: str) -> bool:
        for h in coins:
            if coin_contract.lower() == h.lower():
                return True
        return False

    def contract_interaction_check(self, input: str) -> bool:
        for h in pools:
            if input == h.lower():
                return True
        return False

    def coin_position(self, input_data: str) -> int:
        for b in coins:
            s = input_data.find(b[2:])
            if s > 0:
                return s
        return 0

    def df_staking_count(self, dat: dict, tokenB: float):
        txid = dat["txid"]
        bh = dat["height"]
        sig = dat["inputData"][:10]
        # print(f"STAKE tx {sig} {txid} block height {bh}->  {tokenB}")
        self.usdt_invest += tokenB


class ExcelGraphviz(ExcelBase):
    """
    building the graph to render the images to give all the data to show it.
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
