import sqlite3
from peewee import SqliteDatabase

# メインデータベース接続
db = SqliteDatabase('my_database.db')

# SQLite 直接接続用
DB_PATH = "my_database.db"

def get_db_connection():
    """SQLite データベース接続を取得"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn
