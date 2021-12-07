from PyQt5.QtWidgets import QApplication
from GUI.MainWidget import MainWindow
import sys
from utils.db import DB

import logging

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    db = DB("localhost", _passwd="csnb")
    # db.create_tables(rebuild=True)
    app = QApplication(sys.argv)
    window = MainWindow(db)
    window.show()
    sys.exit(app.exec_())
