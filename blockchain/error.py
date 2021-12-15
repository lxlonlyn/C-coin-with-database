# -*- coding:utf-8 -*-
class CoinNotEnough(Exception):
    """
        余额不足异常。
    """

    def __init__(self, cur_val: float, target_val: float):
        self.info = "余额不足。目前持有{}，需要{}".format(cur_val, target_val)

    def __str__(self):
        return self.info
