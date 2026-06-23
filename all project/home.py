import sys
from PyQt5.QtWidgets import QWidget
from form_1 import Home
from avtorize_for_new import AvtorWindow   # предполагаемый файл
from avtor import AvtorWindowSes          # предполагаемый файл

class HomeWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.ui = Home()
        self.ui.setupUi(self)
        self.avtor_ses = AvtorWindowSes(parent=self)
        self.avtor_ses.hide()
        self.avtor = AvtorWindow(parent=self)
        self.avtor.hide()
        self.ui.pushButton_3.clicked.connect(self.open_avtor_ses)
        self.ui.pushButton_2.clicked.connect(self.open_avtor)

    def open_avtor_ses(self):
        self.avtor_ses = AvtorWindowSes(parent=self)
        self.avtor_ses.show()
        self.hide()

    def open_avtor(self):
        self.avtor.show()
        self.hide()