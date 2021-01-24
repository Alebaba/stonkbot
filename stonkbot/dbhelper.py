import sqlite3

class DBHelper:
    def __init__(self, dbname="tickerdb.sqlite"):
        self.dbname = dbname
        self.conn = sqlite3.connect(dbname, check_same_thread=False)

    def __del__(self):
        self.conn.close()

    def setup(self):
        stmt = "CREATE TABLE IF NOT EXISTS tickers (owner TEXT, ticker TEXT)"
        self.conn.execute(stmt)
        self.conn.commit()

    def add_ticker(self, owner, ticker):
        stmt = 'INSERT INTO tickers (owner, ticker)\
            SELECT ?1, ?2\
            WHERE NOT EXISTS (SELECT 1 FROM tickers WHERE owner = ?1 AND ticker = ?2)'
        args = (owner, ticker)
        self.conn.execute(stmt, args)
        self.conn.commit()


    def delete_ticker(self, owner, ticker):
        stmt = "DELETE FROM tickers WHERE (owner, ticker) = (?, ?)"
        args = (owner, ticker)
        self.conn.execute(stmt, args)
        self.conn.commit()

    def get_tickers(self, owner):
        stmt = "SELECT ticker FROM tickers WHERE owner = (?)"
        args = (owner, )
        return [i[0] for i in self.conn.execute(stmt, args)]