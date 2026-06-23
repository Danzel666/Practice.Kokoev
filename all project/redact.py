from PyQt5.QtWidgets import QWidget, QMessageBox

from db_connection import db_connection

from form_6 import Redact

class RedactWindow(QWidget):
    def __init__(self, session_id, parent=None):
        super().__init__(parent)
        self.session_id = session_id
        self.parent_window = parent
        self.ui = Redact()
        self.ui.setupUi(self)
        self.db = db_connection()
        self.load_data()
        self.ui.pushButton.clicked.connect(self.update_session)
        self.ui.pushButton_2.clicked.connect(self.go_back)

    def ensure_db(self):
        if self.db is None or self.db.con is None or self.db.cur is None:
            self.db = db_connection()
            if self.db.cur is None:
                QMessageBox.critical(self, "Ошибка", "Нет подключения к БД")
                return False
        return True

    def load_data(self):
        if not self.ensure_db():
            return
        try:
            self.db.cur.execute("""
                SELECT work_type_id, coil, spacecraft_id
                FROM session.session WHERE id = %s
            """, (self.session_id,))
            row = self.db.cur.fetchone()
            if not row:
                QMessageBox.critical(self, "Ошибка", "Сеанс не найден")
                return
            work_type_id, coil, spacecraft_id = row
            self.db.cur.execute("SELECT name FROM session.work_type WHERE id = %s", (work_type_id,))
            work_type_name = self.db.cur.fetchone()[0]
            self.db.cur.execute("SELECT name FROM session.spacecraft WHERE id = %s", (spacecraft_id,))
            spacecraft_name = self.db.cur.fetchone()[0]
            self.ui.lineEdit_7.setText(work_type_name)
            self.ui.lineEdit_8.setText(str(coil))
            self.ui.lineEdit_9.setText(spacecraft_name)

            self.db.cur.execute("SELECT id FROM session.formular WHERE session_id = %s ORDER BY id LIMIT 1", (self.session_id,))
            formular_row = self.db.cur.fetchone()
            if not formular_row:
                QMessageBox.critical(self, "Ошибка", "Формуляр для сеанса не найден")
                return
            formular_id = formular_row[0]

            for param_id in range(1, 6):
                self.db.cur.execute("""
                    SELECT value FROM session.parameter_value
                    WHERE formular_id = %s AND parameter_id = %s
                """, (formular_id, param_id))
                row = self.db.cur.fetchone()
                value = row[0] if row else ''
                if param_id == 1:
                    self.ui.lineEdit.setText(str(value) if value != '' else '')
                elif param_id == 2:
                    self.ui.lineEdit_2.setText(str(value) if value != '' else '')
                elif param_id == 3:
                    self.ui.lineEdit_3.setText(str(value) if value != '' else '')
                elif param_id == 4:
                    self.ui.lineEdit_4.setText(str(value) if value != '' else '')
                elif param_id == 5:
                    self.ui.lineEdit_5.setText(str(value) if value != '' else '')
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить данные: {str(e)}")

    def update_session(self):
        if not self.ensure_db():
            return
        val1 = self.ui.lineEdit.text().strip()
        val2 = self.ui.lineEdit_2.text().strip()
        val3 = self.ui.lineEdit_3.text().strip()
        val4 = self.ui.lineEdit_4.text().strip()
        val5 = self.ui.lineEdit_5.text().strip()
        work_type_name = self.ui.lineEdit_7.text().strip()
        coil = self.ui.lineEdit_8.text().strip()
        spacecraft_name = self.ui.lineEdit_9.text().strip()

        if not all([val1, val2, val3, val4, val5, work_type_name, coil, spacecraft_name]):
            QMessageBox.warning(self, "Ошибка", "Заполните все поля")
            return

        try:
            float(val1); float(val2); float(val3); float(val4); float(val5)
            int(coil)
        except ValueError:
            QMessageBox.warning(self, "Ошибка", "Параметры и виток должны быть числами")
            return
        try:
            self.db.cur.execute("SELECT id FROM session.work_type WHERE name = %s", (work_type_name,))
            row = self.db.cur.fetchone()
            if not row:
                QMessageBox.warning(self, "Ошибка", f"Тип испытания '{work_type_name}' не найден")
                return
            work_type_id = row[0]

            self.db.cur.execute("SELECT id FROM session.spacecraft WHERE name = %s", (spacecraft_name,))
            row = self.db.cur.fetchone()
            if not row:
                QMessageBox.warning(self, "Ошибка", f"КА '{spacecraft_name}' не найден")
                return
            spacecraft_id = row[0]

            self.db.cur.execute("""
                UPDATE session.session
                SET work_type_id = %s, coil = %s, spacecraft_id = %s
                WHERE id = %s
            """, (work_type_id, int(coil), spacecraft_id, self.session_id))

            self.db.cur.execute("SELECT id FROM session.formular WHERE session_id = %s ORDER BY id LIMIT 1", (self.session_id,))
            formular_row = self.db.cur.fetchone()
            if not formular_row:
                QMessageBox.critical(self, "Ошибка", "Формуляр для сеанса не найден")
                return
            formular_id = formular_row[0]

            param_values = [(1, float(val1)), (2, float(val2)), (3, float(val3)), (4, float(val4)), (5, float(val5))]
            for param_id, value in param_values:
                self.db.cur.execute("SELECT min_value, max_value FROM session.parameter WHERE id = %s", (param_id,))
                min_val, max_val = self.db.cur.fetchone()
                if min_val is not None and max_val is not None:
                    status = "Норма" if (min_val <= value <= max_val) else "Отклонение"
                else:
                    status = "Норма"
                self.db.cur.execute("""
                    UPDATE session.parameter_value
                    SET value = %s, status = %s
                    WHERE formular_id = %s AND parameter_id = %s
                """, (value, status, formular_id, param_id))
                if self.db.cur.rowcount == 0:
                    self.db.cur.execute("""
                        INSERT INTO session.parameter_value (formular_id, parameter_id, value, status)
                        VALUES (%s, %s, %s, %s)
                    """, (formular_id, param_id, value, status))

            self.db.commit()
            QMessageBox.information(self, "Успех", "Данные сеанса обновлены")
            self.go_back()
        except Exception as e:
            self.db.rollback()
            QMessageBox.critical(self, "Ошибка БД", f"Ошибка при обновлении: {str(e)}")

    def go_back(self):
        if self.parent_window:
            self.parent_window.show()
        self.close()

    def closeEvent(self, event):
        if self.db:
            self.db.close()
        event.accept()