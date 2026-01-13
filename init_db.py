import sqlite3

DB_PATH = 'database.db'

def init_database():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # 1. 科目テーブル
    cur.execute("""
    CREATE TABLE IF NOT EXISTS subjects (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        major TEXT NOT NULL,
        category TEXT NOT NULL,
        grade INTEGER NOT NULL,
        credits INTEGER NOT NULL,
        day TEXT NOT NULL,
        period INTEGER NOT NULL
    )
    """)

    # 2. 学生テーブル（学年カラムを追加）
    cur.execute("""
    CREATE TABLE IF NOT EXISTS students (
        学籍番号 TEXT PRIMARY KEY,
        名前 TEXT NOT NULL,
        生年月日 DATE,
        性別 TEXT,
        専攻 TEXT,
        学年 INTEGER NOT NULL DEFAULT 1
    )
    """)

    # 3. パスワードテーブル
    cur.execute("""
    CREATE TABLE IF NOT EXISTS passwords (
        ユーザID TEXT PRIMARY KEY,
        パスワード TEXT NOT NULL,
        FOREIGN KEY (ユーザID) REFERENCES students (学籍番号)
    )
    """)

    # 4. 選科テーブル
    cur.execute("""
    CREATE TABLE IF NOT EXISTS enrollments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id TEXT NOT NULL,
        subject_id INTEGER NOT NULL,
        grade TEXT,
        UNIQUE(student_id, subject_id),
        FOREIGN KEY (student_id) REFERENCES students (学籍番号),
        FOREIGN KEY (subject_id) REFERENCES subjects (id)
    )
    """)

    # --- テストデータの挿入 ---

    # --- 1. 生徒データ (1〜4年生 各学年2名以上 合計10名) ---
    students_data = [
        # 学籍番号, 名前, 生年月日, 性別, 専攻, 学年
        ('K24000', 'テスト太郎', '2007-04-01', '男性', '情報工学', 1),
        ('K24001', '佐藤美咲', '2007-05-12', '女性', '情報工学', 1),
        ('K24002', '鈴木健太', '2006-08-20', '男性', '知能システム', 2),
        ('K24003', '高橋ひな', '2006-02-14', '女性', '情報工学', 2),
        ('K24004', '田中直樹', '2005-11-30', '男性', 'ネットワーク', 3),
        ('K24005', '伊藤結衣', '2005-07-07', '女性', '知能システム', 3),
        ('K24006', '小林拓海', '2004-03-20', '男性', '情報工学', 4),
        ('K24007', '渡辺真衣', '2004-09-15', '女性', '情報工学', 4),
        ('K24008', '中村亮介', '2007-01-10', '男性', '知能システム', 1), # 1年生3人目
        ('K24009', '加藤彩花', '2005-12-25', '女性', 'ネットワーク', 3)  # 3年生3人目
    ]

    for s in students_data:
        cur.execute("INSERT OR IGNORE INTO students VALUES (?, ?, ?, ?, ?, ?)", s)
        cur.execute("INSERT OR IGNORE INTO passwords VALUES (?, ?)", (s[0], 'password123'))

    # --- 2. 科目データ（4年生向けの科目も追加） ---
    test_subjects = [
        ('プログラミング基礎', '情報工学', 'required', 1, 2, '月', 1),
        ('情報リテラシー', '全専攻', 'required', 1, 1, '金', 1),
        ('データベース論', '情報工学', 'elective', 2, 2, '火', 3),
        ('人工知能概論', '知能システム', 'required', 2, 2, '木', 1),
        ('Webシステム開発', '情報工学', 'elective', 3, 2, '金', 4),
        ('ネットワークセキュリティ', 'ネットワーク', 'required', 3, 2, '火', 2),
        ('卒業研究準備', '情報工学', 'required', 4, 4, '水', 1), # 4年生用
        ('専門英語', '全専攻', 'elective', 4, 2, '木', 5),     # 4年生用
        ('離散数学', '情報工学', 'required', 1, 2, '木', 2),
        ('ロボット制御', '知能システム', 'elective', 3, 2, '月', 5)
    ]

    cur.execute("SELECT COUNT(*) FROM subjects")
    if cur.fetchone()[0] == 0:
        cur.executemany("""
            INSERT INTO subjects (name, major, category, grade, credits, day, period)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, test_subjects)

    conn.commit()
    conn.close()
    print("データベースの初期化が完了しました。")

if __name__ == '__main__':
    init_database()