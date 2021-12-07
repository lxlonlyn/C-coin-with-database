import blockchain
import GUI
from utils import ecdsa
from blockchain import user
import utils.db
from utils.ecdsa import ECDSA
from blockchain import function
'''
这个文件测试function的两个函数
'''
if __name__ == '__main__':
    # 连接数据库
    db = utils.db.DB("localhost", _passwd='csnb')
    # 建表
    db.create_tables(rebuild=True)

    # 创建两个用户
    bright_wif = function.create_user('bright', db)
    lonlyn_wif = function.create_user('lonlyn', db)
    bright = user.User(bright_wif)
    lonlyn = user.User(lonlyn_wif)
    # 挖两个区块
    function.dig_source(bright.compressed_public_key, db)
    function.dig_source(lonlyn.compressed_public_key, db)
    # 两人交易
    function.make_deal(bright, lonlyn.compressed_public_key, 1000, db)
    # 打包这个交易
    function.dig_source(bright.compressed_public_key, db)

    print(function.update_uxto(bright.compressed_public_key, db))
    print(function.update_uxto(lonlyn.compressed_public_key, db))

    # lonlyn开一个店
    function.open_a_store(lonlyn.compressed_public_key, "lonlyn的韭菜收割处", db)
    # lonlyn上架一个app
    function.put_on_shelves("脂腹饱", '114514', '1.0', 'iOS', 30, '0001', db)
    # Bright买一个app
    function.buy_app(bright, '0001', db)
    # 展示当前余额
    print(function.update_uxto(bright.compressed_public_key, db))
    print(function.update_uxto(lonlyn.compressed_public_key, db))
    # 修改店铺名称
    function.change_store_name('0001', '爷收完韭菜啦', db)
