from peewee import SqliteDatabase

# メインデータベース接続
db = SqliteDatabase('database.db', pragmas={'foreign_keys': 1})
