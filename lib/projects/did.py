

from lib.etherscan import LargeTransactionQuery, BscScan
from lib.etherscan.lq import ZipLargeQueryResult
from lib.graphz.rel import GraphBuildingBscRelation
from lib.reql import ReadHash, NetworkRelFromCacheRes

def example():
    pp = ProjectPlan('DID')
    pp.setParams(
        target_address="0xc63c76e846d1a1d37415db4472cf3ae59a47090b",
        binding_tag="Set Referrer",
        bind_sig="0xa18a7bfc"
    )

    pp.step1_scan_x()
    pp.step2()
    pp.step3()
    pp.step4()


class ProjectPlan:
    def __init__(self, project_name):
        self.project_name = project_name

    def setParams(self,
                  target_address: str,
                  binding_tag: str,
                  bind_sig: str
                  ):
        self.target = target_address
        self.tag = binding_tag
        self.signed = bind_sig

    # 1
    def step1_scan_x(self):
        Ltq = LargeTransactionQuery(self.project_name)
        Ltq.setEndpointBase(BscScan())
        Ltq.setTargetAddress(self.target)
        Ltq.retrieve_pages_trx()

    # 2
    def step2(self):
        """
        scan cache files
        """
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
    def setup_network_relation_file_oklink(self):
        # setup the network relation files
        rf = NetworkRelFromCacheRes(self.project_name)
        rf.processRelationOklinkTxs(self.signed)

    # 5
    def step4(self):
        # building the graph
        ref = GraphBuildingBscRelation(self.project_name)
        ref.build_relation_graph()

    def oppo(self):
        """
        only use that for one time purppose
        """
        rf = ReadHash(self.project_name)
        rf.processTransferToSqlLite()

    def count_involves(self):
        ref = GraphBuildingBscRelation(self.project_name)
        ref.count_relations_unique()
