# -*- coding: utf-8 -*-
from typing import Tuple

from PyQt5.QtCore import QSize, Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QWidget, QTabWidget, QListWidget, QHBoxLayout, QVBoxLayout, QListWidgetItem, QFormLayout, \
    QLineEdit, QPushButton, QLabel, QGridLayout, QMessageBox

from blockchain.function import put_on_shelves, update_app_info
from utils.db import DB


class QBossWidget(QTabWidget):
    def __init__(self, info: Tuple[str, str, str, str] = ("", "", "", ""), db: DB = None):
        super().__init__()
        self.setWindowTitle("修改店铺")
        self.setFixedSize(1000, 800)
        self.id, self.name, self.comp_pub_key, self.slogan = info
        self.db = db

        self.mall_widget = QWidget()
        self.tab1_layout = QVBoxLayout()
        # self.ln_mall_name = QLineEdit()
        # self.ln_mall_slogan = QLineEdit()
        self.ln_mall_name = QLabel()
        self.ln_mall_slogan = QLabel()
        self.ln_mall_name.setFont(QFont("Microsoft YaHei", 15, 60))
        self.ln_mall_slogan.setFont(QFont("Microsoft YaHei", 15, 60))
        self.mall_name_layout = QHBoxLayout()
        self.mall_slogan_layout = QHBoxLayout()

        self.app_widget = QWidget()
        self.tab2_layout = QHBoxLayout()
        self.app_list = []
        self.app_name_widget = QListWidget()
        self.app_info_layout = QFormLayout()
        self.item = None
        self.ln_cur_app_id = QLineEdit()
        self.ln_cur_app_name = QLineEdit()
        self.ln_cur_app_size = QLineEdit()
        self.ln_cur_app_version = QLineEdit()
        self.ln_cur_app_system = QLineEdit()
        self.ln_cur_app_price = QLineEdit()
        self.ln_cur_app_sales = QLineEdit()
        self.app_info_and_buy_layout = QVBoxLayout()
        self.bn_confirm = QPushButton()

        self.shelve_widget = QWidget()
        self.tab3_layout = QFormLayout()
        self.ln_new_app_name = QLineEdit()
        self.ln_new_app_size = QLineEdit()
        self.ln_new_app_version = QLineEdit()
        self.ln_new_app_system = QLineEdit()
        self.ln_new_app_price = QLineEdit()
        self.bn_shelve = QPushButton()

        self.addTab(self.mall_widget, "店铺详情")
        self.addTab(self.app_widget, "应用详情")
        self.addTab(self.shelve_widget, "上架应用")

        self.set_tab1_ui()
        self.set_tab2_ui()
        self.set_tab3_ui()

    def update_info(self, info: Tuple[str, str, str, str], db: DB):
        self.id, self.name, self.comp_pub_key, self.slogan = info
        self.db = db
        self.ln_mall_name.setText(self.name)
        self.ln_mall_slogan.setText(self.slogan)
        self.tab1_layout.update()
        self.reset_tab2_ui()

    def set_tab1_ui(self):
        self.tab1_layout.addStretch(10)

        self.mall_name_layout = QHBoxLayout()
        self.mall_name_layout.addStretch(10)
        self.mall_name_layout.addWidget(QLabel("店铺名称：", font=QFont("Microsoft YaHei", 15, 60)))
        self.mall_name_layout.addWidget(self.ln_mall_name)
        self.mall_name_layout.addStretch(10)

        self.tab1_layout.addLayout(self.mall_name_layout)
        self.tab1_layout.addStretch(10)

        self.mall_slogan_layout.addStretch(10)
        self.mall_slogan_layout.addWidget(QLabel("店铺标语:", font=QFont("Microsoft YaHei", 15, 60)))
        self.mall_slogan_layout.addWidget(self.ln_mall_slogan)
        self.mall_slogan_layout.addStretch(10)

        self.tab1_layout.addLayout(self.mall_slogan_layout)
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

        self.bn_confirm.setText("确认修改")
        self.bn_confirm.setFont(QFont("Microsoft YaHei", 15, 60))
        self.bn_confirm.setFixedSize(200, 80)

        self.app_info_and_buy_layout.addWidget(self.bn_confirm, alignment=Qt.AlignCenter)
        self.app_info_and_buy_layout.addStretch(10)
        self.tab2_layout.addLayout(self.app_info_and_buy_layout, 60)
        font = QFont("Microsoft YaHei", 15, 60)

        self.app_info_layout.addRow(QLabel(""))
        self.app_info_layout.addRow(QLabel("应用名称：", font=font), self.ln_cur_app_name)
        self.app_info_layout.addRow(QLabel(""))
        self.app_info_layout.addRow(QLabel("应用大小：", font=font), self.ln_cur_app_size)
        self.app_info_layout.addRow(QLabel(""))
        self.app_info_layout.addRow(QLabel("应用版本：", font=font), self.ln_cur_app_version)
        self.app_info_layout.addRow(QLabel(""))
        self.app_info_layout.addRow(QLabel("适配系统：", font=font), self.ln_cur_app_system)
        self.app_info_layout.addRow(QLabel(""))
        self.app_info_layout.addRow(QLabel("应用价格：", font=font), self.ln_cur_app_price)
        self.app_info_layout.addRow(QLabel(""))
        self.app_info_layout.addRow(QLabel("应用销量：", font=font), self.ln_cur_app_sales)

        self.ln_cur_app_name.setFont(font)
        self.ln_cur_app_size.setFont(font)
        self.ln_cur_app_version.setFont(font)
        self.ln_cur_app_system.setFont(font)
        self.ln_cur_app_price.setFont(font)
        self.ln_cur_app_sales.setFont(font)
        self.ln_cur_app_sales.setEnabled(False)

        self.app_name_widget.currentItemChanged.connect(self.app_info_update)
        self.bn_confirm.clicked.connect(self.update_app_info_clicked)

        self.app_widget.setLayout(self.tab2_layout)

    def update_app_info_clicked(self):
        name = self.ln_cur_app_name.text()
        size = self.ln_cur_app_size.text()
        price = self.ln_cur_app_price.text()
        version = self.ln_cur_app_version.text()
        system = self.ln_cur_app_system.text()
        try:
            update_app_info(self.app_list[self.app_name_widget.currentRow()][0],
                            name, size, version, system, price, self.db)
        except Exception as e:
            QMessageBox.warning(self, "更新失败", "{}".format(e))
        else:
            QMessageBox.information(self, "更新成功", "已成功更新应用信息。")
            self.reset_tab2_ui()


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
            self.ln_cur_app_name.setText("")
            self.ln_cur_app_size.setText("")
            self.ln_cur_app_version.setText("")
            self.ln_cur_app_system.setText("")
            self.ln_cur_app_price.setText("")
            self.ln_cur_app_sales.setText("")
        else:
            self.ln_cur_app_name.setText(self.app_list[cur_id][1])
            self.ln_cur_app_size.setText(str(self.app_list[cur_id][2]))
            self.ln_cur_app_version.setText(self.app_list[cur_id][3])
            self.ln_cur_app_system.setText(self.app_list[cur_id][4])
            self.ln_cur_app_price.setText(str(self.app_list[cur_id][5]))
            self.ln_cur_app_sales.setText(str(self.app_list[cur_id][6]))

        self.app_info_layout.update()

    def set_tab3_ui(self):
        self.shelve_widget.setLayout(self.tab3_layout)

        font = QFont("Microsoft YaHei", 15, 60)
        self.tab3_layout.addRow(QLabel("应用名称：", font=font), self.ln_new_app_name)
        self.tab3_layout.addRow(QLabel("应用大小：", font=font), self.ln_new_app_size)
        self.tab3_layout.addRow(QLabel("应用价格：", font=font), self.ln_new_app_price)
        self.tab3_layout.addRow(QLabel("适配系统：", font=font), self.ln_new_app_system)
        self.tab3_layout.addRow(QLabel("应用版本：", font=font), self.ln_new_app_version)

        self.ln_new_app_name.setFont(font)
        self.ln_new_app_size.setFont(font)
        self.ln_new_app_price.setFont(font)
        self.ln_new_app_system.setFont(font)
        self.ln_new_app_version.setFont(font)

        self.bn_shelve.setText("上架！")
        self.bn_shelve.setFont(font)
        self.bn_shelve.clicked.connect(self.app_shelve_clicked)
        self.tab3_layout.addRow(self.bn_shelve)

    def app_info_update_clicked(self):

        pass

    def app_shelve_clicked(self):
        name = self.ln_new_app_name.text()
        size = self.ln_new_app_size.text()
        price = self.ln_new_app_price.text()
        system = self.ln_new_app_system.text()
        vision = self.ln_new_app_version.text()

        if name == "" or size == "" or price == "" or system == "" or vision == "":
            QMessageBox.warning(self, "信息不完善", "请完善信息")
            return

        try:
            put_on_shelves(name, size, vision, system, price, self.id, self.db)
        except Exception as e:
            QMessageBox.information(self, "创建失败", "{}".format(e))
        else:
            QMessageBox.information(self, "创建成功", "已成功上架应用。")
            self.reset_tab2_ui()
            self.ln_new_app_name.setText("")
            self.ln_new_app_size.setText("")
            self.ln_new_app_price.setText("")
            self.ln_new_app_system.setText("")
            self.ln_new_app_version.setText("")
