import psycopg2
import pandas as pd


class PostgresConnectorContextManager:
    def __init__(self, host: str, port: int, dbname: str, user: str, password: str):
        self.host = host
        self.port = port
        self.dbname = dbname
        self.user = user
        self.password = password
        self.conn = None

    def __enter__(self):
        self.conn = psycopg2.connect(
            host=self.host,
            port=self.port,
            dbname=self.dbname,
            user=self.user,
            password=self.password
        )
        return self

    def __exit__(self, exc_type, exc_value, exc_tb):
        if self.conn:
            self.conn.close()

    def execute_scalar(self, query: str):
        with self.conn.cursor() as cursor:
            cursor.execute(query)
            return cursor.fetchone()[0]

    def get_data_sql(self, sql: str):
        return pd.read_sql(sql, self.conn)