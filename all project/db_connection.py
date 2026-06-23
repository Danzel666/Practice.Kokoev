from psycopg2 import connect, Error


class db_connection:
    def __init__(self, host='localhost', user='postgres', dbname='postgres',
                 password='root', port='5432'):
        self.con = None
        self.cur = None
        try:
            self.con = connect(host=host, user=user, dbname=dbname,
                               password=password, port=port)
            self.cur = self.con.cursor()
            print("Подключение к БД установлено")
        except Error as e:
            print(f"Ошибка подключения: {e}")

    def commit(self):
        if self.con:
            self.con.commit()

    def rollback(self):
        if self.con:
            self.con.rollback()

    def close(self):
        if self.cur:
            self.cur.close()
        if self.con:
            self.con.close()

