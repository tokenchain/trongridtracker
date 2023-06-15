#!/usr/bin/env python
# coding: utf-8
from core.lib import USDTApp, SubLayerAnalysis, Analysis


def line_one_line(t: str):
    USDTApp().CollectionTransactionFromTronForUSDT(t)
    Analysis().start(t)
    SubLayerAnalysis().start(t)


def just_this(t: str):
    USDTApp().CollectionTransactionFromTronForUSDT(t)
    Analysis().start(t)


def only_read(f: str):
    Analysis().start(f)

def local_analysis():
    Analysis().handle_history()


def fill_reports():
    SubLayerAnalysis().fillReport()


def oklinkimport():
    USDTApp().CollectionOKLinkUSDT()
    Analysis().handle_history()


if __name__ == '__main__':
    scan_on_address = input("please enter the tron wallet address: ")
    USDTApp().getOKLinkFile(scan_on_address)
    oklinkimport()
    # just_this(scan_on_address)
    # line_one_line(scan_on_address)
    # fill_reports()
    # local_analysis()
