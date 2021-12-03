# -*- coding:utf-8 -*-
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
        # logging.debug("成功创建用户(wif='" + input_wif + "')。")

    @classmethod
    def create_user(cls, _name="") -> str:
        """
        创建用户。

        :return: 用户的压缩私匙
        """
        temp = ECDSA()
        # 首先，由于 ECDSA 中生成的公钥和私钥为 int 类型，为了 wif 的成功生成，将私钥变为 64 位的 16 进制字符串
        temp.private_key = hex(temp.private_key)[2:]
        temp.private_key = '0' * \
            (64 - len(temp.private_key)) + temp.private_key
        # 下面计算 wif 和 address
        temp.wif = temp.get_wif_from_private_key(temp.private_key)
        db = DB("localhost", _passwd="csnb")
        info = ECDSA.get_compressed_public_key_from_public_key(
            ECDSA.get_public_key_from_private_key(temp.private_key))
        address = ECDSA.get_address_from_compressed_public_key(info)
        if _name != '':
            name = "'" + _name + "'"
        else:
            name = 'NULL'
        db.execute("INSERT INTO 用户 VALUES ('%s', %s, 0)" % (info, name))
        # db.execute("insert \
        #             into 店铺 \
        #             values('%s', %s)" \
        #             % (address, name))
        return temp.wif

    # @classmethod
    # def get_utxo(cls, address: str, chain: Blockchain) -> int:
    #     """
    #     获取用户 UTXO。

    #     :param address: 用户地址
    #     :param chain: 区块链
    #     :return: 对应用户 UTXO
    #     """
    #     ans = 0
    #     for eachBlock in chain.blockList:
    #         for eachTransaction in eachBlock.data:
    #             for eachOut in eachTransaction.outList:
    #                 if eachOut.script == address and eachOut.isUsed is False:
    #                     ans += eachOut.value
    #     return ans

# 待完成的功能函数
# 用户余额更新；用户开店；应用上架；应用下架；用户关店；
# 购买应用程序