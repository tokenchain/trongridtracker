# from the blockscout
import os.path

from core.common.utils import ExcelBase, folder_paths, PersonalBank, Stats
from core.etherscan import LargeTransactionQuery
from core.etherscan.embscan import EmbScan
from core.projects.base.projectflow import ProjectPlan

LK = "0x7df1cb1f664df30dd1df4893e8018a59a767c2d2"
USDT = "0x10186d85ac0579cb141ff37261f23cf4f1d254b5"
ROUTER = "0xf46f07db79910c2af2f0a1ddaf2d9c39666588f4"

"""
The work progress to process raw data from the blockscout raw data from the db
found the data source from the blockscout explorer server
Now we need to sort the data of LK to USD and find out the trading data
"""


class BlockscoutRelation(ExcelBase):
    def __init__(self):
        planner = ProjectPlan('emb')
        planner.setParams(
            target_address="0x6ae848cb8948107574ddb171B02290a2AC50C61d",
            binding_tag="Binding",
            bind_sig="0x27fe703f"
        )
        planner.step1_blockscout(EmbScan(), 910905)



if __name__ == "__main__":
    t = BlockscoutRelation()
