from PyQt5.QtWidgets import QWidget
from form_1 import Home

class HomeWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.ui = Home()
        self.ui.setupUi(self)
        self.ui.pushButton_2.clicked.connect(self.open_avtor)

    def open_avtor(self):
        from avtorize_for_new import AvtorWindow
        self.avtor = AvtorWindow(previous_window=self)
        self.avtor.show()
        self.hide()

