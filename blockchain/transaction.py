# -*- coding:utf-8 -*-
from utils.ecdsa import ECDSA
from utils.sha256 import my_sha256
from .error import *
from typing import List


class In(object):
    """
    交易类中的输入类。主体是解锁脚本，解锁 UTXO。
    """

    def __init__(self, preOut, index, sender) -> None:
        """
        生成一个输出类。

        :param preOut: 引用的上一个交易的哈希
        :param index:
        :param sender:
        """
        # preOut 为引用的上一个交易哈希， preUTXO是维护余额
        # 该输入的原输出的地址
        self.sender = sender
        self.preOut = preOut
        self.index = index
        # 解锁脚本
        private_key = ECDSA.get_private_key_from_wif(sender.wif)
        public_key = ECDSA.get_public_key_from_private_key(private_key)
        self.script = [ECDSA.gen_signature(
            preOut.outList[index].script, int(private_key, 16)), public_key]
        # 维护的UTXO数据
        self.utxo = preOut.outList[index].value

    def to_string(self) -> str:
        string = self.preOut.hash
        string += str(self.script[0][0]) + str(self.script[0][1]) + \
            str(self.script[1][0]) + str(self.script[1][1])
        return string

    def verify(self) -> bool:
        """
        验证消息是否通过。

        :return: 消息通过为 true
        """
        public_key = ECDSA.get_public_key_from_private_key(
            self.sender.wif, True)
        return ECDSA.verify_signature(self.preOut.outList[self.index].script, public_key, self.script[0])


class Out(object):
    """
    交易类中的输出类，主体是锁定脚本。
    """

    def __init__(self, value: int, address: str) -> None:
        # 交易数额
        self.value = value
        # 所在交易集合的索引
        self.index = None
        # 锁定脚本
        self.script = address
        # 是否已经被使用
        self.isUsed = False

    def to_string(self) -> str:
        return str(self.value) + self.script


class Transaction(object):
    """
    单条交易信息。
    """

    def __init__(self) -> None:
        self.inList = []  # type: List[In]
        self.outList = []  # type: List[Out]
        self.hash = ""

    def compute_hash(self) -> None:
        """
        计算单条交易信息的 Hash。
        """
        string = ""
        for each in self.inList:
            string += each.to_string()
        for each in self.outList:
            string += each.to_string()
        self.hash = my_sha256(string)

    def add_input(self, new) -> None:
        """
        加入一个输入类。

        :param new: 输入类
        """
        self.inList.append(new)

    def add_output(self, new) -> None:
        """
        加入一个输出类。

        :param new: 输出类
        """
        self.outList.append(new)
        self.outList[-1].index = len(self.outList) - 1

    def seal(self) -> None:
        self.compute_hash()


def make_deal(sender: "User", receiver_address: str, value: int, blockchain: "Blockchain") -> None:
    """
    构建交易，包含找零过程。

    :param sender: type=User，发起人
    :param receiver_address: 接收人地址
    :param value: 交易金额
    :param blockchain: type=Blockchain，区块链
    """
    # 首先，如果最后一个区块已满，则要求创建新区块
    # 这里设定区块中可以容纳 10 条交易，若超过
    if len(blockchain.blockList[-1].data) == 10:
        raise BlockIsOverFlow()

    # 首先，遍历整个区块链，寻找可用的 UTXO
    curTot = 0
    curTransaction = []
    flag = False
    for blockIndex, eachBlock in enumerate(blockchain.blockList):
        if flag:
            break
        for transactionIndex, eachTransaction in enumerate(eachBlock.data):
            if flag:
                break
            for outIndex, eachOut in enumerate(eachTransaction.outList):
                if flag:
                    break
                if eachOut.script == sender.address and eachOut.isUsed is False:
                    curTot += eachOut.value
                    curTransaction.append(
                        [blockIndex, transactionIndex, outIndex])
                    if curTot >= value:
                        flag = True
    # 根据 UXTO 生成交易输入
    t = Transaction()
    if not flag:
        raise CoinNotEnough()
    for each in curTransaction:
        new = In(blockchain.blockList[each[0]].data[each[1]], each[2], sender)
        if new.verify():
            t.add_input(new)
            blockchain.blockList[each[0]].data[each[1]
                                               ].outList[each[2]].isUsed = True
        else:
            raise AccessDenied()
    # 构建输出
    aim = Out(value, receiver_address)
    # receiver.UTXO += value
    # 开始找零
    returnCoin = Out(curTot - value, sender.address)
    t.add_output(aim)
    t.add_output(returnCoin)
    t.seal()
    # 将该交易打包入区块中
    # # 这里设定区块中可以容纳 10 条交易，若超过
    # if len(blockchain.blockList[-1].data) > 9:
    #     newBlock = Block(sender.addr)
    #     newBlock.addTransaction(t)
    #     blockchain.addBlock(newBlock)
    # else:
    blockchain.blockList[-1].add_transaction(t)
