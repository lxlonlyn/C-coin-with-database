'''
暂时把需求功能函数放到这里
'''
from typing import List, Tuple

from blockchain.error import CoinNotEnough
from blockchain.user import User
from utils.db import DB
from utils.ecdsa import ECDSA
from utils.sha256 import my_sha256
import time
import logging


def make_deal(user: User, receive_compressed_public_key: str, value: float, db: DB) -> any:
    '''
    这个函数是构建交易
    :param user: 是交易的发起者，User类
    :param receive_address: 是收款方的钱包地址
    :param value: 交易的数额
    :param db:操作的数据库
    '''
    receive_address = ECDSA.get_address_from_compressed_public_key(
        receive_compressed_public_key)
    # 第一步，找属于该用户的输出
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
        raise CoinNotEnough(tot, value)

    # 第三步，构建输入
    # 这一步应该收集一下输入的哈希值，因为计算交易哈希时会用到
    in_out_hash_list: List = []
    in_list: List = []

    for each in choosed_out:
        # 把选中的输出，修改其花费标志
        db.execute(
            "update 输出 \
            set 花费标志 = 1 \
            where 输出哈希 = '%s' "
            % each[0]
        )
        sign: Tuple = ECDSA.gen_signature(each[-1], int(user.private_key, 16))
        pre_out_hash: str = each[0]
        compressed_public_key: Tuple = ECDSA.get_compressed_public_key_from_public_key(
            user.public_key)
        # 这里先构建输入
        # 输入（签名，输出哈希，交易哈希，公钥）
        # 输入中的交易哈希只有交易构建完毕后才可以知道，所以先赋空值。
        # 由于签名是一个(int, int)的元组，存入数据库时，转成字符串
        in_list.append([str(sign[0]) + ',' + str(sign[1]),
                        pre_out_hash,
                        compressed_public_key])

        # 记录一下该输入的哈希
        input_string = pre_out_hash \
                       + str(sign[0]) \
                       + str(sign[1]) \
                       + str(compressed_public_key)
        in_out_hash_list.append(my_sha256(input_string))
    # 第四步，构建输出
    # 这一步同样收集一下输出的哈希值，供计算交易哈希使用
    # 输出应该有两个，一个是给收款方的，另一个是给用户自己的找零

    # 先考虑给对方的输出
    # 计算输出哈希，这里存在一个问题
    # 由于输出哈希为其主码，而哈希的计算如果使用value和receive_address来计算，很容易出现重复
    # 所以这里我加入一个对时间戳的哈希，这个时间戳精度较高，可以避免同一时刻的哈希变化
    out_hash_to_target: str = my_sha256(
        str(value) + receive_address + str(time.time()))
    in_out_hash_list.append(out_hash_to_target)
    # 再考虑给自己的找零
    if tot != value:
        out_hash_to_sender: str = my_sha256(
            str(tot - value) + receive_address + str(time.time()))
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
        values('%s', NULL)"
        % transaction_hash
    )
    # 输入进入数据库
    for each in in_list:
        db.execute(
            "insert \
                into 输入 \
                values('%s', '%s', '%s', '%s')"
            % (each[0], each[1], transaction_hash, each[2]))
    # 输出进入数据库
    # 由于输出与用户存在多对一对应关系，所以输出中需要存储用户的公钥
    # 先在用户的表中，找到目前收款地址的对应公钥
    db.execute(
        "insert \
        into 输出 \
        values('%s', 0, '%s', '%s', '%s', '%s')"
        % (
            out_hash_to_target,
            value,
            transaction_hash,
            receive_compressed_public_key,
            receive_address
        )
    )
    if tot != value:
        db.execute(
            "insert \
                into 输出 \
                values('%s', 0, '%s', '%s', '%s', '%s')"
            % (out_hash_to_sender,
               tot - value,
               transaction_hash,
               ECDSA.get_compressed_public_key_from_public_key(
                   user.public_key),
               user.address)
        )


