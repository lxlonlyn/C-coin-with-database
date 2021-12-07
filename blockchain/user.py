# -*- coding:utf-8 -*-
import logging
from PyQt5.QtWidgets import QInputDialog
from utils.db import DB
from utils.ecdsa import ECDSA
from blockchain.block import Blockchain


class User(object):
    """
    用户类。
    """

    def __init__(self, input_wif: str) -> None:
        """
        生成新用户，获取用户的私匙、公匙、wif、address 等信息。

        :param input_wif: 压缩私匙 wif
        """
        self.menu = ECDSA()
        self.wif = input_wif
        self.private_key = ECDSA.get_private_key_from_wif(self.wif)
        self.public_key = ECDSA.get_public_key_from_private_key(
            self.private_key)
        self.compressed_public_key = ECDSA.get_compressed_public_key_from_public_key(
            self.public_key)
        self.address = self.menu.get_address_from_compressed_public_key(
            self.compressed_public_key)
        logging.debug("成功创建用户(wif='" + input_wif + "')。")
