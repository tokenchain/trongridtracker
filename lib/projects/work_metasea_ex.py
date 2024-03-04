#!/usr/bin/env python3
# coding: utf-8
from lib.common.utils import ReadTokenTxCombined
from lib.common.okapi import AssembleOKLink

ARB20_USDT = "0xFd086bC7CD5C481DCC9C85ebE478A1C0b69FCbb9"
USD_CONTRACT = ARB20_USDT

ARB20_MECC = "0x2C81267e895dB378d539253143C98c77881d399f"
BEP20_CMECC = "0x2C5dfA9DDcE0894f9165c8a97F1Ad5ac0Cfb03aF"
BEP20_DME = "0xEda433aF0566418edB1363FA88C68B8a1b0104A1"
# BEP20_LIM = "0xc994c96a378d144f475a1e12302acf06eec43c1f"
# --- now it works
SEA_POOL3 = "0xde627cded2a7241b1f3679821588db42b62f7699"

# ---- now it is not work
s1 = "0xbfc5f384"
# swapExactTokensForTokensSupportingFeeOnTransferTokens(uint256 amountIn, uint256 amountOutMin, address[] path, address to, uint256 deadline)
s88 = "0x5c11d795"
# swapExactTokensForTokens(uint256 amountIn, uint256 amountOutMin, address[] path, address to, uint256 deadline)
s85 = "0x38ed1739"
# swapExactTokensForETH(uint256 amountIn, uint256 amountOutMin, address[] path, address to, uint256 deadline)
s86 = "0x18cbafe5"
# transfer(address recipient, uint256 amount)
s87 = "0xa9059cbb"

coins = [ARB20_MECC, BEP20_CMECC, BEP20_DME]
pools = [SEA_POOL3]
signatures_call = [s1]
trade_hash = [s88, s85]


class ScanFromCombineReadArb(AssembleOKLink):
    def __init__(self, f: str, case_name: str = "excel"):
        self.readtoken = ReadTokenTxCombined(f"data/{case_name}/{f}")
        super().__init__()
        self.cache.setChain("Arbitrum")

    def captureTransactions(self):
        """
        the step 1 to collect all the transaction in res in the cache folder
        """
        # hashes = self.readtoken.get_hashes()
        data = self.readtoken.get_lines()
        tx_ls = [l.split(",")[0].lower() for l in data]
        while self.cache.check_resync(tx_ls) is False:
            self.cache.fetcher_bundle_hash(tx_ls)

    def action(self):
        self.action_start()
        """
        step 2:
        run the anaylsis program to check all the data related to USD inflow and outflow
        """
        data = self.readtoken.get_lines()
        # tx_ls = [l.split(",")[0].lower() for l in data]
        tx_contract_interaction = []
        tx_trades = []
        tx_cex = []

        for l in data:
            txdetail = l.split(",")
            hx = txdetail[0].lower()
            details, input_data, section = self.get_section_data(hx)
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

        self.action_end()

    # ====================

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

    # =======================

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
        return self.coin_by_listing(coins, input_data)
