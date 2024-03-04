from lib.common.utils import ExportCSV
from lib.common.xscanutils import SCAN_X
from bs4 import BeautifulSoup
import lxml

"""
slowmist
web3
https://sso.slowmist.com/en/web3_verification/?eth_address=0x7d87ee7c273bf2f9cbc3184b77d01f31c64f5787
"""

def debug_symbol(x):
    print("------debug this s----")
    print(x)
    print("------debug this e----")


class PolygonScan(SCAN_X):
    endpoint: str = "https://polygonscan.com"
    chain: str = "POLYGON"
    api: str = SCAN_X.POLYGONSCAN_API

    def setHashRelationCacheFile(self, path: str):
        if self.relationship_binding == "":
            print("No method tag is found. Skip relation hash file setup.")
            return
        self.hashTmp = ExportCSV(path)

    def addRelationHash(self, hash: str):
        if self.hashTmp is not None:
            self.hashTmp.add_line(hash)

    def soup_token_holder(self, addline: any, soup_base: BeautifulSoup) -> bool:
        k = soup_base.find("tbody").find_all('tr')

        if len(k) == 0:
            return False
        v = 0
        for h in k:
            g = self.process_holder_ex(h.find_all('td'))
            if len(g) == 0:
                return False

            ranking = g[0]
            is_contract = g[1]
            label = g[2]
            address_holder = g[3]
            holding_amount = g[4]
            holding_share = g[5]
            addline(",".join([ranking, is_contract, label, address_holder, holding_amount, holding_share]))
            v += 1

        return True

    def process_holder_ex(self, soup_td: list) -> list:

        label = ''
        address = ''
        contract = '0'
        amount = ''
        share = ''
        rank = ''
        y = 0
        for b_soup in soup_td:
            text = b_soup.get_text().replace('\n', '').strip()
            if text == '':
                continue
            if 'no matching entries' in text:
                return []
            if text == None:
                y += 1
                continue
            if text != '':
                # debug_symbol(text)
                if y == 0 and int(text) > 0:
                    rank = text
                    y += 1
                    continue

                if '%' in text:
                    share = text
                    y += 1
                    continue

                if '...' in text and text[0:2] == '0x':
                    label = 'wallet'

                    # checking on the contract
                    if b_soup.i != None and b_soup.i.get('aria-label') == 'Contract':
                        contract = '1'
                        label = 'contract'
                    else:
                        contract = '0'

                    if b_soup.a != None and b_soup.a.get('title') != None:
                        address = b_soup.a.get('title')

                    y += 1
                    continue

                if b_soup.a != None and b_soup.a.get('href') != None:
                    hr = b_soup.a.get('href')
                    if '/token/' in hr:
                        address = hr.split("=")[1]
                        label = text
                        contract = '1'
                    # debug_symbol(b_soup.a)
                    y += 1
                    continue

                if ',' in text:
                    amount = text.replace(',', '_')
                    y += 1
                    continue

        return [rank, contract, label, address, amount, share]

    def process_bsc(self, all_td: list) -> list:
        """
        the internal use for html to CVS metadata from etherscan and related htmls
        """
        returnlist = []
        for b_soup in all_td:

            text = b_soup.get_text().replace('\n', '')

            if text == '':
                continue

            if 'no matching entries' in text:
                return []

            if text == None:
                continue

            if text != '':
                if '...' in text and text[0:2] == '0x':
                    if b_soup.span != None and b_soup.span.get('data-bs-title') != None:
                        value = b_soup.span.get('data-bs-title')
                        returnlist.append(value)
                    if b_soup.a != None and b_soup.a.get('data-bs-title') != None:
                        value = b_soup.a.get('data-bs-title')
                        returnlist.append(value)
                else:
                    returnlist.append(text)

        return returnlist

    def soup_em(self, file_path: str, soup_base: BeautifulSoup) -> bool:
        # file_path: the tmp file to store the cvs list info on the plain text file.
        # soup from page of polygon scan and see the tags if found from each line
        k = soup_base.find("tbody").find_all('tr')
        # tempfile = ExportCSV(file_path)
        # tempfile.clear()
        if len(k) == 0:
            return False

        for h in k:
            # g = [b.get_text().replace('\n', '') for b in h.find_all('td')]
            g = self.process_bsc(h.find_all('td'))

            if len(g) == 0:
                return False
            hash = g[0]
            method = g[1]
            height = g[2]
            date = g[3]
            timestamp = g[5]
            xfrom = g[6]
            xto = g[8]
            value = g[9]
            price = g[10]

            # tempfile.add_line(",".join([hash, method, height, date, xfrom, xto, value, price]))
            if method == self.relationship_binding:
                print(f"Found binding file {hash} with {method}")
                self.addRelationHash(hash)

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
