import logging
import pymysql


class DB(object):
    def __init__(self, _host: str, _port: int = 3306, _user: str = "root", _passwd: str = "") -> None:
        """
        创建新数据库
        """
        super().__init__()
        self.conn = pymysql.connect(
            host=_host,
            port=_port,
            user=_user,
            passwd=_passwd,
            charset="utf8"
        )
        self.cursor = self.conn.cursor()
        self.cursor.execute("CREATE DATABASE IF NOT EXISTS C_Coin")
        self.conn.select_db("C_coin")
        self.create_tables(False)

    def __del__(self):
        self.cursor.close()
        self.conn.close()

    def select(self, inst: str, format: bool = False) -> any:
        """
        查询操作。

        :param inst: 查询指令
        :param format: 返回格式，若为 True 返回 list，否则为 tuple
        """
        logging.debug("执行SQL: " + " ".join(inst.split()))
        try:
            # 断线重连
            self.conn.ping(reconnect=True)
            self.cursor.execute(inst)
            res = self.cursor.fetchall()
            if format:
                reslist = []
                for ele in res:
                    reslist.append(ele)
                return reslist
            else:
                return res

        except Exception as e:
            logging.warning("查询SQL错误：{}".format(e))
            # print("出现错误：{}".format(e))
            return []

    def execute(self, inst: str) -> None:
        """
        增删改操作。

        :param inst: 执行的语句
        """
        logging.debug("执行SQL: " + " ".join(inst.split()))
        try:
            # 断线重连
            self.conn.ping(reconnect=True)
            self.cursor.execute(inst)
            self.conn.commit()
        except Exception as e:
            # 回滚所有更改
            print(inst)
            self.conn.rollback()
            logging.warning("执行SQL出现错误：{}".format(e))

    def create_tables(self, rebuild: bool = False):
        """
        初始化，创建所需要的的表

        :param rebuild: 是否要重新重新构建，如果为 True 那么原先同名的表将被删除，之后重新建立，原来的数据会被丢弃。
        """
        if rebuild:
            self.execute("DROP TABLE IF EXISTS 库存")
            self.execute("DROP TABLE IF EXISTS 购买")
            self.execute("DROP TABLE IF EXISTS 应用程序")
            self.execute("DROP TABLE IF EXISTS 输入")
            self.execute("DROP TABLE IF EXISTS 输出")
            self.execute("DROP TABLE IF EXISTS 店铺")
            self.execute("DROP TABLE IF EXISTS 用户")
            self.execute("DROP TABLE IF EXISTS 交易")
            self.execute("DROP TABLE IF EXISTS 区块")

        self.execute(
            "CREATE TABLE IF NOT EXISTS 区块 (\
                区块哈希 VARCHAR(100) PRIMARY KEY,\
                前驱哈希 VARCHAR(100),\
                Merkle哈希 VARCHAR(100),\
                时间戳 TIMESTAMP(6) DEFAULT CURRENT_TIMESTAMP(6),\
                Nonce VARCHAR(100) \
            )"
        )
        self.execute(
            "CREATE TABLE IF NOT EXISTS 交易 (\
                交易哈希 VARCHAR(100) PRIMARY KEY,\
                区块哈希 VARCHAR(100),\
                FOREIGN KEY (区块哈希) REFERENCES 区块(区块哈希)\
            )"
        )
        self.execute(
            "CREATE TABLE IF NOT EXISTS 用户 (\
                公钥 VARCHAR(100) PRIMARY KEY,\
                用户名 VARCHAR(100),\
                余额 FLOAT\
            )"
        )
        self.execute(
            "CREATE TABLE IF NOT EXISTS 店铺 (\
                店铺编号 VARCHAR(100) PRIMARY KEY,\
                店铺名称 VARCHAR(100), \
                公钥 VARCHAR(100), \
                FOREIGN KEY (公钥) REFERENCES 用户(公钥) \
            )"
        )
        self.execute(
            "CREATE TABLE IF NOT EXISTS 输出 (\
                输出哈希 VARCHAR(100) PRIMARY KEY,\
                花费标志 boolean,\
                数额 FLOAT,\
                交易哈希 VARCHAR(100), \
                公钥 VARCHAR(100), \
                收款地址 VARCHAR(100),\
                FOREIGN KEY (交易哈希) REFERENCES 交易(交易哈希), \
                FOREIGN KEY (公钥) REFERENCES 用户(公钥) \
            )"
        )
        self.execute(
            "CREATE TABLE IF NOT EXISTS 输入 (\
                签名 VARCHAR(200) PRIMARY KEY,\
                输出哈希 VARCHAR(100),\
                交易哈希 VARCHAR(100),\
                公钥 VARCHAR(100),\
                FOREIGN KEY (输出哈希) REFERENCES 输出(输出哈希),\
                FOREIGN KEY (交易哈希) REFERENCES 交易(交易哈希),\
                FOREIGN KEY (公钥) REFERENCES 用户(公钥) \
            )"
        )
        self.execute(
            "CREATE TABLE IF NOT EXISTS 应用程序 (\
                应用编号 VARCHAR(100) PRIMARY KEY,\
                应用名称 VARCHAR(100),\
                应用大小 INT(100),\
                应用版本 VARCHAR(100),\
                使用系统 VARCHAR(100),\
                价格 FLOAT,\
                销量 INT,\
                店铺编号 VARCHAR(100),\
                FOREIGN KEY (店铺编号) REFERENCES 店铺(店铺编号)\
            )"
        )
        # self.execute(
        #     "CREATE TABLE IF NOT EXISTS 购买 (\
        #         公钥 VARCHAR(100),\
        #         收款地址 VARCHAR(100),\
        #         应用编号 VARCHAR(100),\
        #         PRIMARY KEY (公钥,收款地址,应用编号),\
        #         FOREIGN KEY (公钥) REFERENCES 用户(公钥),\
        #         FOREIGN KEY (收款地址) REFERENCES 店铺(收款地址),\
        #         FOREIGN KEY (应用编号) REFERENCES 应用程序(应用编号)\
        #     )"
        # )
        self.execute(
            "CREATE TABLE IF NOT EXISTS 库存 (\
                公钥 VARCHAR(100),\
                应用编号 VARCHAR(100),\
                入库时间 TIMESTAMP DEFAULT CURRENT_TIMESTAMP,\
                PRIMARY KEY (公钥,应用编号),\
                FOREIGN KEY (公钥) REFERENCES 用户(公钥),\
                FOREIGN KEY (应用编号) REFERENCES 应用程序(应用编号)\
            )"
        )
