# from the blockscout
import os.path

from lib.common.utils import folder_paths
from lib.common.okapi import Cache, CacheAddressRead, AddressIncomeExpenses, get_csv_token_history

USDT = "0x55d398326f99059ff775485246999027b3197955"
LINA = "0x762539b45a1dcce3d36d080f74d1aed37844b878"


class LinaFolder:
    def __init__(self):
        folder_paths([
            "data/tokenscan",
            "data/tokenscan/cache",
            "data/tokenscan/tokentransfer",
            "data/inputs"
        ])
        self.cache_read = CacheAddressRead("data/tokenscan/cache")
        self.cache_read_t = CacheAddressRead("data/tokenscan/tokentransfer")
        self.cache = Cache("data/tokenscan/cache")
        self.usdt_in = 0
        self.usdt_out = 0
        self.usdt_invest = 0
        self.usdt_cex = 0
        self.find_usd_output = False
        self.counter_list = []

    def scan_addresses_income(self, cc: AddressIncomeExpenses):
        flist = cc.list_incomes_addresses()
        for b in flist:
            path = f"data/tokenscan/tokentransfer/income-{b}.csv"
            if os.path.isfile(path) is False:
                get_csv_token_history(path, b, "BSC")

    def scan_addresses_expense(self, cc: AddressIncomeExpenses):
        flist = cc.list_expenses_addresses()
        for b in flist:
            path = f"data/tokenscan/tokentransfer/expense-{b}.csv"
            if os.path.isfile(path) is False:
                get_csv_token_history(path, b, "BSC")

    def aggregrate_usd(self, xfrom: str, xto: str, contract: str, value: float):
        if contract != LINA:
            return

        for g in self.counter_list:
            if g["address"] == xfrom:
                count: AddressIncomeExpenses = g["count"]
                count.expense_hit(xto, value)

            if g["address"] == xto:
                count: AddressIncomeExpenses = g["count"]
                count.income_hit(xto, value)

    def sum_up_expense(self, cc: AddressIncomeExpenses):
        explist = cc.list_expenses_addresses()
        self.sum_up(explist)

    def sum_up_income(self, cc: AddressIncomeExpenses):
        explist = cc.list_incomes_addresses()
        self.sum_up(explist)

    def sum_up(self, explist: list):
        flist = self.cache_read_t.scan().get_lines()
        self.counter_list = [{
            "address": h,
            "count": AddressIncomeExpenses(LINA, h)
        } for h in explist]
        for l in flist:
            txdetail = l.split(",")
            xfrom = txdetail[4].lower()
            xto = txdetail[5].lower()
            value = float(txdetail[6])
            contract = txdetail[8].lower()
            self.aggregrate_usd(xfrom, xto, contract, value)
        for l in self.counter_list:
            ycount: AddressIncomeExpenses = l["count"]
            ycount.print("LINA")

        self.layer2sum([l['count'] for l in self.counter_list], "LINA")

    def layer2sum(self, lisof: list, token_name: str):
        ffexpense = 0
        ffincome = 0
        for yc in lisof:
            ffexpense += yc.full_expense
            ffincome += yc.full_income
        print("======================================")
        print(f"data from the above")
        print(f"total expense: {ffexpense} {token_name}")
        print(f"total income: {ffincome} {token_name}")

    def action(self, token_addr: str, chase_address: str):
        counter = AddressIncomeExpenses(token_addr, chase_address)
        """
           [Tx Hash,blockHeight,blockTime(UTC+8),blockTime(UTC),from,to,value,fee,status]
        """
        data = self.cache_read.scan().get_lines()

        for l in data:
            txdetail = l.split(",")
            xfrom = txdetail[4].lower()
            xto = txdetail[5].lower()
            value = float(txdetail[6])
            symbol = txdetail[8].lower()

            if symbol == token_addr:
                if xfrom == chase_address:
                    counter.expense_hit(xto, value)
                else:
                    counter.income_hit(xfrom, value)

        counter.print("LINA")
        # counter.print_address()
        self.scan_addresses_income(counter)
        self.scan_addresses_expense(counter)
        self.sum_up_expense(counter)
        self.sum_up_income(counter)
