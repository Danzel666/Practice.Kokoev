from PyQt5.QtWidgets import QWidget, QMessageBox
from form_3 import Reg
from db_connection import db_connection
import  bcrypt

class RegisterWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__()
        self.ui = Reg()
        self.ui.setupUi(self)
        self.parent = parent
        self.db = db_connection()
        self.ui.pushButton.clicked.connect(self.add_operator)
        self.ui.pushButton_2.clicked.connect(self.go_back)

    def add_operator(self):
        fio = self.ui.lineEdit.text().strip()
        gender = self.ui.lineEdit_2.text().strip()
        date = self.ui.lineEdit_3.text().strip()
        phone = self.ui.lineEdit_4.text().strip()
        login = self.ui.lineEdit_5.text().strip()
        password = self.ui.lineEdit_6.text().strip()


        if gender == 'Мужской':
            gender_id = 1
        elif gender == 'Женский':
            gender_id = 2
        else:
            gender_id = 0


        if not all([fio, gender, date, phone, login, password]):
            QMessageBox.warning(self, 'Ошибка', 'Заполните все поля')
            return
        if gender_id not in (1, 2):
            QMessageBox.warning(self, 'Ошибка', 'Пол: Мужской или Женский')
            return
        if not phone.isdigit() or len(phone) != 11:
            QMessageBox.warning(self, 'Ошибка', 'Телефон – 11 цифр')
            return

        try:
            self.db.cur.execute(
                "SELECT * FROM postgres.session.operator WHERE login = %s",
                (login,)
            )
            if self.db.cur.fetchone():
                QMessageBox.warning(self, 'Ошибка', 'Пользователь уже существует')
                return
            hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
            hash = hashed_password.decode('utf-8')
            self.db.cur.execute(
                """
                INSERT INTO session.operator (full_name, gender_id, phone, birth_date, login, parol)
VALUES (%s, %s, %s, %s, %s, %s)
                """,
                (fio, gender_id, phone, date, login, hash)
            )
            self.db.commit()
            QMessageBox.information(self, 'Успех', 'Сотрудник добавлен')
            for line in [self.ui.lineEdit, self.ui.lineEdit_2, self.ui.lineEdit_3,
                         self.ui.lineEdit_4, self.ui.lineEdit_5, self.ui.lineEdit_6]:
                line.clear()
        except Exception as e:
            QMessageBox.critical(self, 'Ошибка БД', str(e))
            self.db.rollback()

    def go_back(self):
        if self.parent:
            self.parent.show()
        self.close()

    def closeEvent(self, event):
        if self.db:
            self.db.close()
        event.accept()