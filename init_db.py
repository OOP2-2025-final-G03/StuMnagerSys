import sqlite3

DB_PATH = 'database.db'

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS subjects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,          -- 科目名
    major TEXT NOT NULL,         -- 専攻
    category TEXT NOT NULL,      -- 単位区分（required / elective）
    grade INTEGER NOT NULL,      -- 対象学年
    credits INTEGER NOT NULL,    -- 単位数
    day TEXT NOT NULL,           -- 曜日（月・火など）
    period INTEGER NOT NULL      -- 時間（1〜6）
)
""")

conn.commit()
conn.close()

print("database.db と subjects テーブルを作成しました（最新版仕様）")
