#!/usr/bin/env python
# coding: utf-8
from lib import USDTApp, CustomToken, Analysis

def line_one_line():
    # r = CustomToken().CheckTokenHolderAddress("TVddDhyFbFnq75S93Jydn4ueVD1B2zKoei", 6)
    # addresspool="TVddDhyFbFnq75S93Jydn4ueVD1B2zKoei"
    # addresspool="TDEz41eiEBE8LSjB2UvGNt2hkqmafhKX4Y"
    scan_on_address = "TS2zT9XRqpD6ZU7GGGPBZMWhJrfFdr2KVM"
    USDTApp().CollectionTransactionFromTronForUSDT(scan_on_address)
    Analysis().start(scan_on_address)


def only_read():
    scan_on_address = "TS2zT9XRqpD6ZU7GGGPBZMWhJrfFdr2KVM"
    Analysis().start(scan_on_address)


if __name__ == '__main__':
    only_read()
