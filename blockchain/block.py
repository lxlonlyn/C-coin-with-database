# -*- coding:utf-8 -*-
import time
import logging
from typing import List
from utils.sha256 import my_sha256
from blockchain.transaction import Transaction, Out


class Block(object):
    """
    区块链的区块结构，保留可以进行交易的必要区块头信息。

    该区块链并不是符合比特币规范版本的区块链，原因是我俩只开发了一周。
    """
    def __init__(self, miner_address: str) -> None:
        """
        创建一个新的区块，并传入交易记录。

        :param miner_address: 矿工地址，字符串0
        """
        self.timeStamp = Block.set_timestamp()
        self.data = Block.dig_source(miner_address)
        self.preHash = '0' * 64
        self.merkleHash = ""
        self.set_merkle_hash()
        self.blockHash = ""
        self.set_block_hash()
        logging.debug("新区块(BlockHash='" + self.blockHash + "')成功生成。")

    @classmethod
    def set_timestamp(cls) -> float:
        """
        获取时间，设定时间戳。

        :return: 当前时间
        """
        return time.time()

    @classmethod
    def dig_source(cls, miner_address: str) -> List[Transaction]:
        """
        生成每个新区块的交易信息，只包含挖矿所得。

        :param miner_address: 矿工地址
        :return: 初始的交易信息
        """
        coinbase = Transaction()
        new = Out(50, miner_address)
        coinbase.add_output(new)
        coinbase.seal()
        return [coinbase]

    # 在该区块中增加交易
    def add_transaction(self, new_transaction: Transaction) -> None:
        """
        区块中新增交易。

        :param new_transaction: 新增的交易
        """
        self.data.append(new_transaction)
        self.set_merkle_hash()
        self.set_block_hash()

    def set_merkle_hash(self) -> None:
        """
        通过传入的交易来计算 Merkle Hash。
        """
        cur = []  # type: List[str]
        for each in self.data:
            cur.append(each.hash)
        nxt = []  # type: List[str]
        while len(cur) != 1:
            last = None
            for i, each in enumerate(cur):
                if i % 2 == 0:
                    if i == len(cur) - 1:
                        nxt.append(my_sha256(my_sha256(each + each)))
                    else:
                        last = each
                else:
                    nxt.append((my_sha256(last + each)))
            cur = nxt
            nxt = []
        self.merkleHash = cur[0]

    def set_block_hash(self) -> None:
        """
        通过传入的区块来计算当前区块的 Block Hash
        """
        string = str(self.timeStamp)
        for each in self.data:
            string += each.hash
        string += self.preHash + self.merkleHash
        self.blockHash = my_sha256(string)

    def link(self, pre: str) -> None:
        """
        增添区块时，记录上个区块 Block Hash，计算本区块 Block Hash。

        :param pre: 上个区块的 Block Hash
        """
        self.preHash = pre
        self.set_block_hash()


class Blockchain(object):
    """
    区块链，本质是区块的 list 集合。
    """
    def __init__(self):
        self.blockList = []  # type: List[Block]

    def add_block(self, new_block: Block) -> None:
        if len(self.blockList) > 0:
            new_block.link(self.blockList[-1].blockHash)
        self.blockList.append(new_block)
        logging.debug("已将新区块(block hash = '" + new_block.blockHash + "')加入区块链。")
