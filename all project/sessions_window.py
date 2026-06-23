from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QScrollArea, QFrame, QComboBox, QMessageBox
from PyQt5.QtCore import Qt

from db_connection import db_connection

from new_ses import NewSesWindow
from redact import RedactWindow

class SessionCard(QFrame):
    def __init__(self, session_id, work_type, spacecraft, parent_window, parent=None):
        super().__init__(parent)
        self.session_id = session_id
        self.parent_window = parent_window
        self.setFrameShape(QFrame.Box)
        self.setStyleSheet("QFrame { background-color: #f0f0f0; margin: 5px; padding: 5px; }")
        layout = QVBoxLayout()
        layout.addWidget(QLabel(f"<b>Сеанс №{session_id}</b>"))
        layout.addWidget(QLabel(f"Тип испытания: {work_type}"))
        layout.addWidget(QLabel(f"КА: {spacecraft}"))

        btn_layout = QHBoxLayout()
        edit_btn = QPushButton("Редактировать")
        edit_btn.clicked.connect(self.edit)
        delete_btn = QPushButton("Удалить")
        delete_btn.clicked.connect(self.delete)
        btn_layout.addWidget(edit_btn)
        btn_layout.addWidget(delete_btn)
        layout.addLayout(btn_layout)
        self.setLayout(layout)

    def edit(self):
        if self.parent_window:
            self.parent_window.edit_session(self.session_id)

    def delete(self):
        if self.parent_window:
            self.parent_window.delete_session(self.session_id)

class SessionsWindow(QWidget):
    def __init__(self, operator_id, parent=None):
        super().__init__(parent)
        self.operator_id = operator_id
        self.db = None
        self.all_sessions = []
        self.setWindowTitle("Список сеансов")
        self.setGeometry(200, 200, 700, 500)
        self.setWindowFlags(Qt.Window)
        self.setup_ui()
        self.load_sessions()

    def setup_ui(self):
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)

        top = QHBoxLayout()
        back_btn = QPushButton("Назад")
        back_btn.clicked.connect(self.go_back)
        top.addWidget(back_btn)

        create_btn = QPushButton("Создать сеанс")
        create_btn.clicked.connect(self.create_session)
        top.addWidget(create_btn)
        top.addStretch()
        main_layout.addLayout(top)

        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel("Тип испытания:"))
        self.work_type_combo = QComboBox()
        self.work_type_combo.addItem("Все")
        self.work_type_combo.currentTextChanged.connect(self.apply_filters)
        filter_layout.addWidget(self.work_type_combo)

        filter_layout.addWidget(QLabel("КА:"))
        self.spacecraft_combo = QComboBox()
        self.spacecraft_combo.addItem("Все")
        self.spacecraft_combo.currentTextChanged.connect(self.apply_filters)
        filter_layout.addWidget(self.spacecraft_combo)
        filter_layout.addStretch()
        main_layout.addLayout(filter_layout)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        self.container = QWidget()
        self.cards_layout = QVBoxLayout(self.container)
        self.cards_layout.setAlignment(Qt.AlignTop)
        scroll.setWidget(self.container)
        main_layout.addWidget(scroll)

    def ensure_db(self):
        if self.db is None or self.db.con is None or self.db.cur is None:
            self.db = db_connection()
            if self.db.cur is None:
                QMessageBox.critical(self, "Ошибка", "Не удалось подключиться к базе данных")
                return False
        return True

    def load_sessions(self):
        if not self.ensure_db():
            return
        try:
            query = """
                SELECT s.id, wt.name, sc.name
                FROM session.session s
                JOIN session.work_type wt ON s.work_type_id = wt.id
                JOIN session.spacecraft sc ON s.spacecraft_id = sc.id
                WHERE s.operator_id = %s
                ORDER BY s.id
            """
            self.db.cur.execute(query, (self.operator_id,))
            rows = self.db.cur.fetchall()
            self.all_sessions = []
            work_types = set()
            spacecrafts = set()
            for row in rows:
                sess = {
                    'id': row[0],
                    'work_type': row[1],
                    'spacecraft': row[2]
                }
                self.all_sessions.append(sess)
                work_types.add(row[1])
                spacecrafts.add(row[2])

            self.work_type_combo.clear()
            self.work_type_combo.addItem("Все")
            self.work_type_combo.addItems(sorted(work_types))

            self.spacecraft_combo.clear()
            self.spacecraft_combo.addItem("Все")
            self.spacecraft_combo.addItems(sorted(spacecrafts))

            self.apply_filters()
        except Exception as e:
            import traceback
            traceback.print_exc()
            QMessageBox.critical(self, "Ошибка БД", f"Не удалось загрузить сеансы: {e}")

    def apply_filters(self):
        wt_filter = self.work_type_combo.currentText()
        sc_filter = self.spacecraft_combo.currentText()
        filtered = [
            s for s in self.all_sessions
            if (wt_filter == "Все" or s['work_type'] == wt_filter)
            and (sc_filter == "Все" or s['spacecraft'] == sc_filter)
        ]
        while self.cards_layout.count():
            child = self.cards_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        for sess in filtered:
            card = SessionCard(sess['id'], sess['work_type'], sess['spacecraft'], self, self.container)
            self.cards_layout.addWidget(card)

        if not filtered:
            label = QLabel("Нет сеансов, соответствующих фильтру.")
            label.setAlignment(Qt.AlignCenter)
            self.cards_layout.addWidget(label)
        elif not self.all_sessions:
            label = QLabel("У вас нет сеансов. Создайте новый сеанс.")
            label.setAlignment(Qt.AlignCenter)
            self.cards_layout.addWidget(label)

    def create_session(self):
        self.new_ses_win = NewSesWindow(self.operator_id, parent=self)
        self.new_ses_win.setWindowFlags(Qt.Window)
        self.new_ses_win.show()
        self.hide()

    def edit_session(self, session_id):
        self.redact_win = RedactWindow(session_id, parent=self)
        self.redact_win.setWindowFlags(Qt.Window)
        self.redact_win.show()
        self.hide()

    def delete_session(self, session_id):
        reply = QMessageBox.question(
            self, "Удаление сеанса",
            f"Вы уверены, что хотите удалить сеанс №{session_id} и все связанные с ним данные (формуляры, параметры)?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        if reply != QMessageBox.Yes:
            return

        if not self.ensure_db():
            return

        try:
            self.db.cur.execute("""
                DELETE FROM session.parameter_value
                WHERE formular_id IN (SELECT id FROM session.formular WHERE session_id = %s)
            """, (session_id,))
            self.db.cur.execute("DELETE FROM session.formular WHERE session_id = %s", (session_id,))
            self.db.cur.execute("DELETE FROM session.session WHERE id = %s", (session_id,))
            self.db.commit()
            QMessageBox.information(self, "Успех", f"Сеанс №{session_id} и все связанные данные удалены.")
            self.load_sessions()
        except Exception as e:
            self.db.rollback()
            QMessageBox.critical(self, "Ошибка БД", f"Не удалось удалить сеанс: {str(e)}")

    def go_back(self):
        if self.parent():
            self.parent().show()
        self.close()

    def showEvent(self, event):
        super().showEvent(event)
        self.load_sessions()

    def closeEvent(self, event):
        if self.db:
            self.db.close()
        event.accept()