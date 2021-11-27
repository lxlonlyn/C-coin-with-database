# -*- coding: utf-8 -*-
from typing import Tuple
import random
import struct
import hashlib
from .sha256 import my_sha256
from .sha1 import my_sha1
import base58
import secrets


# ECDSA 签名机制。私匙 160 比特，公匙为点坐标。
class ECDSA(object):
    """
        ECDSA 类：
            一、每次创建类的对象时，会生成对应的新的私匙和公匙

            二、可以生成私匙和公匙，并实现私匙、公匙、压缩私匙、压缩公匙、地址间的转化

            三、可以根据私匙给信息签名，同时可以根据公匙验证信息

    """
    # 生成元及模数
    g = 0x79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798, \
        0x483ADA7726A3C4655DA4FBFC0E1108A8FD17B448A68554199C47D08FFB10D4B8
    p = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
    MOD = 0xFFFFFFFFFFFFFFFFFFFFFFFF0123456789ABCEA7
    # 定义无穷点，GF 的阶
    INF = (-1, -1)
    order = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141

    def __init__(self):
        self.private_key = secrets.randbits(256) % ECDSA.p
        print("private key:", self.private_key)
        self.public_key = ECDSA.curve_mul(ECDSA.g, self.private_key)

    @classmethod
    def quick_pow(cls, x: int, k: int, md: int = p) -> int:
        res = 1
        while k:
            if k % 2 == 1:
                res = res * x % md
            x = x * x % md
            k = k // 2
        return res % md

    @classmethod
    def inv(cls, input_num: int, md: int = p) -> int:
        """
        返回输入值在模意义下的逆元

        :param input_num: 输入值
        :param md: 模数，默认为 p
        :return: 模意义下的逆元
        """
        k = md - 2
        res = 1
        tmp = input_num % md
        while k > 0:
            if k % 2 == 1:
                res = res * tmp % md
            tmp = tmp * tmp % md
            k = k // 2
        return res % md

    @classmethod
    def curve_add(cls, p1: Tuple[int, int], p2: Tuple[int, int]) -> Tuple[int, int]:
        """
        基于椭圆曲线 y^2=x^3+7 上两点的加法。

        :param p1: 一个点
        :param p2: 一个点
        :return: 两点求和结果
        """
        # 如果是 0, 0 直接返回另一个
        if p1 == cls.INF:
            return p2
        if p2 == cls.INF:
            return p1

        # 相加为 INF 处理
        if p1[0] == p2[0]:
            if (p1[1] + p2[1]) % cls.p == 0:
                return cls.INF

        # 计算斜率
        if (p1[0] == p2[0]) and (p1[1] == p2[1]):
            k = (3 * p1[0] * p1[0]) % cls.p * cls.inv(2 * p1[1]) % cls.p
        else:
            k = (p2[1] - p1[1] + cls.p) % cls.p * \
                cls.inv((p2[0] - p1[0] + cls.p) % cls.p) % cls.p

        # 计算坐标
        x3 = (k * k + 2 * cls.p - p1[0] - p2[0]) % cls.p
        y3 = (k * (p1[0] - x3 + cls.p) + cls.p - p1[1]) % cls.p
        return x3, y3

    @classmethod
    def curve_mul(cls, x_in: Tuple[int, int], k: int) -> Tuple[int, int]:
        """
        椭圆曲线 y^2=x^3+7 上乘法，基于快速加法实现

        :param x_in: 输入的点 x
        :param k: 倍数 k
        :return: 点 kx
        """
        r = k
        res = cls.INF
        tmp = x_in
        while r > 0:
            if r % 2 == 1:
                res = cls.curve_add(res, tmp)
            tmp = cls.curve_add(tmp, tmp)
            r = r // 2
        return res

    @classmethod
    def get_wif_from_private_key(cls, input_str: str) -> str:
        """
        由未压缩私匙生成压缩私匙 wif

        :param input_str: 未压缩私匙
        :return: 压缩私匙
        """

        input_str = '80' + input_str + '01'
        h = my_sha256(my_sha256(input_str, True, True), True, True)
        input_str += h[0:8]
        bits = b''
        for i in range(0, len(input_str), 2):
            num = (int(input_str[i], 16) << 4) + (int(input_str[i + 1], 16))
            bits += struct.pack('<B', num)
        return base58.b58encode(bits).decode()

    @classmethod
    def get_private_key_from_wif(cls, input_str: str) -> str:
        """
        由压缩私匙 wif 生成私匙

        :param input_str: 压缩私匙
        :return: 未压缩私匙
        """
        bits = base58.b58decode(input_str.encode())
        bits = bits[1:-5]
        out_str = ""
        for i in range(32):
            out_str += hex(bits[i] // 16)[2:] + hex(bits[i] % 16)[2:]
        return out_str

    @classmethod
    def get_public_key_from_private_key(cls, private_key: str, is_compressed: bool = False) -> Tuple[int, int]:
        """
        由私匙导出公匙，返回未压缩公匙二元组

        :param private_key: 私匙
        :param is_compressed: 私匙是否为压缩私匙
        :return: 未压缩公匙
        """
        if private_key[0:2] == "0x":
            private_key = private_key[2:]
        if is_compressed:
            key = int(cls.get_private_key_from_wif(private_key), 16)
        else:
            key = int(private_key, 16)
        return cls.curve_mul(cls.g, key)

    @classmethod
    def get_compressed_public_key_from_public_key(cls, public_key: Tuple[int, int]) -> str:
        """
        由未压缩公匙获得压缩公匙

        :param public_key: 未压缩公匙
        :return: 压缩公匙
        """
        x, y = public_key
        compressed_key = ""
        if y % 2 == 0:
            compressed_key += "02"
        else:
            compressed_key += "03"
        num_str = hex(x)[2:]
        return compressed_key + num_str

    @classmethod
    def get_public_key_from_compressed_public_key(cls, compressed_key: str) -> Tuple[int, int]:
        """
        由压缩公匙获得未压缩公匙

        :param public_key: 压缩公匙
        :return: 未压缩公匙
        """
        y_flag = int(compressed_key[:2], base=16) % 2
        _x = int(compressed_key[2:], base=16)
        x = (_x ** 3 + 7) % ECDSA.p

        def cipolla(x: int) -> int:
            """
            利用 Cipolla 求二次剩余

            """
            class cp:
                def __init__(self, r: int, i: int) -> None:
                    self.real = r
                    self.imag = i

            def cpmul(a: cp, b: cp, w: int) -> cp:
                ans = cp(0, 0)
                ans.real = ((a.real * b.real % ECDSA.p + a.imag * b.imag %
                             ECDSA.p * w % ECDSA.p) % ECDSA.p + ECDSA.p) % ECDSA.p
                ans.imag = ((a.real * b.imag % ECDSA.p + a.imag *
                             b.real % ECDSA.p) % ECDSA.p + ECDSA.p) % ECDSA.p
                return ans

            while True:
                a = random.randint(1, ECDSA.p - 1)
                w = ((a * a % ECDSA.p - x) % ECDSA.p + ECDSA.p) % ECDSA.p
                if ECDSA.quick_pow(w, (ECDSA.p - 1) // 2) == ECDSA.p - 1:
                    break

            x = cp(a, 1)
            y = cp(1, 0)
            b = (ECDSA.p + 1) // 2
            while b > 0:
                if b % 2 == 1:
                    y = cpmul(y, x, w)
                x = cpmul(x, x, w)
                b = b // 2
            return y.real % ECDSA.p

        y = cipolla(x)
        if y % 2 != y_flag:
            y = ECDSA.p - y
        return _x, y

    @classmethod
    def get_address_from_compressed_public_key(cls, compressed_key: str) -> str:
        """
        由压缩公匙生成地址

        :param compressed_key: 压缩公匙
        :return: 地址
        """
        # part 1: 对 33 位压缩公匙 -> sha256 -> ripemd160
        sha = my_sha256(compressed_key, True, True)
        hash160 = hashlib.new("ripemd160", int(
            sha, base=16).to_bytes(length=32, byteorder='big'))
        hash160 = hash160.hexdigest()
        hash160 = "00" + hash160
        # part 2: 校验码由 part 1 两次 hash 得到
        verify_code = my_sha256(my_sha256(hash160, True, True), True, True)[:8]
        sum_str = hash160 + verify_code
        bits = b''
        for i in range(0, len(sum_str), 2):
            num = (int(sum_str[i], 16) << 4) + (int(sum_str[i + 1], 16))
            bits += struct.pack('<B', num)
        return base58.b58encode(bits).decode()

    @classmethod
    def gen_signature(cls, input_str: str, key: int) -> Tuple[int, int]:
        """
        根据私匙生成签名

        生成过程：
            一. 产生 160 比特随机数 k

            二. 计算 P = k * g

            三. P 的横坐标即为 R

            四. 利用 sha1 计算原信息哈希值，得到 160 位整数 z

            五. 计算 S = k^(-1) * (z + private_key * R) % p

            六. 签名 R,S 一共是 320 比特

        :param input_str: 待签名的信息
        :param key: 私匙，整数格式
        :return: 签名 R,S
        """
        k = random.randrange(2 ** 150, 2 ** 160, 1)
        P = cls.curve_mul(cls.g, k)
        R = P[0]
        z = int(my_sha1(input_str), 16)
        S = cls.inv(k, cls.order) * ((z + key * R) % cls.order) % cls.order
        return R, S

    @classmethod
    def verify_signature(cls, input_str: str, key: Tuple[int, int], sign: Tuple[int, int]) -> bool:
        """
        根据公匙验证签名与信息

        :param input_str: 待验证的信息
        :param key: 公匙
        :param sign: 待验证的签名
        :return: 若签名有效则返回 True，否则为 False
        """
        R, S = sign
        z = int(my_sha1(input_str), 16)
        P = cls.curve_add(cls.curve_mul(cls.g, cls.inv(S, cls.order) * z),
                          cls.curve_mul(key, cls.inv(S, cls.order) * R))
        if P[0] == R:
            return True
        else:
            return False