def dig_source(minner_compressed_public_key: str, db: DB) -> str:
    '''
    该函数用来生成新区块，同时对 未确认的交易 进行打包
    即所谓的挖矿操作

    :param minner_public_key: 挖矿的矿工地址
    :param db：操作的数据库

    函数返回新区块的区块哈希
    '''
    minner_address = ECDSA.get_address_from_compressed_public_key(
        minner_compressed_public_key)

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
        values('%s', 0, '%s', '%s', '%s', '%s')"
        % (coinbase, 50, coinbase, minner_compressed_public_key, minner_address)
    )

    # 第二步，寻找要打包的交易
    transcation_to_be_packed: List = db.select(
        "select 交易哈希 \
        from 交易 \
        where 区块哈希 is NULL"
    )

    # 下一步，选中的交易中，对其签名进行验证
    tmp = []
    for each in transcation_to_be_packed:
        cur_transaction_hash = each[0]
        verify_ok: bool = True
        # 对每个each（交易），先从输入的表中找到该交易包含的输入
        in_list = db.select(
            "select * \
            from 输入 \
            where 交易哈希 = '%s'"
            % cur_transaction_hash
        )
        # 对于in_list中每个输入，我们对它验证签名；
        # 一旦有一个输入无法通过签名验证，该交易作废，拒绝被打包进入区块
        # 下面是对输入的签名验证流程
        for each_in in in_list:
            # 首先找到该输入引用的输出，存储它的解锁脚本，即收款地址，这其实也是该签名所保证的消息内容
            used_out_address = db.select(
                "select 收款地址 \
                from 输出 \
                where 输出哈希 = '%s'"
                % each_in[1]
            )[0][0]
            # 然后取出该输入中的公钥
            public_key = ECDSA.get_public_key_from_compressed_public_key(
                each_in[3])
            # 最后取出该输入中的签名
            # 由于签名在存储时，由一个 Tuple[int, int]转为一个字符串存储，所以这里把它还原
            string = each_in[0]
            index_of_comma = string.index(',')
            sign = int(string[:index_of_comma]), int(
                string[index_of_comma + 1:])
            # 至此，所有变量准备完毕
            # 如果验证失败，则拒绝打包该交易
            if not ECDSA.verify_signature(used_out_address, public_key, sign):
                verify_ok = False
                break
        # 所有输入已经扫描完毕
        if verify_ok:
            tmp.append(each)
    # 将签名通过的交易结果记录
    transcation_to_be_packed = tmp[:]

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
    previous_hash = ''
    block_num = db.select(
        "select COUNT('区块哈希') \
        from 区块"
    )[0][0]
    if block_num == 0:
        # 如果此时没有区块，则创建创世区块
        previous_hash = '0' * 64
    else:
        previous_hash = db.select(
            "select 区块哈希 \
            from 区块 \
            where 时间戳 = ( \
                select MAX(时间戳) \
                from 区块 \
            )"
        )[0][0]

    # 第三步，变换Nonce，计算区块哈希
    # 要求前 7 位为 0
    Nonce: str = ''
    block_hash: str = ''
    for i in range(0, 4294967297):
        cur_hash = my_sha256(my_sha256(previous_hash + merkle_hash + str(i)))
        # 检查前7位是否是全0
        seven_digits_are_all_zero: bool = True
        for j in range(0, 2):
            if (cur_hash[j] != '0'):
                seven_digits_are_all_zero = False
                break
        # 如果不满足前 7 位 为 0，那么继续改变 Nonce
        if not seven_digits_are_all_zero:
            continue
        # 如果满足，则挖矿成功
        else:
            Nonce = hex(i)[2:]
            Nonce = '0' * (8 - len(Nonce)) + Nonce
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
        where 区块哈希 is NULL"
        % block_hash
    )
    return block_hash


def update_uxto(user_compressed_public_key: str, db: DB) -> float:
    '''
    该函数计算一个用户的当前最新余额
    并返回该余额

    :param user_compressed_public_key:顾名思义，所查用户的压缩公钥
    :param db:操作的数据库
    '''
    out_of_user = db.select(
        "select 数额 \
        from 输出 \
        where 公钥 = '%s' and 花费标志 = 0"
        % user_compressed_public_key
    )
    tot: float = 0
    for each in out_of_user:
        tot = tot + each[0]
    return tot


def open_a_store(user_compressed_public_key: str, store_name: str, db: DB):
    '''
    该函数 给某个用户开一个新店铺

    :param user_compressed_public_key:开店用户的压缩公钥
    :param store_name:店铺的名称
    :param db:操作的数据库
    '''
    cur_store_num = db.select(
        "select count(店铺编号) \
        from 店铺"
    )[0][0]

    store_index = str(cur_store_num + 1)
    store_index = (4 - len(store_index)) * '0' + store_index

    db.execute(
        "insert \
        into 店铺 \
        values('%s', '%s', '%s', '店主很懒，什么也没有写')"
        % (store_index, store_name, user_compressed_public_key)
    )


