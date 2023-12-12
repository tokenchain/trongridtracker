from core.common.xscanutils import SCAN_X
from bs4 import BeautifulSoup

class Etherscan(SCAN_X):
    endpoint: str = "https://etherscan.io"
    chain: str = "ETH"
    api:str = SCAN_X.ETHERSCAN_API
