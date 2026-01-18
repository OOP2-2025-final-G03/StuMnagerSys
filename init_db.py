"""
データベースの初期化とランダムデータ生成スクリプトです。
"""

import random
import argparse
from datetime import date, timedelta
from utils.db import db
from models import Password, Student, Teacher, Subject, Grade, User, Enrollment

# --- ランダムのユーザー名と科目 ---
LAST_NAMES = ["山田", "田中", "佐藤", "鈴木", "高橋", "伊藤", "渡辺", "中村", "小林", "加藤"]
FIRST_NAMES_MALE = ["太郎", "一郎", "健太", "浩志", "直樹", "亮", "修", "拓也"]
FIRST_NAMES_FEMALE = ["花子", "恵", "真由美", "陽子", "結衣", "香織", "美紀", "彩"]
DEPARTMENTS = ["情報科学科", "電気電子工学科", "機械工学科", "経営学科"]
SUBJECT_PREFIX = ["基礎", "応用", "実践", "概論", "演習"]
SUBJECT_CORE = ["プログラミング", "アルゴリズム", "データベース", "ネットワーク", "AI", "OS"]

def get_random_date(start_year, end_year):
    """
    指定された年の範囲内でランダムな日付を生成
    """
    start_date = date(start_year, 1, 1)
    end_date = date(end_year, 12, 31)
    time_between_dates = end_date - start_date
    days_between_dates = time_between_dates.days
    random_number_of_days = random.randrange(days_between_dates)
    return start_date + timedelta(days=random_number_of_days)

def clear_db():
    """
    既存のデータを削除
    """
    tables = [Enrollment, Grade, Password, Student, Teacher, Subject, User]
    for table in tables:
        table.delete().execute()
    print("✓ 既存のデータを削除しました")

def generate_random_data(student_count=20, teacher_count=5, subject_count=10):
    """
    ランダムなデータを生成してデータベースに挿入する
    生成されるデータの数は引数で指定可能
    Args:
        student_count (int): 生成する学生の数. 初期値は20.
        teacher_count (int): 生成する教師の数. 初期値は5.
        subject_count (int): 生成する科目の数. 初期値は10.
    """
    db.create_tables([Password, Student, Teacher, Subject, Grade, User, Enrollment], safe=True)
    clear_db()

    # 科目の生成
    subjects = []
    days = ["月", "火", "水", "木", "金"]
    for i in range(subject_count):
        sub = Subject.create(
            name=f"{random.choice(SUBJECT_CORE)}{random.choice(SUBJECT_PREFIX)}",
            department=random.choice(DEPARTMENTS),
            category=random.choice(["required", "elective"]),
            grade=random.randint(1, 4),
            credits=random.choice([2, 4]),
            day=random.choice(days),
            period=random.randint(1, 5)
        )
        subjects.append(sub)
    print(f"✓ 科目データを {subject_count} 件作成しました")

    # 教員の生成 (User -> Teacher -> Password)
    for i in range(1, teacher_count + 1):
        t_id = f"TEA{i:03d}"
        gender = random.choice(['male', 'female'])
        name = random.choice(LAST_NAMES) + (random.choice(FIRST_NAMES_MALE) if gender == 'male' else random.choice(FIRST_NAMES_FEMALE))
        
        User.create(user_id=t_id, role='teacher')
        Teacher.create(
            teacher_id=t_id,
            name=name,
            birth_date=get_random_date(1960, 1990),
            gender=gender,
            department=random.choice(DEPARTMENTS)
        )
        Password.create_password(user_id=t_id, role='teacher', raw_password="password123")
    print(f"✓ 教員データを {teacher_count} 件作成しました")

    # 学生の生成 (User -> Student -> Password)
    student_ids = []
    for i in range(1, student_count + 1):
        s_id = f"STU{i:03d}"
        student_ids.append(s_id)
        gender = random.choice(['male', 'female', 'other'])
        name = random.choice(LAST_NAMES) + (random.choice(FIRST_NAMES_MALE) if gender == 'male' else random.choice(FIRST_NAMES_FEMALE))
        
        User.create(user_id=s_id, role='student')
        Student.create(
            student_id=s_id,
            name=name,
            birth_date=get_random_date(2003, 2006),
            gender=gender,
            department=random.choice(DEPARTMENTS),
            grade=str(random.randint(1, 4))
        )
        Password.create_password(user_id=s_id, role='student', raw_password="password123")
    print(f"✓ 学生データを {student_count} 件作成しました")

    # 履修登録と成績の生成
    for s_id in student_ids:
        # ランダムに2〜4科目を履修登録
        enrolled_subs = random.sample(subjects, random.randint(2, 4))
        for sub in enrolled_subs:
            Enrollment.create(subject=sub, student_id=s_id)
            
            # 成績データの生成
            Grade.create(
                student_id=s_id,
                subject_id=sub.id,
                unit=sub.credits,
                score=random.randint(0, 100)
            )
    print("✓ 履修登録と成績データをランダムに作成しました")

    # 管理者アカウントの作成
    if not User.get_or_none(User.user_id == 'admin'):
        User.create(user_id='admin', role='admin')
        Password.create_password(user_id='admin', role='admin', raw_password='admin')
        print("✓ 管理者を作成しました")

def parse_args():
    """
    コマンドライン引数を解析する
    
    Returns:
        argparse.Namespace: 解析された引数
    """
    parser = argparse.ArgumentParser(description="データベース初期化")

    parser.add_argument(
        "--s",
        type=int,
        default=20,
        help="学生の数（例: 20）"
    )

    parser.add_argument(
        "--t",
        type=int,
        default=5,
        help="教員の数（例: 5）"
    )

    parser.add_argument(
        "--sb",
        type=int,
        default=12,
        help="科目の数（例: 12）"
    )

    return parser.parse_args()

if __name__ == "__main__":
    args = parse_args()
    generate_random_data(student_count=args.s, teacher_count=args.t, subject_count=args.sb)
    print("\n✅ データベースの初期化とランダム生成が完了しました")