def change_store_name(store_index: str, new_name: str, db: DB):
    """
    该函数修改店铺的名称

    :param store_index:操作的店铺编号
    :param new_name:新名称
    :param db:操作的数据库
    """
    db.execute(
        "update 店铺 \
        set 店铺名称 = '%s' \
        where 店铺编号 = '%s' "
        % (new_name, store_index)
    )


def put_on_shelves(app_name: str, app_size: str, app_version: str, app_system: str, app_price: float, store_index: str,
                   db: DB):
    """
    该函数实现某个店铺应用上架

    :param app_name: 应用名称
    :param app_size: 应用大小
    :param app_version: 应用版本
    :param app_system: 应用使用的操作系统
    :param app_price: 应用价格
    :param store_index: 店铺编号
    :param db: 操作的数据库
    """

    # 首先，计算该应用的编号
    app_index = db.select(
        "select count(应用编号) \
        from 应用程序"
    )[0][0] + 1
    app_index = str(app_index)
    app_index = (4 - len(app_index)) * '0' + app_index

    # 插入数据库
    db.execute(
        "insert \
        into 应用程序 \
        values('%s', '%s', '%s', '%s', '%s', '%s', 0, '%s')"
        % (app_index, app_name, app_size, app_version,
           app_system, app_price, store_index)
    )


def buy_app(user: User, app_index: str, db: DB):
    '''
    该函数实现顾客购买app

    :param user: 顾客类
    :param app_index: 购买的应用程序的编号
    :param db: 操作的数据库
    '''
    # 首先，找到应用程序的价格和收款公钥
    tmp = db.select(
        "select 价格, 店铺编号 \
        from 应用程序 \
        where 应用编号 = '%s'"
        % app_index
    )
    value = tmp[0][0]
    receive_compressed_public_key = db.select(
        "select 公钥 \
        from 店铺 \
        where 店铺编号 = '%s'"
        % tmp[0][1]
    )[0][0]
    # 先进行交易
    deal = make_deal(user, receive_compressed_public_key, value, db)
    # 如果钱不够，操作终止
    if isinstance(deal, int) and deal == -1:
        return -1
    # 修改应用程序的销量
    db.execute(
        "update 应用程序 \
        set 销量 = 销量 + 1 \
        where 应用编号 = '%s'"
        % app_index
    )
    # 更新用户的库存
    db.execute(
        "insert \
        into 库存(公钥, 应用编号) \
        values('%s', '%s')"
        % (user.compressed_public_key, app_index)
    )


def create_user(_name: str, db: DB) -> str:
    """
    创建用户。

    :return: 用户的压缩私匙
    """
    temp = ECDSA()
    # 首先，由于 ECDSA 中生成的公钥和私钥为 int 类型
    # 为了 wif 的成功生成，将私钥变为 64 位的 16 进制字符串
    temp.private_key = hex(temp.private_key)[2:]
    temp.private_key = '0' * \
                       (64 - len(temp.private_key)) + temp.private_key
    # 下面计算 wif 和 address
    temp.wif = temp.get_wif_from_private_key(temp.private_key)
    info = ECDSA.get_compressed_public_key_from_public_key(
        ECDSA.get_public_key_from_private_key(temp.private_key))
    if _name != '':
        name = "'" + _name + "'"
    else:
        name = 'NULL'
    logging.debug(
        "执行 SQL：" + "INSERT INTO 用户 VALUES ('%s', %s)" % (info, name))
    db.execute("INSERT INTO 用户 VALUES ('%s', %s)" % (info, name))
    return temp.wif


def update_app_info(app_index: str, app_name: str, app_size: str, app_version: str, app_system: str, app_price: float, db: DB):
    db.execute("UPDATE 应用程序 SET "
               "应用名称 = '%s', "
               "应用大小 = '%s', "
               "应用版本 = '%s', "
               "使用系统 = '%s', "
               "价格 = '%s' "
               "WHERE 应用编号 = '%s'"
               % (app_name, app_size, app_version,
                  app_system, app_price, app_index)
               )
