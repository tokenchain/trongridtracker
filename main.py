#!/usr/bin/env python
# coding: utf-8
from lib import USDTApp, SubLayerAnalysis, Analysis


def line_one_line(t: str):
    # USDTApp().CollectionTransactionFromTronForUSDT(t)
    Analysis().start(t)
    SubLayerAnalysis().start(t)


def only_read(f: str):
    Analysis().start(f)


def local_analysis():
    Analysis().handle_history()


if __name__ == '__main__':
    # scan_on_address = input("please enter the tron wallet address: ")
    # line_one_line(scan_on_address)
    local_analysis()
