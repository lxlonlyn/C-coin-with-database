# -*- coding: utf-8 -*-
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QVBoxLayout, QLabel, QFrame


class QBlockWidget(QFrame):
    """
    用来显示区块列表中的一个区块。
    """
    def __init__(self):
        super().__init__()
        self.setMinimumSize(740, 220)
        self.block_hash = "none"
        self.time_stamp = "none"
        self.pre_hash = "none"
        self.merkle_hash = "none"
        self.setFrameStyle(QFrame.Box | QFrame.Raised)
        self.setContentsMargins(10, 10, 10, 10)
        layout = QVBoxLayout()

        self.lb_hash = QLabel()
        self.lb_hash.setText(self.block_hash)
        # self.lb_hash.setFrameStyle(QFrame.Box)

        self.lb_time = QLabel()
        self.lb_time.setText(self.time_stamp)
        # self.lb_time.setFrameStyle(QFrame.Box)

        self.lb_prehash = QLabel()
        self.lb_prehash.setText(self.pre_hash)

        self.lb_merkle = QLabel()
        self.lb_merkle.setText(self.merkle_hash)

        font = QFont("Microsoft YaHei", 8, 60)
        self.lb_hash.setFont(font)
        self.lb_time.setFont(font)
        self.lb_prehash.setFont(font)
        self.lb_merkle.setFont(font)

        layout.addWidget(self.lb_hash)
        layout.addWidget(self.lb_time)
        layout.addWidget(self.lb_prehash)
        layout.addWidget(self.lb_merkle)

        layout.setAlignment(Qt.AlignLeft)
        self.setLayout(layout)

    def set_hash(self, new_hash):
        self.block_hash = new_hash
        self.update()

    def set_time(self, time):
        self.time_stamp = time
        self.update()

    def set_prehash(self, prehash):
        self.pre_hash = prehash
        self.update()

    def set_merkle(self, merkle):
        self.merkle_hash = merkle
        self.update()

    def update(self):
        self.lb_hash.setText("区块哈希：" + self.block_hash[0:32] + self.block_hash[32:])
        self.lb_hash.repaint()
        self.lb_time.setText("时间戳：" + self.time_stamp)
        self.lb_time.repaint()
        self.lb_prehash.setText("父区块哈希值：" + self.pre_hash)
        self.lb_prehash.repaint()
        self.lb_merkle.setText("Merkle Hash：" + self.merkle_hash)
        self.lb_merkle.repaint()
