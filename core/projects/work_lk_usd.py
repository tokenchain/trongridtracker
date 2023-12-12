# from the blockscout
import os.path

from core.common.utils import ExcelBase, folder_paths, PersonalBank, Stats

LK = "0x7df1cb1f664df30dd1df4893e8018a59a767c2d2"
USDT = "0x10186d85ac0579cb141ff37261f23cf4f1d254b5"
ROUTER = "0xf46f07db79910c2af2f0a1ddaf2d9c39666588f4"

"""
The work progress to process raw data from the blockscout raw data from the db
found the data source from the blockscout explorer server
Now we need to sort the data of LK to USD and find out the trading data
"""


class ExcelExplorer(ExcelBase):
    def __init__(self):
        folder_paths([
            "data/excel",
            "data/excel/cache",
            "data/inputs"
        ])

        self.folder = "data/excel"
        self.folderi = "data/inputs"
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
        self._main_address = ""
        self.edges = 0
        self.use_from = False
        self.use_to = False
        self.is_independence = False
        self.enable_sidenote = False
        self.context_tx = []
        self._sumLines = 0
        self.proc_hash = ""
        self.stats = Stats()
        self.personal: PersonalBank = None

    def check_used_addresses(self, filename: str):
        path_fi = os.path.join(self.folderi, filename)
        file1 = open(path_fi, 'r')
        _lines = file1.readlines()
        _sum = len(_lines)
        self.check_sum_addr = [h.replace("\n", "") for h in _lines]
        self._sumLines = _sum
        print(self.check_sum_addr)
        self.personal = PersonalBank()
        return self

    def read(self):
        path = os.path.join(self.folder, "LK-USDT.xlsx")
        _df = self._readDF(path, "exchange for USDT-LK",
                           [
                               "transaction_hash", "log_index", "from_address_hash",
                               "to_address_hash", "amount", "token_id",
                               "token_contract_address_hash", "inserted_at",
                               "update_at", "block_number", "block_hash",
                               "cumulative_gas_used", "status", "updated_at",
                               "block_number"
                           ])

        hash = []
        txHash = dict()

        for i, row in _df.iterrows():
            th = row["transaction_hash"]
            _from = row["from_address_hash"]
            _to = row["to_address_hash"]
            _contract = row["token_contract_address_hash"]
            _amount = row["amount"]
            _time = row["updated_at"]
            _block_number = row["block_number"]
            _status = row["status"]

            if th not in hash:
                hash.append(th)
                txHash[th] = {
                    "status": _status,
                    "blocknumber": _block_number,
                    "update_time": _time,
                    "line": [],
                }

            txHash[th]["line"].append({
                "contract": _contract,
                "from": _from,
                "to": _to,
                "amount": _amount
            })

            if len(txHash[th]["line"]) == 2:
                self.conclusion(th, _time, txHash[th]["line"])

        self.context_tx = txHash
        if self.personal != None:
            self.personal.conclusion()
        else:
            self.stats.flood()

    def conclusion(self, hash: str, update: str, trns: list):
        self.proc_hash = hash
        if trns[0]["contract"] == LK:
            k1 = trns[0]["amount"] / 10 ** 18
            k2 = trns[1]["amount"] / 10 ** 6
            price = float(k2) / float(k1)
            if self._sumLines > 0:
                self.check_address(trns, f"LK - > USDT SELL,{price},{k1},{k2},{update}")
            else:
                self.stats.set_sell_usdt(hash, k2, price)
                print(f"{hash},LK - > USDT SELL,{price},{k1},{k2},{update}")

        if trns[0]["contract"] == USDT:
            k1 = trns[0]["amount"] / 10 ** 6
            k2 = trns[1]["amount"] / 10 ** 18
            price = float(k1) / float(k2)
            line = f"{hash},USDT - > LK BUY,{price},{k2},{k1},{update}"
            if self._sumLines > 0:
                self.check_address(trns, f"USDT - > LK BUY,{price},{k2},{k1},{update}")
            else:
                print(line)

    def check_address(self, transactions: list, pline: str):
        for op in [transactions[0]["from"],
                   transactions[0]["to"],
                   transactions[1]["from"],
                   transactions[1]["to"]]:
            if op == ROUTER:
                continue
            for y in self.check_sum_addr:
                if op.lower() == y.lower():
                    if transactions[0]["contract"] == USDT:
                        self.personal.set_lk(transactions[1]["amount"] / 10 ** 18)
                        self.personal.set_usdt(transactions[0]["amount"] / 10 ** 6)
                    if transactions[0]["contract"] == LK:
                        self.personal.set_lk(transactions[0]["amount"] / 10 ** 18)
                        self.personal.set_usdt(transactions[1]["amount"] / 10 ** 6)
                        self.personal.set_sell()
                    print(f"Suspects involves in the trade {self.proc_hash} - with wallet address {op} {pline}")
