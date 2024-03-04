from lib.common.utils import ExportCSV
from lib.common.xscanutils import SCAN_X
from bs4 import BeautifulSoup


class ArbiScan(SCAN_X):
    endpoint: str = "https://arbiscan.io"
    chain: str = "BASE"
    api:str = SCAN_X.ARBISCAN_API

    def soup_em(self, file_path: str, soup_base: BeautifulSoup) -> bool:
        k = soup_base.find("tbody").find_all('tr')
        tempfile = ExportCSV(file_path)
        tempfile.clear()
        if len(k) == 0:
            return False

        for h in k:
            g = [b.get_text() for b in h.find_all('td')]
            if g[0] == 'There are no matching entries' or g[0] == '':
                return False

            hash = g[1]
            method = g[2]
            height = g[3]
            date = g[4]
            xfrom = g[6]
            xto = g[8]
            value = g[9]
            price = g[10]
            tempfile.add_line(",".join([hash, method, height, date, xfrom, xto, value, price]))
        return True

    def soup_em_internal(self, file_path: str, soup_base: BeautifulSoup) -> bool:
        k = soup_base.find("tbody").find_all('tr')
        tempfile = ExportCSV(file_path)

        if len(k) == 0:
            return False

        tempfile.clear()
        for h in k:
            htmls = h.find_all('td')
            g = [b.get_text() for b in htmls]
            if g[0] == 'There are no matching entries' or g[2] == '':
                return False
            hash = g[1]
            age = g[2]
            xfrom = g[4]
            xto = g[6]
            value = g[7]
            token_contract = htmls[8].a.get("href").replace("/token/", "").split("?")[0]
            token_symbol = g[8]
            tempfile.add_line(",".join([hash, age, xfrom, xto, value, token_contract, token_symbol]))
