from lib.common.blockscout import ReqDatBlockScout
from lib.common.utils import ExportCSV
from lib.common.xscanutils import SCAN_X
from bs4 import BeautifulSoup


class EmbScan(SCAN_X):
    endpoint: str = "https://ember.cash"
    chain: str = "EMB"
    relationship_binding = "GetReward"

    def __init__(self):
        chain: str = "EMB"
        self.api_req = ReqDatBlockScout()
        self.api_req.setBase(f"{self.endpoint}/api")

    def json_blkscout(self, file_path: str, html_items: list) -> bool:
        tempfile = ExportCSV(file_path)
        for r in html_items:
            txt = r.replace("\n", "").replace("\"", '"')
            bs = BeautifulSoup(txt, 'html.parser')
            then_tag = bs.find("div", text=self.relationship_binding)
            if then_tag is None:
                continue
            parent_div = then_tag.find_parent('div', attrs={'data-identifier-hash': True})
            if parent_div:
                hash = parent_div['data-identifier-hash']
                tempfile.add_line(hash)
                print(f"{hash} found keyword {self.relationship_binding}")
            else:
                print("No parent div with 'data-identifier-hash' attribute.")
        return True

    def soup_em_internal(self, file_path: str, soup_base: BeautifulSoup) -> bool:
        return True
