# -*- coding:utf-8 -*-
import logging
class CoinNotEnough(Exception):
    def __init__(self):
        logging.warning("比特币余额不足。")
        pass

class AccessDenied(Exception):
    def __init__(self):
        pass

class BlockIsOverFlow(Exception):
    def __init__(self):
        logging.warning("交易已达上限，需要更多的区块。")
        pass