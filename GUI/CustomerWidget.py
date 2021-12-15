# -*- coding: utf-8 -*-
import logging
from typing import Tuple

from PyQt5.QtCore import QSize, Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QWidget, QTabWidget, QListWidget, QHBoxLayout, QVBoxLayout, QListWidgetItem, QFormLayout, \
    QLabel, QPushButton, QInputDialog, QLineEdit, QMessageBox

from blockchain.error import CoinNotEnough
from blockchain.function import make_deal, buy_app
from blockchain.user import User
from utils.db import DB


class QCustomerWidget(QTabWidget):
    def __init__(self, info: Tuple[str, str, str, str] = ("", "", "", ""), db: DB = None):
        super().__init__()
        self.setWindowTitle("应用商城")
        self.setFixedSize(1000, 800)
        self.id, self.name, self.comp_pub_key, self.slogan = info
        self.db = db

        self.mall_widget = QWidget()
        self.tab1_layout = QVBoxLayout()
        self.lb_mall_name = QLabel()
        self.lb_mall_slogan = QLabel()
        self.lb_mall_name.setFont(QFont("Microsoft YaHei", 15, 60))
        self.lb_mall_slogan.setFont(QFont("Microsoft YaHei", 15, 60))

        self.app_widget = QWidget()
        self.tab2_layout = QHBoxLayout()
        self.app_list = []
        self.app_name_widget = QListWidget()
        self.app_info_layout = QFormLayout()
        self.item = None

        self.lb_cur_app_id = QLabel()
        self.lb_cur_app_name = QLabel()
        self.lb_cur_app_size = QLabel()
        self.lb_cur_app_version = QLabel()
        self.lb_cur_app_system = QLabel()
        self.lb_cur_app_price = QLabel()
        self.lb_cur_app_sales = QLabel()
        self.app_info_and_buy_layout = QVBoxLayout()
        self.bn_buy = QPushButton()

        self.addTab(self.mall_widget, "店铺详情")
        self.addTab(self.app_widget, "应用详情")

        self.set_tab1_ui()
        self.set_tab2_ui()

    def update_info(self, info: Tuple[str, str, str, str], db: DB):
        self.id, self.name, self.comp_pub_key, self.slogan = info
        self.db = db
        self.lb_mall_name.setText("店铺名称：" + self.name)
        self.lb_mall_slogan.setText("店铺标语：" + self.slogan)
        self.tab1_layout.update()
        self.reset_tab2_ui()

    def set_tab1_ui(self):
        self.tab1_layout.addStretch(10)
        self.tab1_layout.addWidget(self.lb_mall_name)
        self.tab1_layout.addStretch(10)
        self.tab1_layout.addWidget(self.lb_mall_slogan)
        self.tab1_layout.addStretch(10)
        self.mall_widget.setLayout(self.tab1_layout)

    def set_tab2_ui(self):
        if self.db is not None:
            self.app_list = self.db.select("SELECT * FROM 应用程序 WHERE 店铺编号 = '{}'".format(self.id))
        else:
            self.app_list.clear()

        self.app_name_widget.clear()
        for i in range(len(self.app_list)):
            self.item = QListWidgetItem(self.app_list[i][1], self.app_name_widget)
            self.item.setSizeHint(QSize(30, 60))
            self.item.setTextAlignment(Qt.AlignCenter)

        self.tab2_layout.addWidget(self.app_name_widget, 30)
        self.tab2_layout.addStretch(5)
        self.app_info_and_buy_layout.addLayout(self.app_info_layout)
        self.app_info_and_buy_layout.addStretch(20)

        self.bn_buy.setText("立即购买")
        self.bn_buy.setFont(QFont("Microsoft YaHei", 15, 60))
        self.bn_buy.setFixedSize(200, 80)

        self.app_info_and_buy_layout.addWidget(self.bn_buy, alignment=Qt.AlignCenter)
        self.app_info_and_buy_layout.addStretch(10)
        self.tab2_layout.addLayout(self.app_info_and_buy_layout, 60)
        font = QFont("Microsoft YaHei", 15, 60)

        self.app_info_layout.addRow(QLabel(""))
        self.app_info_layout.addRow(QLabel("应用名称：", font=font), self.lb_cur_app_name)
        self.app_info_layout.addRow(QLabel(""))
        self.app_info_layout.addRow(QLabel("应用大小：", font=font), self.lb_cur_app_size)
        self.app_info_layout.addRow(QLabel(""))
        self.app_info_layout.addRow(QLabel("应用版本：", font=font), self.lb_cur_app_version)
        self.app_info_layout.addRow(QLabel(""))
        self.app_info_layout.addRow(QLabel("适配系统：", font=font), self.lb_cur_app_system)
        self.app_info_layout.addRow(QLabel(""))
        self.app_info_layout.addRow(QLabel("应用价格：", font=font), self.lb_cur_app_price)
        self.app_info_layout.addRow(QLabel(""))
        self.app_info_layout.addRow(QLabel("应用销量：", font=font), self.lb_cur_app_sales)

        self.lb_cur_app_name.setFont(font)
        self.lb_cur_app_size.setFont(font)
        self.lb_cur_app_version.setFont(font)
        self.lb_cur_app_system.setFont(font)
        self.lb_cur_app_price.setFont(font)
        self.lb_cur_app_sales.setFont(font)

        self.app_name_widget.currentItemChanged.connect(self.app_info_update)
        self.bn_buy.clicked.connect(self.buy_clicked)

        self.app_widget.setLayout(self.tab2_layout)

    def reset_tab2_ui(self):
        if self.db is not None:
            self.app_list = self.db.select("SELECT * FROM 应用程序 WHERE 店铺编号 = '{}'".format(self.id))
        else:
            self.app_list = []

        self.app_name_widget.clear()
        for i in range(len(self.app_list)):
            self.item = QListWidgetItem(self.app_list[i][1], self.app_name_widget)
            self.item.setSizeHint(QSize(30, 60))
            self.item.setTextAlignment(Qt.AlignCenter)

    def app_info_update(self):
        cur_id = self.app_name_widget.currentRow()
        if cur_id < 0:
            self.lb_cur_app_name.setText("")
            self.lb_cur_app_size.setText("")
            self.lb_cur_app_version.setText("")
            self.lb_cur_app_system.setText("")
            self.lb_cur_app_price.setText("")
            self.lb_cur_app_sales.setText("")
        else:
            self.lb_cur_app_name.setText(self.app_list[cur_id][1])
            self.lb_cur_app_size.setText(str(self.app_list[cur_id][2]))
            self.lb_cur_app_version.setText(self.app_list[cur_id][3])
            self.lb_cur_app_system.setText(self.app_list[cur_id][4])
            self.lb_cur_app_price.setText(str(self.app_list[cur_id][5]))
            self.lb_cur_app_sales.setText(str(self.app_list[cur_id][6]))

        self.app_info_layout.update()

    def buy_clicked(self):
        cur_id = self.app_name_widget.currentRow()
        if cur_id < 0:
            QMessageBox.information(self, "未选中商品", "已成功购买空气×1")
            return
        msg = "请确认购买信息，然后在下方输入您的私钥：" + \
              "\n应用名称：" + self.lb_cur_app_name.text() + \
              "\n应用价格：" + self.lb_cur_app_price.text() + \
              "\n适配系统：" + self.lb_cur_app_system.text()
        pri_key, ok = QInputDialog.getText(
            self, "确认购买", msg, QLineEdit.Normal, "")
        try:
            user = User(pri_key)
            buy_app(user, self.app_list[cur_id][0], self.db)
        except CoinNotEnough as e:
            QMessageBox.warning(self, "余额不足", "{}".format(e))
        except Exception as e:
            QMessageBox.warning(self, "交易失败", "请检查私钥是否正确。")
            logging.info("{}".format(e))
        else:
            logging.info("交易成功")
            QMessageBox.information(self, "交易成功", "交易成功，您已获得此应用！")

