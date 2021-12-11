# -*- coding: utf-8 -*-
from typing import Tuple

from PyQt5.QtCore import QSize, Qt
from PyQt5.QtWidgets import QWidget, QTabWidget, QListWidget, QHBoxLayout, QVBoxLayout, QListWidgetItem, QFormLayout
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

        self.app_widget = QWidget()
        self.tab2_layout = QHBoxLayout()
        self.app_name_widget = QListWidget()
        self.app_info_layout = QFormLayout()
        self.item = None

        self.addTab(self.mall_widget, "店铺详情")
        self.addTab(self.app_widget, "应用详情")

        self.set_tab1_ui()
        self.set_tab2_ui()

    def update_info(self, info: Tuple[str, str, str, str], db: DB):
        self.id, self.name, self.comp_pub_key, self.slogan = info
        self.db = db
        self.reset_tab2_ui()

    def set_tab1_ui(self):
        pass

    def set_tab2_ui(self):
        if self.db is not None:
            app_list = self.db.select("SELECT * FROM 应用程序 WHERE 店铺编号 = '{}'".format(self.id))
        else:
            app_list = []

        self.app_name_widget.clear()
        for i in range(len(app_list)):
            self.item = QListWidgetItem(app_list[i][1], self.app_name_widget)
            self.item.setSizeHint(QSize(30, 60))
            self.item.setTextAlignment(Qt.AlignCenter)

        self.tab2_layout.addWidget(self.app_name_widget, 30)
        self.tab2_layout.addStretch(10)
        self.tab2_layout.addLayout(self.app_info_layout, 60)

        self.app_widget.setLayout(self.tab2_layout)

    def reset_tab2_ui(self):
        if self.db is not None:
            app_list = self.db.select("SELECT * FROM 应用程序 WHERE 店铺编号 = '{}'".format(self.id))
        else:
            app_list = []

        self.app_name_widget.clear()
        for i in range(len(app_list)):
            self.item = QListWidgetItem(app_list[i][1], self.app_name_widget)
            self.item.setSizeHint(QSize(30, 60))
            self.item.setTextAlignment(Qt.AlignCenter)
