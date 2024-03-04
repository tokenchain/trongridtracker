

import logging
import os

# Only show warnings
logging.getLogger("urllib3").setLevel(logging.ERROR)
# Disable all child loggers of urllib3, e.g. urllib3.connectionpool
logging.getLogger("urllib3").propagate = False

DATAPATH_BASE = "/Users/hesdx/Documents/b95/trackerfactory"
NETWORK = "mainnet"
ROOT = os.path.join(os.path.dirname(__file__))
statement = 'End : {}, IO File {}'
file_format = 'data/reports/report_{}.txt'
file_analysis = 'data/analysis/analysis_{}.json'
case_report_summary = 'data/reports/summary_{}.txt'
file_hold_format = 'rehold_{}.txt'
filelog_format = 'log_{}.txt'
statement_process = 'Processed page: {} {}\n'
statement_log = 'Log {}, FP: {}\n'
statement_sum = '\nReport for address {}\nTotal outgoing USDT: {} / count: {}\nTotal incoming USDT: {} / count: {}\nNet {}'
request_1_token = "https://api.trongrid.io/v1/accounts/{}/transactions/trc20?limit={}&contract_address={}"
api_holders = "https://apilist.tronscan.org/api/tokenholders?sort=-balance&limit={}&start={}&count=true&address={}"
API_PAGER = "https://apilist.tronscanapi.com/api/token_trc20/transfers"
help = """
Please note that the json file {FILENAME} gives the following explaination:
address:  the address transfered to
bal: the total amount to be transfered, positive is the collection address, negative is the upper level collection.
hit: the amount of transactions that is associated to this address
"""

"""
https://dreampuf.github.io/GraphvizOnline/#digraph%20G%20%7B%0A%0A%20%20subgraph%20cluster_0%20%7B%0A%20%20%20%20style%3Dfilled%3B%0A%20%20%20%20color%3Dlightgrey%3B%0A%20%20%20%20node%20%5Bstyle%3Dfilled%2Ccolor%3Dwhite%5D%3B%0A%20%20%20%20a0%20-%3E%20a1%20-%3E%20a2%20-%3E%20a3%3B%0A%20%20%20%20label%20%3D%20%22process%20%231%22%3B%0A%20%20%7D%0A%0A%20%20subgraph%20cluster_1%20%7B%0A%20%20%20%20node%20%5Bstyle%3Dfilled%5D%3B%0A%20%20%20%20b0%20-%3E%20b1%20-%3E%20b2%20-%3E%20b3%3B%0A%20%20%20%20label%20%3D%20%22process%20%232%22%3B%0A%20%20%20%20color%3Dblue%0A%20%20%7D%0A%20%20start%20-%3E%20a0%3B%0A%20%20start%20-%3E%20b0%3B%0A%20%20a1%20-%3E%20b3%3B%0A%20%20b2%20-%3E%20a3%3B%0A%20%20a3%20-%3E%20a0%3B%0A%20%20a3%20-%3E%20end%3B%0A%20%20b3%20-%3E%20end%3B%0A%0A%20%20start%20%5Bshape%3DMdiamond%5D%3B%0A%20%20end%20%5Bshape%3DMsquare%5D%3B%0A%7D

abort("Cannot enlarge memory arrays. Either (1) compile with -s TOTAL_MEMORY=X with X higher than the current value 16777216, (2) compile with -s ALLOW_MEMORY_GROWTH=1 which allows increasing the size at runtime but prevents some optimizations, (3) set Module.TOTAL_MEMORY to a higher value before the program runs, or (4) if you want malloc to return NULL (0) instead of this abort, compile with -s ABORTING_MALLOC=0 "). Build with -s ASSERTIONS=1 for more info.

"""

