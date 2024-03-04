# !/usr/bin/env python
# coding: utf-8
import json
import time

import web3
# Press ⌃R to execute it or replace it with your code.
# Press Double ⇧ to search everywhere for classes, files, tool windows, actions, and settings.
from .mask import EthereumBaseWallet
from .app import AppMetamask
import logging

logger1 = logging.getLogger("web3.RequestManager")
logger2 = logging.getLogger("web3.providers.HTTPProvider")
logger3 = logging.getLogger("urllib3.connectionpool")
logger2.setLevel(logging.ERROR)
logger1.setLevel(logging.ERROR)
logger3.setLevel(logging.ERROR)
