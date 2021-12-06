# -*- coding: utf-8 -*-
from PyQt5.QtCore import QLine, QRegExp, Qt, QTime, QTimer
from PyQt5.QtGui import QDoubleValidator, QFont, QRegExpValidator, QValidator
from PyQt5.QtWidgets import QApplication, QGridLayout, QWidget, QFormLayout, QLineEdit, QPushButton, QHBoxLayout, \
    QVBoxLayout, QTabWidget, QMessageBox, QLabel, QFrame, QScrollArea, QInputDialog
from GUI import BlockWidget
from blockchain.block import Block, Blockchain
from blockchain.user import User
# from blockchain.transaction import make_deal
from utils.db import DB
from utils.ecdsa import ECDSA
import logging
from functools import partial
from blockchain.function import make_deal, dig_source, create_user


class MainWindow(QTabWidget):
    def __init__(self, db: DB):
        super().__init__()

        # 存储信息定义
        self.db = db
        self.all_user = []  # type: list[User]
        self.blockchain = Blockchain()

        # 主界面
        self.setWindowTitle("C coin——全新的数字货币")
        self.resize(1200, 800)

        # 页面一：欢迎页面
        self.welcome_widget = QWidget()
        self.time = QLabel()
        self.timer = QTimer()

        # 页面二：区块页面
        self.block_widget = QWidget()
        self.tab2_layout = QHBoxLayout()
        self.blocksBox = QWidget()
        self.block_scroll = QScrollArea()

        # 页面三：账户页面
        self.account_widget = QWidget()
        self.tab3_layout = QHBoxLayout()
        self.user_scroll = QScrollArea()
        self.usersBox = QWidget()
        self.new_usersBox = QWidget()

        # 页面四：交易页面
        self.deal_widget = QWidget()
        self.tab4_layout = QFormLayout()
        self.le_wif = QLineEdit()
        self.le_address = QLineEdit()
        self.le_number = QLineEdit()

        # 初始化操作
        self.func()

    def func(self):
        self.addTab(self.welcome_widget, "欢迎页面")
        self.addTab(self.block_widget, "区块信息")
        self.addTab(self.account_widget, "账户信息")
        self.addTab(self.deal_widget, "交易页面")

        blockchain = Blockchain()
        self.set_blockchain(blockchain)

        self.set_tab1_ui()
        self.set_tab2_ui()
        self.set_tab3_ui()
        self.set_tab4_ui()

    def set_tab1_ui(self):
        """
            tab1：欢迎界面
        """
        layout = QVBoxLayout()
        wel = QLabel()
        wel.setText("欢迎使用 C-coin 系统")
        wel.setFont(QFont("Microsoft YaHei", 20, 60))
        wel.setAlignment(Qt.AlignCenter)
        self.time.setText(QTime.currentTime().toString())
        self.time.setFont(QFont("Microsoft YaHei", 15, 60))
        self.time.setAlignment(Qt.AlignCenter)
        layout.addStretch(10)
        layout.addWidget(wel, 0, Qt.AlignHCenter)
        layout.addStretch(1)
        layout.addWidget(self.time, 0, Qt.AlignHCenter)
        layout.addStretch(10)
        self.welcome_widget.setLayout(layout)

        self.timer.timeout.connect(self.clock_update)
        self.timer.start(1000)

    def clock_update(self):
        """
            tab1：更新时钟
        """
        self.time.setText(QTime.currentTime().toString())

    def set_tab2_ui(self):
        """
            tab2：区块信息页面:
        """
        # 左侧：区块链显示
        self.blocksBox.setMinimumSize(
            750, max(800, 20 + len(self.blockchain.blockList) * 215))
        self.block_scroll.setAlignment(Qt.AlignCenter)
        self.block_scroll.setWidget(self.blocksBox)
        self.block_scroll.setFrameShape(QFrame.Box)
        self.block_scroll.setMinimumWidth(750)
        self.tab2_layout.addWidget(self.block_scroll, 3)

        # 右侧：空间按钮

        buttonBox = QFrame()
        buttonBox.setFrameShape(QFrame.Box)
        btn_createBlock = QPushButton()
        btn_createBlock.setParent(buttonBox)
        btn_createBlock.setText("创建新区块")
        btn_createBlock.setFixedSize(200, 80)
        btn_createBlock.move(45, 50)
        self.tab2_layout.addWidget(buttonBox, 1)
        self.block_widget.setLayout(self.tab2_layout)
        self.blcokList = []

        btn_createBlock.clicked.connect(self.create_block_clicked)
        self.timer.timeout.connect(self.blocksbox_update)

    def blocksbox_update(self):
        """
            tab2：更新左侧区块展示
        """
        self.blockList = self.db.select("SELECT * FROM 区块 ORDER BY 时间戳;", True)
        self.blocksBox = QWidget()
        self.blocksBox.setMinimumSize(
            750, max(800, 20 + len(self.blockList) * 215))

        for i in range(len(self.blockList)):
            block = self.blockList[i]
            a = BlockWidget.QBlockWidget()
            a.setParent(self.blocksBox)
            a.move(0, 10 + i * 215)
            a.set_hash(block[0])
            a.set_time(str(block[3]))
            a.set_prehash(block[1])
            a.set_merkle(block[2])

        self.blocksBox.update()
        oldval = self.block_scroll.verticalScrollBar().value()
        oldmaxval = self.block_scroll.verticalScrollBar().maximum()
        self.block_scroll.setMinimumWidth(750)
        self.block_scroll.setWidget(self.blocksBox)
        if oldmaxval == 0:
            self.block_scroll.verticalScrollBar().setValue(0)
        else:
            self.block_scroll.verticalScrollBar().setValue(
                oldval * self.block_scroll.verticalScrollBar().maximum() / oldmaxval)

    def set_blockchain(self, new_blockchain):
        """
            设置区块链
        """
        self.blockchain = new_blockchain
        self.blocksbox_update()

    def add_block(self, new_block: Block) -> None:
        """
            添加新区块
        """
        self.blockchain.add_block(new_block)
        self.blocksbox_update()

    def create_block_clicked(self):
        input_address, okPressed = QInputDialog.getText(
            self, "确认打工人", "请输入打工人的地址", QLineEdit.Normal, "")
        found = -1
        all_user = self.db.select("SELECT * FROM 用户;")
        for i in range(len(all_user)):
            if ECDSA.get_address_from_compressed_public_key(all_user[i][0]) == input_address:
                found = i
                break
        if found == -1:
            logging.warning("未找到用户信息，新区块不会被创建。")
        else:
            logging.info("已找到对应用户，正在创建区块")
        if okPressed:
            if found != -1:
                dig_source(all_user[found][0], self.db)
                QMessageBox.information(self, "新区块已创立", "好耶，是新区块！", QMessageBox.Yes | QMessageBox.No,
                                        QMessageBox.Yes)
                # self.add_block(Block(input_address))
                self.usersbox_update()
            else:
                QMessageBox.information(self, "新区块创立失败", "随便输一个可是过不了的 ╮(╯▽╰)╭ ", QMessageBox.Yes | QMessageBox.No,
                                        QMessageBox.Yes)

    def set_tab3_ui(self):
        """
            tab3：用户界面
        """
        # 左侧：User 显示

        self.user_scroll.setAlignment(Qt.AlignCenter)
        self.user_scroll.setFrameShape(QFrame.Box)
        self.tab3_layout.addWidget(self.user_scroll, 3)

        self.frame_list = []
        self.lb_name_list = []
        self.lb_addr_list = []
        self.lb_money_list = []
        self.bn_copy_list = []

        self.usersbox_update("")

        ln_name = QLineEdit()
        ln_name.setValidator(QRegExpValidator(
            QRegExp("([a-zA-Z0-9]+)(([ ]([a-zA-Z0-9]+))*)$")))
        ln_addr = QLineEdit()
        ln_addr.setValidator(QRegExpValidator(
            QRegExp("([a-zA-Z0-9]+)(([ ]([a-zA-Z0-9]+))*)$")))
        ln_money_min = QLineEdit()
        ln_money_min.setValidator(QDoubleValidator())
        ln_money_max = QLineEdit()
        ln_money_max.setValidator(QDoubleValidator())

        self.timer.timeout.connect(
            lambda: self.usersbox_update(ln_name.text(), ln_addr.text(), (ln_money_min.text(), ln_money_max.text())))

        # 右侧：筛选与新增用户按钮

        buttonBox = QFrame()
        buttonBox.setFrameShape(QFrame.Box)

        lb_name = QLabel()
        lb_name.setText("用户名：")
        lb_name.setParent(buttonBox)
        lb_name.setFixedSize(150, 30)
        lb_name.move(30, 50)

        ln_name.setParent(buttonBox)
        ln_name.setFixedSize(150, 30)
        ln_name.move(120, 50)

        lb_addr = QLabel()
        lb_addr.setText("公钥：")
        lb_addr.setParent(buttonBox)
        lb_addr.setFixedSize(150, 30)
        lb_addr.move(30, 100)

        ln_addr.setParent(buttonBox)
        ln_addr.setFixedSize(150, 30)
        ln_addr.move(120, 100)

        lb_money = QLabel()
        lb_money.setText("持有金额：")
        lb_money.setParent(buttonBox)
        lb_money.setFixedSize(150, 30)
        lb_money.move(30, 150)

        ln_money_min.setParent(buttonBox)
        ln_money_min.setFixedSize(60, 30)
        ln_money_min.move(120, 150)

        lb_money_to = QLabel()
        lb_money_to.setParent(buttonBox)
        lb_money_to.setText("-")
        lb_money_to.setFixedSize(30, 30)
        lb_money_to.move(190, 150)

        ln_money_max.setParent(buttonBox)
        ln_money_max.setFixedSize(60, 30)
        ln_money_max.move(210, 150)

        ln_money_min.setParent(buttonBox)
        ln_money_max.setParent(buttonBox)

        btn_createUser = QPushButton()
        btn_createUser.setParent(buttonBox)
        btn_createUser.setText("创建新账户")
        btn_createUser.setFixedSize(200, 80)
        btn_createUser.move(45, 250)
        self.tab3_layout.addWidget(buttonBox, 1)

        btn_createUser.clicked.connect(self.create_user_clicked)

        self.account_widget.setLayout(self.tab3_layout)

    def create_user_clicked(self):
        """
            tab3：点击创建用户事件
        """
        _name, ok = QInputDialog.getText(self, "输入名字", "请输入用户姓名")
        if not ok:
            logging.info("用户取消创建")
            return
        reg = QRegExp("([a-zA-Z0-9]+)(([ ]([a-zA-Z0-9]+))*)$")
        if not reg.exactMatch(_name):
            logging.info("用户名格式错误")
            QMessageBox.information(
                self, "用户名格式错误", "用户名只能包含连续的字母数字段，每段以一个空格隔开。\n用户名不能为空。")
            return

        new_user = User(create_user(_name, self.db))
        info = QMessageBox(self)
        info.setIcon(QMessageBox.Icon.Information)
        info.setWindowTitle("新用户已创立")
        info.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextSelectableByMouse)
        info.setText("好耶，是新用户！记住你的信息：\n" +
                     "地址：" + new_user.address + "\n" +
                     "压缩私匙 wif：" + new_user.wif)
        info.setStandardButtons(QMessageBox.Yes)
        info.setDefaultButton(QMessageBox.Yes)
        info.exec()

        self.all_user.append(new_user)
        logging.info("创建用户完毕。")

    def usersbox_update(self, info: str = "", pub: str = "", money: tuple = (0, 1e18)):
        """
            tab3：更新用户框
        """
        sql = "SELECT * FROM 用户 WHERE 用户名 LIKE '" + info + "%'"
        sql += "AND 公钥 LIKE '" + pub + "%'"
        if money[0] == "":
            money = (0, money[1])
        if money[1] == "":
            money = (money[0], 1e18)
        sql += "AND 余额 BETWEEN " + str(money[0]) + " AND " + str(money[1])
        users = self.db.select(sql, True)

        self.usersBox = QWidget()
        self.usersBox.setMinimumSize(
            750, max(800, 20 + len(users) * 215))

        self.frame_list.clear()
        self.lb_name_list.clear()
        self.lb_addr_list.clear()
        self.lb_money_list.clear()
        self.bn_copy_list.clear()

        for i in range(len(users)):
            addr = ECDSA.get_address_from_compressed_public_key(users[i][0])
            money = users[i][2]
            name = users[i][1]
            if not isinstance(name, str):
                logging.warning("地址为{}的用户没有对应用户名，以default替代".format(addr))
                name = "default"
            self.frame_list.append(QFrame())
            self.frame_list[i].setParent(self.usersBox)
            self.frame_list[i].setFixedSize(740, 220)
            self.frame_list[i].setFrameShape(QFrame.Box)
            self.frame_list[i].setContentsMargins(10, 10, 10, 10)
            self.frame_list[i].move(0, 10 + i * 215)

            self.lb_name_list.append(QLabel())
            self.lb_name_list[i].setText("姓名：" + name)
            self.lb_name_list[i].setParent(self.frame_list[-1])
            self.lb_addr_list.append(QLabel())
            self.lb_addr_list[i].setText("地址：" + addr)
            self.lb_addr_list[i].setParent(self.frame_list[-1])
            self.lb_money_list.append(QLabel())
            self.lb_money_list[i].setText("持有金额：" + str(money))
            self.lb_money_list[i].setParent(self.frame_list[-1])
            font = QFont("Microsoft YaHei", 10, 60)
            self.lb_name_list[i].setFont(font)
            self.lb_addr_list[i].setFont(font)
            self.lb_money_list[i].setFont(font)
            self.lb_name_list[i].move(20, 60)
            self.lb_addr_list[i].move(20, 100)
            self.lb_money_list[i].move(20, 140)
            self.lb_addr_list[i].setTextInteractionFlags(
                Qt.TextInteractionFlag.TextSelectableByMouse)

            self.bn_copy_list.append(QPushButton())
            self.bn_copy_list[i].setText("复制")
            self.bn_copy_list[i].setParent(self.frame_list[-1])
            self.bn_copy_list[i].setFont(font)
            self.bn_copy_list[i].move(
                self.frame_list[i].width() - 120, 100)

        self.usersBox.update()

        for i in range(len(self.bn_copy_list)):
            self.bn_copy_list[i].clicked.connect(
                partial(self.bn_copy_clicked, self.bn_copy_list[i].parent().findChildren(QLabel)[1].text()))

        oldval = self.user_scroll.verticalScrollBar().value()
        oldmaxval = self.user_scroll.verticalScrollBar().maximum()
        self.user_scroll.setMinimumWidth(750)
        self.user_scroll.setWidget(self.usersBox)
        if oldmaxval == 0:
            self.user_scroll.verticalScrollBar().setValue(0)
        else:
            self.user_scroll.verticalScrollBar().setValue(
                oldval * self.user_scroll.verticalScrollBar().maximum() / oldmaxval)

    def bn_copy_clicked(self, ele: str) -> None:
        """
            tab3：复制按钮点击事件
        """
        ele = ele.split('：')[1]
        clipboard = QApplication.clipboard()
        clipboard.setText(ele)

    def set_tab4_ui(self):
        """
            tab4：交易页面
        """
        btn_deal = QPushButton()
        btn_deal.setText("点我进行交易")
        btn_deal.clicked.connect(self.deal_clicked)
        self.tab4_layout.addRow("你的压缩私匙 wif：", self.le_wif)
        self.tab4_layout.addRow("转账对象的地址：", self.le_address)
        self.tab4_layout.addRow("转账金额：", self.le_number)
        self.tab4_layout.addRow(btn_deal)

        self.deal_widget.setLayout(self.tab4_layout)

    def deal_clicked(self):
        """
            tab4：点击交易事件
        """
        occurred = False
        for u in self.all_user:
            if u.wif == self.le_wif.text():
                occurred = True
                break
        to_pos = -1
        for i in range(len(self.all_user)):
            if self.all_user[i].address == self.le_address.text():
                to_pos = i
                break
        if to_pos == -1 or occurred is False:
            if not occurred:
                QMessageBox.information(self, "无法交易", "冒充别人充钱是不好的(￢_￢)。", QMessageBox.Yes | QMessageBox.No,
                                              QMessageBox.Yes)
            elif to_pos == -1:
                QMessageBox.information(self, "无法交易", "请确定你的地址输入正确(￢_￢)。", QMessageBox.Yes | QMessageBox.No,
                                              QMessageBox.Yes)
        else:
            QMessageBox.information(self, "交易成功", "请查看账户来确认完成交易。", QMessageBox.Yes | QMessageBox.No,
                                          QMessageBox.Yes)
            make_deal(User(self.le_wif.text()), self.le_address.text(),
                      int(self.le_number.text(), 10), self.blockchain)
            self.blocksbox_update()
            self.usersbox_update()
