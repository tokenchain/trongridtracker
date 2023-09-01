#!/usr/bin/env python
# coding: utf-8

from core.explorer_db import ExcelExplorer

if __name__ == '__main__':
    ee  = ExcelExplorer()
    # ee.check_used_addresses("dhclk.txt")
    #ee.check_used_addresses("赵伟国地址.txt")
    ee.check_used_addresses("孙伯雄地址.txt")
    ee.read()
