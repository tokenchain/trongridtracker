#!/usr/bin/env python
# coding: utf-8
from lib import USDTApp, CustomToken, Analysis

scan_on_address = "...."


def line_one_line():
    USDTApp().CollectionTransactionFromTronForUSDT(scan_on_address)
    Analysis().start(scan_on_address)


def only_read():
    Analysis().start(scan_on_address)


if __name__ == '__main__':
    only_read()
