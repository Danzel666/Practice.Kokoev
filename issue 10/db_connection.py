from psycopg2 import connect, Error, OperationalError




class db_connection:
    def __init__(self, host='localhost', user='postgres', dbname='postgres',
                 password='root', port='5432'):
        self.host = host
        self.user = user
        self.dbname = dbname
        self.password = password
        self.port = port
        self.con = None
        self.cur = None
        self._connect()

    def _connect(self):
        try:
            self.con = connect(
                host=self.host,
                user=self.user,
                dbname=self.dbname,
                password=self.password,
                port=self.port
            )
            self.cur = self.con.cursor()
            print('Подключение к БД успешно!')
        except Error as e:
            print(f'Ошибка подключения: {e}')
            self.con = None
            self.cur = None

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
            print('Соединение с БД закрыто.')

    def reconnect(self):
        self.close()
        self._connect()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            self.rollback()
        self.close()
