import blockchain
import GUI
from blockchain import user
from utils import ecdsa
import utils.db
from utils.ecdsa import ECDSA
from blockchain import function
'''
这个文件测试function的两个函数
'''
if __name__ == '__main__':
    # 连接数据库
    db = utils.db.DB("localhost", _passwd = 'csnb')
    # 建表
    db.create_tables(rebuild=True)
    # 创建两个用户
    # bright_private_key = ECDSA().private_key
    # '''
    # 问题：为什么private_key也是个string？
    # '''
    # print("我的私钥"+str(bright_private_key))
    # bright_wif = ECDSA.get_wif_from_private_key(str(bright_private_key))
    # print("下面用我的wif生成用户")
    # '''
    # 问题：用户创建时，要输入的wif为str
    # '''
    # bright = user.User.create_user(bright_wif)

    # 创建两个用户
    bright_wif = user.User.create_user('bright')
    lonlyn_wif = user.User.create_user('lonlyn')
    bright = user.User(bright_wif)
    lonlyn = user.User(lonlyn_wif)
    # 挖两个区块
    function.dig_source(bright.compressed_public_key)
    function.dig_source(lonlyn.compressed_public_key)
    # 两人交易
    function.make_deal(bright, lonlyn.compressed_public_key, 10)
    # 打包这个交易
    function.dig_source(bright.compressed_public_key)

