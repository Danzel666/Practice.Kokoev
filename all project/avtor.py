from PyQt5.QtWidgets import QWidget, QMessageBox
from form_4 import Full_avt
from db_connection import db_connection
from sessions_window import SessionsWindow

class AvtorWindowSes(QWidget):
    def __init__(self, parent=None):
        super().__init__()
        self.ui = Full_avt()
        self.ui.setupUi(self)
        self.parent = parent
        self.db = db_connection()
        self.ui.pushButton.clicked.connect(self.open_sessions)
        self.ui.pushButton_2.clicked.connect(self.go_back)

    def open_sessions(self):
        login = self.ui.lineEdit.text().strip()
        password = self.ui.lineEdit_2.text().strip()

        if not login or not password:
            QMessageBox.warning(self, 'Ошибка', 'Введите логин и пароль')
            return

        try:
            query = "SELECT id FROM session.operator WHERE login = %s AND parol = %s"
            self.db.cur.execute(query, (login, password))
            user = self.db.cur.fetchone()
            if user:
                operator_id = user[0]
                self.ui.lineEdit.clear()
                self.ui.lineEdit_2.clear()
                self.sessions_win = SessionsWindow(operator_id, parent=self)
                self.sessions_win.show()
                self.hide()
            else:
                QMessageBox.warning(self, 'Ошибка', 'Неверный логин или пароль')
        except Exception as e:
            QMessageBox.critical(self, 'Ошибка БД', f'Ошибка при проверке данных:\n{str(e)}')

    def go_back(self):
        if self.parent:
            self.parent.show()
        self.close()

    def closeEvent(self, event):
        if self.db:
            self.db.close()
        event.accept()