from PyQt5.QtWidgets import QWidget, QMessageBox
from form_4 import Full_avt
import bcrypt
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
            # 1. Ищем пользователя ТОЛЬКО по логину. Пароль сюда НЕ передаём!
            query = "SELECT id, parol FROM session.operator WHERE login = %s"
            self.db.cur.execute(query, (login,))
            user = self.db.cur.fetchone()

            if user:
                operator_id, stored_hash = user

                if isinstance(stored_hash, str):
                    stored_hash_bytes = stored_hash.encode('utf-8')
                else:
                    stored_hash_bytes = stored_hash

                is_password_correct = bcrypt.checkpw(password.encode('utf-8'), stored_hash_bytes)

                if is_password_correct:
                    self.ui.lineEdit.clear()
                    self.ui.lineEdit_2.clear()

                    self.sessions_win = SessionsWindow(operator_id, parent=self)
                    self.sessions_win.show()
                    self.hide()
                else:
                    QMessageBox.warning(self, 'Ошибка', 'Неверный логин или пароль')
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