import math
import os.path

from core.common.blockscout import Excel
from core.etherscan import LargeTransactionQuery
from core.etherscan.lq import ZipLargeQueryResult
from core.etherscan.polygonscan import PolygonScan
from core.graphz.rel import GraphBuildingBscRelation
from core.reql import ReadHash, NetworkRelFromCacheRes


class ProjectPlan:
    def __init__(self, project_name):
        self.project_name = project_name
        self.ltq = LargeTransactionQuery(project_name)
        self.rf = NetworkRelFromCacheRes(project_name)

    def setParams(self,
                  target_address: str,
                  binding_tag: str,
                  bind_sig: str
                  ):
        self.target = target_address
        self.tag = binding_tag
        self.signed = bind_sig

    # 1
    def step1_scan_x(self, endpoint=PolygonScan(), page_start: int = 0):
        endpoint.selectTags(self.tag, self.signed)
        self.ltq.setStartPageAt(page_start)
        self.ltq.setEndpointBase(endpoint)
        self.ltq.setTargetAddress(self.target)
        self.ltq.retrieve_pages_trx()

    def step1_blockscout(self, endpoint=PolygonScan(), block_num: int = 0):
        endpoint.selectTags(self.tag, self.signed)
        self.ltq.setEndpointBase(endpoint)
        self.ltq.setTargetAddress(self.target)
        self.ltq.setStartBlockNumber(block_num)
        self.ltq.process_blockscout_transaction()

    def step3_refine_hash(self, endpoint=PolygonScan()):
        self.ltq.setEndpointBase(endpoint)
        self.ltq.collectHashes()
        self.ltq.hashCheckRefine()

    # 2
    def step2(self):
        bc = ZipLargeQueryResult(self.project_name)
        # 0xa18a7bfc
        # bc.ScanRelationship("0xa18a7bfc").SlotAddress(0)
        bc.process(self.tag)

    # 3
    def step3(self):
        # process db referral
        rf = ReadHash(self.project_name)
        rf.processCacheDB()

    # 4
    def setup_network_relation_file_oklink(self, endpoint=PolygonScan()):
        self.rf.cache_db.setOKLinkChainSymbol(endpoint.chain)
        # setup the network relation files
        self.rf.processRelationOklinkTxs(self.signed)

    # 4
    def setup_network_relation_file_bs(self):
        # setup the network relation files
        self.rf.processRelationBlockscoutTxs(self.signed)

    def read_excel1(self, read_excel: str, metadatabankemail: dict = {}) -> dict:
        """
        scan cache files
        """
        ex = Excel()
        path = os.path.join(self.ltq.excelfolder, read_excel)

        def read(row, header):
            email = row["用户邮箱"]
            address = row["用户钱包地址"]
            email = f"{email}"
            address = address.lower()

            if email is None or email == "" or email == "nan":
                metadatabankemail[address] = "n/a"

            else:
                metadatabankemail[address] = email

        ex.setReader(read)
        ex.readFile(path, ["用户邮箱", "用户手机号码", "用户钱包地址", "钱包地址私钥"], "users")

        # new need to build up the hash file from the database

        return metadatabankemail

    def read_excel2(self, read_excel: str, metadatabankemail: dict = {}) -> dict:
        """
        scan cache files
        """
        ex = Excel()
        path = os.path.join(self.ltq.excelfolder, read_excel)

        def read(row, header):
            person_name = row["名字"]
            address = row["TP钱包链接"]
            person_name = f"{person_name}"
            address = address.lower()

            if person_name is None or person_name == "" or person_name == "nan":
                metadatabankemail[address] = "n/a"
            else:
                metadatabankemail[address] = person_name

        ex.setReader(read)
        ex.readFile(path, ["名字", "TP钱包链接"], "keypeople")
        # new need to build up the hash file from the database

        return metadatabankemail

    def step_make_rel_graph_with_tags(self, tags: dict):
        # building the graph
        ref = GraphBuildingBscRelation(self.project_name)
        ref.build_relation_graph_nametagged(tags)

    # 5 develop the chart simply
    def step_build_rel_graph(self):
        # building the graph
        ref = GraphBuildingBscRelation(self.project_name)
        ref.build_relation_graph()

    def tx_sync(self):
        """
        only use that for one time purppose
        """
        rf = ReadHash(self.project_name)
        rf.processTransferRawToSqlLite()
