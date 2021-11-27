# -*- coding: utf-8 -*-
import struct

MOD = 0xFFFFFFFF

# 寄存器初始值
H = H0 = [0x67452301, 0xEFCDAB89, 0x98BADCFE, 0x10325476, 0xC3D2E1F0]

# 加法常量 K (4)
K = [0x5A827999, 0x6ED9EBA1, 0x8F1BBCDC, 0xCA62C1D6]


def left_rotate(data: int, k: int) -> int:
    """
    sha1 内部函数，返回循环左移结果。

    :param data: 被移动的数字
    :param k: 移动的步数
    :return: 移动后的数字
    """
    return ((data << k) | (data >> (32 - k))) & MOD


def my_sha1_hash(input_data: bytes) -> None:
    """
    sha1 内部函数，对分组后的一组消息进行处理，长度 64 字节。

    :param input_data: 输入的字节流，长度 64 字节
    """
    global H

    # 创建信息集合 w，0-15 为初始值，后面 64 位为 0，之后进行操作。
    w = list(struct.unpack(">" + "I" * 16, input_data)) + ([0] * 64)
    for i in range(16, 80):
        w[i] = left_rotate(w[i - 16] ^ w[i - 14] ^ w[i - 8] ^ w[i - 3], 1)

    # 初始化变量
    a, b, c, d, e = H

    # 压缩函数主循环
    for i in range(80):
        if 0 <= i < 20:
            f = (b & c) | ((~b) & d)
            k = K[0]
        elif 20 <= i < 40:
            f = b ^ c ^ d
            k = K[1]
        elif 40 <= i < 60:
            f = (b & c) | (b & d) | (c & d)
            k = K[2]
        else:
            f = b ^ c ^ d
            k = K[3]
        a, b, c, d, e = (e + f + left_rotate(a, 5) + w[i] + k) & MOD, a, left_rotate(b, 30), c, d

    # 更改目前哈希值
    H = (H[0] + a) & MOD, (H[1] + b) & MOD, \
        (H[2] + c) & MOD, (H[3] + d) & MOD, \
        (H[4] + e) & MOD


def my_sha1(input_str: str) -> str:
    """
    返回输入字符串经 sha1 操作后的字符串

    :param input_str: 输入的字符串
    :return: 经 sha1 后返回的字符串，长度 40
    """
    # 消息填充
    # len() 返回的是字符数（英文 8 比特，1 字节），所有方法都应是 8 倍
    data_len = struct.pack('>Q', len(input_str) * 8)
    data = input_str.encode()
    # 添加 10 序列
    data += b'\x80'
    data += b'\x00' * ((56 - len(data) % 64 + 64) % 64)
    # 添加消息长度
    data += data_len

    # MD 缓冲区初始化
    global H
    H = H0

    # 处理消息
    # data 以 8 个字符为一个单位，每次处理 data[p:p+63]
    p = 0
    while p < len(data):
        my_sha1_hash(data[p: p + 64])
        p += 64

    # 最终 H 连接即为答案
    # print(result)
    return "{:08x}".format(H[0]) + "{:08x}".format(H[1]) + \
           "{:08x}".format(H[2]) + "{:08x}".format(H[3]) + \
           "{:08x}".format(H[4])
