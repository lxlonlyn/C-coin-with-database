# -*- coding: utf-8 -*-
import struct

MOD = 0xFFFFFFFF

# 寄存器初始值
H = H0 = [0x6a09e667, 0xbb67ae85, 0x3c6ef372, 0xa54ff53a,
          0x510e527f, 0x9b05688c, 0x1f83d9ab, 0x5be0cd19]

# 加法常量 K (64)
K = [0x428a2f98, 0x71374491, 0xb5c0fbcf, 0xe9b5dba5,
     0x3956c25b, 0x59f111f1, 0x923f82a4, 0xab1c5ed5,
     0xd807aa98, 0x12835b01, 0x243185be, 0x550c7dc3,
     0x72be5d74, 0x80deb1fe, 0x9bdc06a7, 0xc19bf174,
     0xe49b69c1, 0xefbe4786, 0x0fc19dc6, 0x240ca1cc,
     0x2de92c6f, 0x4a7484aa, 0x5cb0a9dc, 0x76f988da,
     0x983e5152, 0xa831c66d, 0xb00327c8, 0xbf597fc7,
     0xc6e00bf3, 0xd5a79147, 0x06ca6351, 0x14292967,
     0x27b70a85, 0x2e1b2138, 0x4d2c6dfc, 0x53380d13,
     0x650a7354, 0x766a0abb, 0x81c2c92e, 0x92722c85,
     0xa2bfe8a1, 0xa81a664b, 0xc24b8b70, 0xc76c51a3,
     0xd192e819, 0xd6990624, 0xf40e3585, 0x106aa070,
     0x19a4c116, 0x1e376c08, 0x2748774c, 0x34b0bcb5,
     0x391c0cb3, 0x4ed8aa4a, 0x5b9cca4f, 0x682e6ff3,
     0x748f82ee, 0x78a5636f, 0x84c87814, 0x8cc70208,
     0x90befffa, 0xa4506ceb, 0xbef9a3f7, 0xc67178f2]


def right_rotate(data: int, k: int) -> int:
    """
    sha256 内部函数，返回循环右移结果。

    :param data: 被移动的数字
    :param k: 移动的步数
    :return: 移动后的数字
    """
    return ((data >> k) | (data << (32 - k))) & MOD


def my_sha256_hash(input_data: bytes) -> None:
    """
    sha256 内部函数，对分组后的一组消息进行处理，长度 64 字节。

    :param input_data: 输入的字节流，长度 64 字节
    """
    global H

    # 创建信息集合 w，0-15 为初始值，后面 48 位为0，之后进行操作。
    w = list(struct.unpack(">" + "I" * 16, input_data)) + ([0] * 48)
    for i in range(16, 64):
        s0 = right_rotate(
            w[i - 15], 7) ^ right_rotate(w[i - 15], 18) ^ (w[i - 15] >> 3)
        s1 = right_rotate(
            w[i - 2], 17) ^ right_rotate(w[i - 2], 19) ^ (w[i - 2] >> 10)
        w[i] = (w[i - 16] + s0 + w[i - 7] + s1) & MOD

    # 初始化变量
    a, b, c, d, e, f, g, h = H

    # 压缩函数主循环
    for i in range(64):
        # print(a, b, c, d, e, f, g, h)
        s1 = right_rotate(e, 6) ^ right_rotate(e, 11) ^ right_rotate(e, 25)
        ch = (e & f) ^ ((~e) & g)
        tmp1 = (h + s1 + ch + K[i] + w[i]) & MOD
        s0 = right_rotate(a, 2) ^ right_rotate(a, 13) ^ right_rotate(a, 22)
        maj = (a & b) ^ (a & c) ^ (b & c)
        tmp2 = (s0 + maj) & MOD

        h = g
        g = f
        f = e
        e = (d + tmp1) & MOD
        d = c
        c = b
        b = a
        a = (tmp1 + tmp2) & MOD

    # 更改目前哈希值
    H = (H[0] + a) & MOD, (H[1] + b) & MOD, \
        (H[2] + c) & MOD, (H[3] + d) & MOD, \
        (H[4] + e) & MOD, (H[5] + f) & MOD, \
        (H[6] + g) & MOD, (H[7] + h) & MOD


def my_sha256(input_str: str, is_number: bool = False, is_hex: bool = False) -> str:
    """
    对输入字符串进行 sha256

    :param input_str: 输入的字符串，如果为数字需提前转换为字符串格式。
    :param is_number: 是否按照数字格式处理字符串，若不是则会使用对应字符值。
    :param is_hex: 是否是十六进制数字串，若为 False 则按照十进制处理。
    :return: 长度为 64 的十六进制字符串，代表 sha256 后结果
    """
    if is_number:
        # original_len = len(input_str)
        original_len = 64
        if is_hex:
            num_str = hex(int(input_str, 16))[2:]
        else:
            num_str = hex(int(input_str, 10))[2:]

        if len(num_str) < original_len:
            num_str = "0" * (original_len - len(num_str)) + num_str

        data_len = struct.pack('>Q', len(num_str) * 4)
        data = b''
        for i in range(0, len(num_str), 2):
            num = (int(num_str[i], 16) << 4)
            if i + 1 < len(num_str):
                num += int(num_str[i + 1], 16)
            data += struct.pack('<B', num)
    else:
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
        my_sha256_hash(data[p: p + 64])
        p += 64

    # 最终 H 连接即为答案
    # print(result)
    return "{:08x}".format(H[0]) + "{:08x}".format(H[1]) + \
           "{:08x}".format(H[2]) + "{:08x}".format(H[3]) + \
           "{:08x}".format(H[4]) + "{:08x}".format(H[5]) + \
           "{:08x}".format(H[6]) + "{:08x}".format(H[7])
