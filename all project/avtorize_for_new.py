from PyQt5.QtWidgets import QWidget, QMessageBox
from form_2 import Avtorize_new
from db_connection import db_connection
from register import RegisterWindow

class AvtorWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__()
        self.ui = Avtorize_new()
        self.ui.setupUi(self)
        self.parent = parent  # home или register

        self.db = db_connection()

        self.ui.pushButton.clicked.connect(self.open_register)
        self.ui.pushButton_2.clicked.connect(self.go_back)

        self.login = 0
        self.password = 0


    def open_register(self):
        login = self.ui.lineEdit.text().strip()
        password = self.ui.lineEdit_2.text().strip()

        if login == 'kokoev' and password == 'kokoev':
            self.ui.lineEdit.clear()
            self.ui.lineEdit_2.clear()
            self.reg = RegisterWindow(parent=self)
            self.reg.show()
            self.hide()
        else:
            QMessageBox.warning(self, 'Ошибка', 'Неверный логин или пароль!')

    def go_back(self):
        if self.parent:
            self.parent.show()
        self.close()

    def closeEvent(self, event):
        if self.db:
            self.db.close()