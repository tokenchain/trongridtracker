# from the blockscout
import os.path

from core.common.utils import folder_paths
from core.common.okapi import Cache, CacheAddressRead, AddressIncomeExpenses, get_csv_token_history
from core.etherscan import LargeTransactionQuery, BscScan
from core.etherscan.lq import ZipLargeQueryResult
from core.etherscan.polygonscan import PolygonScan
from core.graphz.rel import GraphBuildingBscRelation
from core.reql import ReadHash, NetworkRelFromCacheRes

USDT = "0x55d398326f99059ff775485246999027b3197955"
LINA = "0x762539b45a1dcce3d36d080f74d1aed37844b878"


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
    def step1(self):
        Ltq = LargeTransactionQuery(self.project_name)
        Ltq.setEndpointBase(PolygonScan())
        Ltq.setTargetAddress(self.target)
        Ltq.retrieve_pages_trx()

    def step2(self):
        """
        scan cache files
        """
        bc = ZipLargeQueryResult(self.project_name)
        # 0xa18a7bfc
        bc.callback_pre_al_hash()
        bc.api_work_scan_hash("zip_large_query_result")

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

    def tx_sync(self):
        """
        only use that for one time purppose
        """
        rf = ReadHash(self.project_name)
        rf.processTransferRawToSqlLite()


def work_registeration_bin():
    planner = ProjectPlan('sevenSpringsFinance')
    planner.setParams(
        target_address="0xD3C39cba6d3Afb3d304703F085Fc7A8249576C18",
        binding_tag="Register",
        bind_sig="0x4420e486"
    )

    planner.step1_scan_x()
    planner.step2()
    planner.step3()
    planner.step4()

    planner.tx_sync()

    exit(0)
