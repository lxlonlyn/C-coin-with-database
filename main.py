from PyQt5.QtWidgets import QApplication
from GUI.MainWidget import MainWindow
import sys

import logging

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
