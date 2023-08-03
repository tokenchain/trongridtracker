# _*_ coding: utf-8 _*_
# @Date:  4:37 下午
# @File: utils.py
# @Author: liyf
import os.path

import execjs
import hashlib

import pandas as pd
from pandas import DataFrame


# ocr = ddddocr.DdddOcr(show_ad=False)

# https://github.com/liyf-code/reverse_practice/tree/master
class Utils:
    def __init__(self, js_file_name=None, origin_md5_str=None):
        '''
        初始化参数
        :param js_file_name: 需要读取的js文件名称
        :param origin_md5_str: 需要进行md5加密的字符串
        '''
        self.js_file_name = js_file_name
        self.origin_md5_str = origin_md5_str

    def read_js_file(self):
        f = open(self.js_file_name, 'r')
        js_str = f.read()
        ctx = execjs.compile(''.join(js_str))
        return ctx

    def encrypt_md5(self) -> str:
        md5 = hashlib.md5()
        md5.update(self.origin_md5_str.encode('utf8'))
        return md5.hexdigest()


class ExcelBase:
    def _readDF(self, excel_file: str, sheet: str, header: list) -> DataFrame:
        data = pd.read_excel(excel_file, sheet_name=sheet)
        df = pd.DataFrame(data, columns=header)

        return df

    def _sheets(self, excel_file: str) -> list:
        sheetsf = []
        with pd.ExcelFile(excel_file) as f:
            sheets = f.sheet_names
            for sht in sheets:
                # df = f.parse(sht)
                sheetsf.append(sht)
        return sheetsf

    def find_sheet(self, full: str, list_sheets: list):
        h1 = len(full)
        for sh in list_sheets:
            h = len(sh)
            if full[h1 - h:h1] == sh.lower():
                return sh
        return ""

    def _get_sheet(self, sheet: str, header: list) -> DataFrame:
        return self._readDF(self._excel_file, sheet, header=header)

    def setExcelFile(self, path: str):
        self._excel_file = path

    def setHeader(self, header: list):
        self._excel_header = header


def folder_paths(folders: list):
    for f in folders:
        if os.path.isdir(f) is False:
            os.makedirs(f)
