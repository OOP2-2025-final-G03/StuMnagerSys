"""
データベースの初期化スクリプト
テスト用のユーザーデータを作成します
"""

from utils.db import db
from models import Credential, Student, Teacher, Subject, Grade
from datetime import date


def init_database():
    """データベーステーブルの作成とテストデータの挿入"""
    
    # テーブル作成
    db.create_tables([Credential, Student, Teacher, Subject, Grade], safe=True)
    print("✓ テーブルが作成されました")
    
    # 既存データを削除（開発環境用）
    Credential.delete().execute()
    Student.delete().execute()
    Teacher.delete().execute()
    Subject.delete().execute()
    Grade.delete().execute()
    print("✓ 既存データをリセットしました")
    
    # テスト用学生データ
    test_students = [
        {
            'student_id': 'STU001',
            'name': '山田太郎',
            'birth_date': date(2006, 4, 15),
            'gender': 'male',
            'major': '情報科学科',
        },
        {
            'student_id': 'STU002',
            'name': '佐藤花子',
            'birth_date': date(2007, 5, 20),
            'gender': 'female',
            'major': '情報科学科',
        }
    ]
    
    # 学生の作成
    for student_data in test_students:
        Student.create(**student_data)
        print(f"✓ 学生作成: {student_data['student_id']} ({student_data['name']})")
    
    # テスト用教員データ
    test_teachers = [
        {
            'teacher_id': 'TEA001',
            'name': '鈴木教子',
            'age': 45,
            'department': '情報科学科',
            'is_admin': False,
        },
        {
            'teacher_id': 'TEA002',
            'name': '田中校長',
            'age': 58,
            'department': '情報科学科',
            'is_admin': True,  # 管理者権限あり
        }
    ]
    
    # 教員の作成
    for teacher_data in test_teachers:
        Teacher.create(**teacher_data)
        admin_label = " (管理者権限)" if teacher_data['is_admin'] else ""
        print(f"✓ 教員作成: {teacher_data['teacher_id']} ({teacher_data['name']}){admin_label}")
    
    # テスト用認証情報
    test_credentials = [
        {
            'user_id': 'STU001',
            'password_hash': 'password123'
        },
        {
            'user_id': 'STU002',
            'password_hash': 'password456'
        },
        {
            'user_id': 'TEA001',
            'password_hash': 'teacher123'
        },
        {
            'user_id': 'TEA002',
            'password_hash': 'admin123'
        }
    ]
    
    # =========================
    # テスト用科目データ
    # =========================
    test_subjects = [
        {
            'name': 'プログラミング基礎',
            'major': '情報科学科',
            'category': 'required',
            'grade': 1,
            'credits': 2,
            'day': '月',
            'period': 1,
        },
        {
            'name': 'データベース概論',
            'major': '情報科学科',
            'category': 'required',
            'grade': 2,
            'credits': 2,
            'day': '火',
            'period': 3,
        },
        {
            'name': 'アルゴリズム',
            'major': '情報科学科',
            'category': 'required',
            'grade': 2,
            'credits': 3,
            'day': '水',
            'period': 2,
        },
        {
            'name': 'Webアプリケーション開発',
            'major': '情報科学科',
            'category': 'elective',
            'grade': 3,
            'credits': 2,
            'day': '木',
            'period': 4,
        },
        {
            'name': '人工知能入門',
            'major': '情報科学科',
            'category': 'elective',
            'grade': 3,
            'credits': 2,
            'day': '金',
            'period': 5,
        },
    ]

    for subject_data in test_subjects:
        Subject.create(**subject_data)
        print(f"✓ 科目作成: {subject_data['name']} ({subject_data['day']}{subject_data['period']}限)")

    
    # 認証情報の作成
    for cred_data in test_credentials:
        Credential.create(**cred_data)
        print(f"✓ 認証情報作成: {cred_data['user_id']}")
    
    print("\n✅ データベース初期化が完了しました")
    print("\nテストユーザー:")
    print("【学生】")
    print("1. STU001 (山田太郎) / password123")
    print("2. STU002 (佐藤花子) / password456")
    print("【教員】")
    print("3. TEA001 (鈴木教子) / teacher123")
    print("4. TEA002 (田中校長) / admin123 [管理者権限]")

if __name__ == '__main__':
    init_database()