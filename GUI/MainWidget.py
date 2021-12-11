# -*- coding: utf-8 -*-
from PyQt5 import QtGui
from PyQt5.QtCore import QDateTime, QRegExp, Qt, QTime, QTimer
from PyQt5.QtGui import QDoubleValidator, QFont, QRegExpValidator
from PyQt5.QtWidgets import QApplication, QDateTimeEdit, QWidget, QLineEdit, QPushButton, QHBoxLayout, \
    QVBoxLayout, QTabWidget, QMessageBox, QLabel, QFrame, QScrollArea, QInputDialog, QDialog, QFormLayout, \
    QDialogButtonBox
from GUI import BlockWidget
from GUI.CustomerWidget import QCustomerWidget
from blockchain.user import User
from utils.db import DB
from utils.ecdsa import ECDSA
import logging
from functools import partial
from blockchain.function import dig_source, create_user, open_a_store


class MainWindow(QTabWidget):
    def __init__(self, db: DB):
        super().__init__()

        # 存储信息定义
        self.db = db
        self.all_user = []  # type: list[User]

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
        self.le_time_start = QDateTimeEdit()
        self.le_time_end = QDateTimeEdit()
        self.blockList = []

        # 页面三：账户页面
        self.account_widget = QWidget()
        self.tab3_layout = QHBoxLayout()
        self.user_scroll = QScrollArea()
        self.usersBox = QWidget()
        self.new_usersBox = QWidget()
        self.userframe_list = []
        self.lb_username_list = []
        self.lb_useraddr_list = []
        self.lb_usermoney_list = []
        self.bn_useraddr_copy_list = []

        # 页面四：店铺页面
        self.mall_widget = QWidget()
        self.tab4_layout = QHBoxLayout()
        self.mallsBox = QWidget()
        self.mall_scroll = QScrollArea()
        self.mallList = []
        self.mallframe_list = []
        self.lb_mallname_list = []
        self.lb_mallslogan_list = []
        self.bn_mall_customer_list = []
        self.bn_mall_boss_list = []
        self.customer_widget = QCustomerWidget()

        # 初始化操作
        self.func()

    def func(self):
        self.addTab(self.welcome_widget, "欢迎页面")
        self.addTab(self.block_widget, "区块信息")
        self.addTab(self.account_widget, "账户信息")
        self.addTab(self.mall_widget, "店铺信息")

        self.set_tab1_ui()
        self.set_tab2_ui()
        self.set_tab3_ui()
        self.set_tab4_ui()
        self.setCurrentIndex(0)

    def closeEvent(self, a0: QtGui.QCloseEvent) -> None:
        self.customer_widget.close()
        a0.accept()

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
        btn_createBlock.setText("挖矿")
        btn_createBlock.setFixedSize(200, 80)
        btn_createBlock.move(45, 50)
        self.tab2_layout.addWidget(buttonBox, 1)

        lb_timeRange = QLabel()
        lb_timeRange.setText("选择时间区间")
        lb_timeRange.setParent(buttonBox)
        lb_timeRange.setFixedSize(200, 20)
        lb_timeRange.move(45, 180)
        lb_timeRange.setAlignment(Qt.AlignCenter)

        lb_time_start = QLabel()
        lb_time_start.setText("从：")
        lb_time_start.setParent(buttonBox)
        lb_time_start.move(45, 230)

        self.le_time_start.setFixedSize(165, 30)
        self.le_time_start.setParent(buttonBox)
        self.le_time_start.setDisplayFormat("yyyy:MM:dd HH:mm")
        self.le_time_start.setCalendarPopup(True)
        self.le_time_start.move(80, 220)

        lb_time_end = QLabel()
        lb_time_end.setText("至：")
        lb_time_end.setParent(buttonBox)
        lb_time_end.move(45, 280)

        self.le_time_end.setFixedSize(165, 30)
        self.le_time_end.setParent(buttonBox)
        self.le_time_end.setDisplayFormat("yyyy:MM:dd HH:mm")
        self.le_time_end.setDateTime(QDateTime.currentDateTime())
        self.le_time_end.setCalendarPopup(True)
        self.le_time_end.move(80, 270)

        self.block_widget.setLayout(self.tab2_layout)
        self.blockList.clear()
        self.setCurrentIndex(1)
        self.blocksbox_update()

        btn_createBlock.clicked.connect(self.create_block_clicked)
        self.timer.timeout.connect(self.blocksbox_update)

    def blocksbox_update(self):
        """
            tab2：更新左侧区块展示
        """
        if self.currentIndex() != 1:
            return
        time1 = self.le_time_start.dateTime()
        time1 = time1.toString("yyyy-MM-dd hh:mm:ss")
        time2 = self.le_time_end.dateTime()
        time2 = time2.toString("yyyy-MM-dd hh:mm:ss")

        sql = "SELECT * FROM 区块 WHERE 时间戳 BETWEEN '"
        sql += time1 + "' AND '" + time2 + "' ORDER BY 时间戳;"
        self.blockList = self.db.select(sql, True)
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
                oldval * self.block_scroll.verticalScrollBar().maximum() // oldmaxval)

    def create_block_clicked(self):
        """
            tab2：点击挖矿事件
        """
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

        self.userframe_list.clear()
        self.lb_username_list.clear()
        self.lb_useraddr_list.clear()
        self.lb_usermoney_list.clear()
        self.bn_useraddr_copy_list.clear()

        self.setCurrentIndex(2)
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
        if self.currentIndex() != 2:
            return
        sql = "SELECT * FROM 用户 WHERE 用户名 LIKE '" + info + "%'"
        sql += " AND 公钥 LIKE '" + pub + "%'"
        if money[0] == "":
            money = (0, money[1])
        if money[1] == "":
            money = (money[0], 1e18)
        sql += " AND 余额 BETWEEN " + str(money[0]) + " AND " + str(money[1])
        users = self.db.select(sql, True)

        self.usersBox = QWidget()
        self.usersBox.setMinimumSize(
            750, max(800, 20 + len(users) * 215))

        self.userframe_list.clear()
        self.lb_username_list.clear()
        self.lb_useraddr_list.clear()
        self.lb_usermoney_list.clear()
        self.bn_useraddr_copy_list.clear()

        for i in range(len(users)):
            addr = ECDSA.get_address_from_compressed_public_key(users[i][0])
            money = users[i][2]
            name = users[i][1]
            if not isinstance(name, str):
                logging.warning("地址为{}的用户没有对应用户名，以default替代".format(addr))
                name = "default"
            self.userframe_list.append(QFrame())
            self.userframe_list[i].setParent(self.usersBox)
            self.userframe_list[i].setFixedSize(740, 220)
            self.userframe_list[i].setFrameShape(QFrame.Box)
            self.userframe_list[i].setContentsMargins(10, 10, 10, 10)
            self.userframe_list[i].move(0, 10 + i * 215)

            self.lb_username_list.append(QLabel())
            self.lb_username_list[i].setText("姓名：" + name)
            self.lb_username_list[i].setParent(self.userframe_list[-1])
            self.lb_useraddr_list.append(QLabel())
            self.lb_useraddr_list[i].setText("地址：" + addr)
            self.lb_useraddr_list[i].setParent(self.userframe_list[-1])
            self.lb_usermoney_list.append(QLabel())
            self.lb_usermoney_list[i].setText("持有金额：" + str(money))
            self.lb_usermoney_list[i].setParent(self.userframe_list[-1])
            font = QFont("Microsoft YaHei", 10, 60)
            self.lb_username_list[i].setFont(font)
            self.lb_useraddr_list[i].setFont(font)
            self.lb_usermoney_list[i].setFont(font)
            self.lb_username_list[i].move(20, 60)
            self.lb_useraddr_list[i].move(20, 100)
            self.lb_usermoney_list[i].move(20, 140)
            self.lb_useraddr_list[i].setTextInteractionFlags(
                Qt.TextInteractionFlag.TextSelectableByMouse)

            self.bn_useraddr_copy_list.append(QPushButton())
            self.bn_useraddr_copy_list[i].setText("复制")
            self.bn_useraddr_copy_list[i].setParent(self.userframe_list[-1])
            self.bn_useraddr_copy_list[i].setFont(font)
            self.bn_useraddr_copy_list[i].move(
                self.userframe_list[i].width() - 120, 100)

        self.usersBox.update()

        for i in range(len(self.bn_useraddr_copy_list)):
            self.bn_useraddr_copy_list[i].clicked.connect(
                partial(self.bn_copy_clicked, self.bn_useraddr_copy_list[i].parent().findChildren(QLabel)[1].text()))

        oldval = self.user_scroll.verticalScrollBar().value()
        oldmaxval = self.user_scroll.verticalScrollBar().maximum()
        self.user_scroll.setMinimumWidth(750)
        self.user_scroll.setWidget(self.usersBox)
        if oldmaxval == 0:
            self.user_scroll.verticalScrollBar().setValue(0)
        else:
            self.user_scroll.verticalScrollBar().setValue(
                oldval * self.user_scroll.verticalScrollBar().maximum() // oldmaxval)

    def bn_copy_clicked(self, ele: str) -> None:
        """
            tab3：复制按钮点击事件
        """
        ele = ele.split('：')[1]
        clipboard = QApplication.clipboard()
        clipboard.setText(ele)

    def set_tab4_ui(self):
        """
            tab4：店铺页面
        """
        # 左侧：店铺显示
        self.mall_scroll.setAlignment(Qt.AlignCenter)
        self.mall_scroll.setWidget(self.mallsBox)
        self.mall_scroll.setFrameShape(QFrame.Box)
        self.mall_scroll.setMinimumWidth(750)
        self.tab4_layout.addWidget(self.mall_scroll, 3)

        # 右侧：空间按钮
        buttonBox = QFrame()
        buttonBox.setFrameShape(QFrame.Box)
        btn_createMall = QPushButton()
        btn_createMall.setParent(buttonBox)
        btn_createMall.setText("创建新店铺")
        btn_createMall.setFixedSize(200, 80)
        btn_createMall.move(45, 50)
        self.tab4_layout.addWidget(buttonBox, 1)

        self.setCurrentIndex(3)
        self.mallsbox_update()

        btn_createMall.clicked.connect(self.create_mall_clicked)
        self.timer.timeout.connect(self.mallsbox_update)
        self.mall_widget.setLayout(self.tab4_layout)

    def create_mall_clicked(self):
        dialog = QDialog()
        dialog.setWindowTitle("创建店铺")
        dialog.setFixedSize(300, 140)
        form = QFormLayout(dialog)
        form.addRow(QLabel(text="请输入您的私钥和店铺期望的名称"))
        le_pri_key = QLineEdit(dialog)
        form.addRow(QLabel(text="私钥："), le_pri_key)
        le_mallname = QLineEdit(dialog)
        form.addRow(QLabel(text="名称："), le_mallname)
        buttonBox = QDialogButtonBox(QDialogButtonBox.Ok, Qt.Horizontal, dialog)
        form.addRow(buttonBox)

        buttonBox.accepted.connect(dialog.accept)
        buttonBox.rejected.connect(dialog.rejected)

        fg = dialog.exec()

        if fg == QDialog.Rejected:
            logging.debug("取消创建店铺")

        if fg == QDialog.Accepted:
            try:
                u = User(le_pri_key.text())
                open_a_store(u.compressed_public_key, le_mallname.text(), self.db)
            except Exception as e:
                logging.warning("创建用户失败：{}".format(e))
                QMessageBox.warning(self, "创建失败", "请检查输入的私钥是否正确")

    def mallsbox_update(self):
        """
            tab4：更新店铺显示
        """
        if self.currentIndex() != 3:
            return
        sql = "SELECT * FROM 店铺 ORDER BY 店铺编号;"
        mallList = self.db.select(sql, True)
        self.mallsBox = QWidget()
        self.mallsBox.setMinimumSize(
            750, max(800, 20 + len(mallList) * 215))

        self.mallframe_list.clear()
        self.lb_mallname_list.clear()
        self.lb_mallslogan_list.clear()
        self.bn_mall_customer_list.clear()
        self.bn_mall_boss_list.clear()

        for i in range(len(mallList)):
            name = mallList[i][1]
            slogan = mallList[i][3]
            self.mallframe_list.append(QFrame())
            self.mallframe_list[i].setParent(self.mallsBox)
            self.mallframe_list[i].setFixedSize(740, 220)
            self.mallframe_list[i].setFrameShape(QFrame.Box)
            self.mallframe_list[i].setContentsMargins(10, 10, 10, 10)
            self.mallframe_list[i].move(0, 10 + i * 215)

            self.lb_mallname_list.append(QLabel())
            self.lb_mallname_list[i].setText("店铺名称：" + name)
            self.lb_mallname_list[i].setParent(self.mallframe_list[-1])
            self.lb_mallslogan_list.append(QLabel())
            self.lb_mallslogan_list[i].setText("店铺标语：" + slogan)
            self.lb_mallslogan_list[i].setParent(self.mallframe_list[-1])
            font = QFont("Microsoft YaHei", 10, 60)
            self.lb_mallname_list[i].setFont(font)
            self.lb_mallslogan_list[i].setFont(font)
            self.lb_mallname_list[i].move(20, 70)
            self.lb_mallslogan_list[i].move(20, 130)

            self.bn_mall_customer_list.append(QPushButton())
            self.bn_mall_customer_list[i].setText("我是顾客")
            self.bn_mall_customer_list[i].setFixedSize(120, 40)
            self.bn_mall_customer_list[i].setParent(self.mallframe_list[-1])
            self.bn_mall_customer_list[i].setFont(font)
            self.bn_mall_customer_list[i].move(
                self.mallframe_list[i].width() - 160, 60)

            self.bn_mall_boss_list.append(QPushButton())
            self.bn_mall_boss_list[i].setText("我是店主")
            self.bn_mall_boss_list[i].setFixedSize(120, 40)
            self.bn_mall_boss_list[i].setParent(self.mallframe_list[-1])
            self.bn_mall_boss_list[i].setFont(font)
            self.bn_mall_boss_list[i].move(
                self.mallframe_list[i].width() - 160, 120)

        self.mallsBox.update()

        for i in range(len(self.bn_mall_customer_list)):
            self.bn_mall_customer_list[i].clicked.connect(
                partial(self.bn_mall_customer_clicked, mallList[i]))

        for i in range(len(self.bn_mall_boss_list)):
            self.bn_mall_boss_list[i].clicked.connect(
                partial(self.bn_mall_boss_clicked, mallList[i]))

        oldval = self.mall_scroll.verticalScrollBar().value()
        oldmaxval = self.mall_scroll.verticalScrollBar().maximum()
        self.mall_scroll.setMinimumWidth(750)
        self.mall_scroll.setWidget(self.mallsBox)
        if oldmaxval == 0:
            self.mall_scroll.verticalScrollBar().setValue(0)
        else:
            self.mall_scroll.verticalScrollBar().setValue(
                oldval * self.mall_scroll.verticalScrollBar().maximum() // oldmaxval)

    def bn_mall_customer_clicked(self, ele):
        self.customer_widget.update_info(ele, self.db)
        self.customer_widget.setCurrentIndex(0)
        self.customer_widget.show()

    def bn_mall_boss_clicked(self, ele):
        print(ele)
