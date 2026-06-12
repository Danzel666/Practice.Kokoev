import sys
from PyQt5.QtWidgets import QApplication
from home import HomeWindow

if __name__ == "__main__":
    app = QApplication(sys.argv)
    home = HomeWindow()
    home.show()
    sys.exit(app.exec_())
