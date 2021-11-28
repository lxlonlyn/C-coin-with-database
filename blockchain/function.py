'''
暂时把需求功能函数放到这里
'''
from typing import List, Tuple
from blockchain.user import User
from utils.db import DB
from utils.ecdsa import ECDSA
from utils.sha256 import my_sha256
import time

def make_deal(user: User, receive_address: str, value: float) -> any:
    '''
    这个函数是构建交易
    :param user: 是交易的发起者，User类
    :param receive_address: 是收款方的钱包地址
    :param value: 交易的数额
    '''
    # 第一步，找属于该用户的输出
    db = DB("localhost", _password = "csnb")
    available_out: Tuple = db.select(
        "select * \
        from 输出 \
        where 收款地址 = '%s' and 花费标志 = 0" % user.address)
    # 第二步，选出一些输出来花费，要求够用
    choosed_out: List = []
    tot: float = 0
    for each in available_out:
        # 选够了就停止
        if tot >= value:
            break
        # 累计当前的余额
        tot = tot + each[2]
        choosed_out.append(each)
    # 这里判断一下钱是否足够
    if tot < value:
        return -1
    
    # 第三步，构建输入
    # 这一步应该收集一下输入的哈希值，因为计算交易哈希时会用到
    in_out_hash_list: List = []
    in_list: List = []

    for each in choosed_out:
        # 把选中的输出，修改其花费标志
        db.execute(
            "update 输出 \
            set 花费标志 = 1 \
            where 输出哈希 = '%s' " \
            % each[0]
        )
        sign: Tuple = ECDSA.gen_signature(each[-1], int(user.private_key, 16))
        pre_out_hash: str= each[0]
        public_key: Tuple = user.public_key
        # 这里先构建输入
        # 输入（签名，输出哈希，交易哈希，公钥）
        # 输入中的交易哈希只有交易构建完毕后才可以知道，所以先赋空值。
        in_list.append([sign, pre_out_hash, public_key])

        # 记录一下该输入的哈希
        input_string = pre_out_hash \
                        + str(sign[0]) \
                        + str(sign[1]) \
                        + str(public_key[0] \
                        + str(public_key[1]))
        in_out_hash_list.append(my_sha256(input_string))
    # 第四步，构建输出
    # 这一步同样收集一下输出的哈希值，供计算交易哈希使用
    # 输出应该有两个，一个是给收款方的，另一个是给用户自己的找零

    # 先考虑给对方的输出
    # 计算输出哈希，这里存在一个问题
    # 由于输出哈希为其主码，而哈希的计算如果使用value和receive_address来计算，很容易出现重复
    # 所以这里我加入一个对时间戳的哈希，这个时间戳精度较高，可以避免同一时刻的哈希变化
    out_hash_to_target: str = my_sha256(str(value) + receive_address + str(time.time()))
    in_out_hash_list.append(out_hash_to_target)
    # 再考虑给自己的找零
    if tot != value:
        value = tot - value
        out_hash_to_sender: str = my_sha256(str(value) + receive_address + str(time.time()))
        in_out_hash_list.append(out_hash_to_sender)

    # 第五步，构建交易
    transaction_hash = ''
    for each in in_out_hash_list:
        transaction_hash = transaction_hash + each
    transaction_hash = my_sha256(my_sha256(transaction_hash))
    # 第六步，完善数据库
    # 交易进入数据库
    # 交易所属的区块哈希先空着，等到区块被打包时，再进行完善
    db.execute(
        "insert \
        into 交易 \
        values('%s', NULL)" \
        % transaction_hash
    )
    # 输入进入数据库
    for each in in_list:
        db.execute(
                "insert \
                into 输入 \
                values('%s', '%s', '%s', '%s')" \
                    % (each[0], each[1], transaction_hash, each[2]))
    # 输出进入数据库
    db.execute(
        "insert \
        into 输出 \
        values('%s', 0, '%s', NULL, '%s')" \
        % (out_hash_to_target, value, receive_address)
    )
    if tot != value:
        db.execute(
                "insert \
                into 输出 \
                values('%s', 0, '%s', '%s')" \
                % (out_hash_to_sender, value, user.address)
        )


def dig_source(minner_address: str) -> str:
    '''
    该函数用来生成新区块，同时对 未确认的交易 进行打包
    即所谓的挖矿操作

    :param minner_address: 挖矿的矿工地址

    函数返回新区块的区块哈希
    '''
    db = DB("localhost", _password = "csnb")

    # 第一步，创建coinbase交易，即矿工给自己的挖矿奖励50个币
    coinbase: str = my_sha256(str(50) + minner_address + str(time.time()))
    # 将该coinbase交易写入交易数据库
    db.execute(
        "insert \
        into 交易 \
        values('%s', NULL)"
        % coinbase
    )
    # 将该coinbase交易写入输出数据库
    db.execute(
        "insert \
        into 输出 \
        values('%s', 0, '%s', '%s', '%s')" \
        % (coinbase, 50, coinbase, minner_address)
    )

    # 第二步，寻找要打包的交易
    transcation_to_be_packed: List = db.select(
        "select 交易哈希 \
        from 交易 \
        where 区块哈希 = NULL"
    )

    # 第二步，计算 Merkle 树根
    # 先把刚刚 select 得到的元组中取出其交易哈希值，存入 cur
    cur = []  # type: List[str]
    for each in transcation_to_be_packed:
        cur.append(each[0])
    # 下面用二重循环计算merkle树根
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
        cur = nxt[:]
        nxt = []
    merkle_hash = cur[0]

    # 第二步，确定前驱哈希
    previous_hash = db.select(
        "select 区块哈希 \
        from 区块 \
        where 时间戳 = ( \
            select MAX(时间戳) \
            from 区块 \
        )"
    )[0]

    # 第三步，变换Nonce，计算区块哈希
    # 要求前 7 位为 0
    Nonce: str = ''
    block_hash: str = ''
    for i in range(0, 4294967297):
        cur_hash = my_sha256(my_sha256(previous_hash + merkle_hash + i))
        # 检查前7位是否是全0
        seven_digits_are_all_zero: bool = True
        for i in range(0, 7):
            if(cur_hash[i] != '0'):
                seven_digits_are_all_zero = False
                break
        # 如果不满足前 7 位 为 0，那么继续改变 Nonce
        if not seven_digits_are_all_zero:
            continue
        # 如果满足，则挖矿成功
        else:
            Nonce = hex(i)[2:]
            block_hash = cur_hash
            break
    
    # 第四步，新区块进入数据库
    # 这里我不插入时间戳，因为它可以自动生成
    db.execute(
        "insert \
        into 区块(区块哈希, 前驱哈希, Merkle哈希, Nonce) \
        values('%s', '%s', '%s', '%s')"
        % (block_hash, previous_hash, merkle_hash, Nonce)
    )
    # 第五步，把该区块中打包的交易的区块哈希值更新为该区块
    db.execute(
        "update 交易\
        set 区块哈希 = '%s' \
        where 区块哈希 = NULL" \
        % block_hash
    )
    return block_hash