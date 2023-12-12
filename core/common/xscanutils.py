# !/usr/bin/env python
# coding: utf-8
from bs4 import BeautifulSoup
from time import sleep

"""
This code base support large query data crawl from any of the 
1. etherscan - https://etherscan.io
            - https://cn.etherscan.com/
2. bscscan - https://bscscan.com/
3. arbiscan - https://arbiscan.io/
4. polygonscan - https://polygonscan.com/
5. basescan - https://basescan.org/

"""


def generate_header():
    __headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36',
    }
    return __headers


class SCAN_X:
    endpoint: str = "https://etherscan.io"
    chain: str = "ETH"
    api: str = ''

    ETHERSCAN_API: str = '5PANAI4IM9F2UQT7HGEX4JSHP2B4A5M9YV'
    BSCSCAN_API: str = '59IISNUG2CR3PIMAJF7MACQTS7DY6WFJDJ'
    BASESCAN_API: str = 'Z9NYC5I2M9VE7IQP4VMD1MI2VAT2TSIJJV'
    ARBISCAN_API: str = '8CH3DSGEY59K3XN8ACYD2AI991V8HNKPIC'
    POLYGONSCAN_API: str = '2I26GHVDCVCCMF29MT5BYFZWWIUPJSMB6K'
    OPTIMISTICSCAN_API: str = 'Y1SZVBTW55J6ZCGNNIRFD4GE875QTMTU16'

    def selectTags(self, method: str, signature: str):
        self.relationship_binding = method
        self.signature_binding = signature

    def setHashRelationCacheFile(self, path: str):
        pass

    def addRelationHash(self, hash: str):
        pass

    def json_blkscout(self, file_path: str, html_items: list) -> bool:
        pass

    def soup_em(self, file_path: str, soup_base: BeautifulSoup) -> bool:
        """
        process soup html transaction from etherscan base html
        """
        pass

    def soup_em_internal(self, file_path: str, soup_base: BeautifulSoup) -> bool:
        """
        process soup html internal transaction from etherscan base html
        """
        pass

    def soup_token_holder(self, addline: any, soup_base: BeautifulSoup) -> bool:
        """
        process soup html internal transaction from etherscan base html
        """
        pass


class EtherscanChina(SCAN_X):
    endpoint: str = "https://cn.etherscan.com"
    chain: str = "ETH"


class PolygonScan(SCAN_X):
    endpoint: str = "https://polygonscan.com"
    chain: str = "POL"


class BaseScan(SCAN_X):
    endpoint: str = "https://basescan.org"
    chain: str = "BASE"


class AvaxScan(SCAN_X):
    endpoint: str = "https://snowtrace.io"
    chain: str = "AVAX"
