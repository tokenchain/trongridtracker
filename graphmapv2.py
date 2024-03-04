#!/usr/bin/python
from lib.projects.casesscan import *
"""
  worker is now working.
  0xBe88292826d0d763423195688bdE1AAdCeAf8c25
"""
import logging

# Only show warnings
logging.getLogger("urllib3").setLevel(logging.ERROR)
# Disable all child loggers of urllib3, e.g. urllib3.connectionpool
# logging.getLogger("urllib3").propagate = False


if __name__ == '__main__':
    gamble_case_1_analysis()
