"""
データベースの初期化スクリプト
テスト用のユーザーデータを作成します
"""

from utils.db import db
from models import Password, Student, Teacher, Subject, Grade, User, Enrollment
from datetime import date

def init_database():
    """データベーステーブルの作成とテストデータの挿入"""
    
    # テーブル作成
    db.create_tables([Password, Student, Teacher, Subject, Grade, User, Enrollment], safe=True)
    print("✓ テーブルが作成されました")
    
    # 既存データを削除（開発環境用）
    Password.delete().execute()
    Student.delete().execute()
    Teacher.delete().execute()
    Subject.delete().execute()
    Grade.delete().execute()
    User.delete().execute()
    Enrollment.delete().execute()
    print("✓ 既存データをリセットしました")
    
    # テスト用学生データ
    test_students = [
        {
            'student_id': 'STU001',
            'name': '山田太郎',
            'birth_date': date(2006, 4, 15),
            'gender': 'male',
            'department': '情報科学科',
            'grade': '1',
        },
        {
            'student_id': 'STU002',
            'name': '佐藤花子',
            'birth_date': date(2007, 5, 20),
            'gender': 'female',
            'department': '情報科学科',
            'grade': '2',
        },
        {
            'student_id': 'STU003',
            'name': '鈴木一郎',
            'birth_date': date(2008, 6, 30),
            'gender': 'male',
            'department': '情報科学科',
            'grade': '3',
        },
        {
            'student_id': 'STU004',
            'name': '高橋花子',
            'birth_date': date(2009, 7, 10),
            'gender': 'female',
            'department': '情報科学科',
            'grade': '4',
        },
        {
            'student_id': 'STU005',
            'name': '伊藤太郎',
            'birth_date': date(2010, 8, 15),
            'gender': 'male',
            'department': '情報科学科',
            'grade': '5',
        },
        {
            'student_id': 'STU006',
            'name': '渡辺花子',
            'birth_date': date(2011, 9, 25),
            'gender': 'female',
            'department': '情報科学科',
            'grade': '6',
        },
        {
            'student_id': 'STU007',
            'name': '高橋一郎',
            'birth_date': date(2012, 10, 5),
            'gender': 'male',
            'department': '情報科学科',
            'grade': '7',
        },
        {
            'student_id': 'STU008',
            'name': '伊藤花子',
            'birth_date': date(2013, 11, 18),
            'gender': 'female',
            'department': '情報科学科',
            'grade': '8',
        },
        {
            'student_id': 'STU009',
            'name': '渡辺一郎',
            'birth_date': date(2014, 12, 30),
            'gender': 'male',
            'department': '情報科学科',
            'grade': '9',
        },
        {
            'student_id': 'STU010',
            'name': '高橋花子',
            'birth_date': date(2015, 1, 20),
            'gender': 'female',
            'department': '情報科学科',
            'grade': '10',
        },
    ]

    
    # テスト用教員データ
    test_teachers = [
        {
            'teacher_id': 'TEA001',
            'name': '鈴木教子',
            'birth_date': date(1976, 3, 10),
            'gender': 'male',
            'department': '情報科学科',
        },
        {
            'teacher_id': 'TEA002',
            'name': '田中校長',
            'birth_date': date(1968, 8, 25),
            'gender': 'male',
            'department': '情報科学科',
        }
    ]
    
    
    # テスト用認証情報
    test_credentials = [
        {
            'user_id': 'STU001',
            'password': 'password123',
            'role':'student'
        },
        {
            'user_id': 'STU002',
            'password': 'password456',
            'role':'student'
        },
        {
            'user_id': 'TEA001',
            'password': 'teacher123',
            'role':'teacher'
        },
        {
            'user_id': 'TEA002',
            'password': 'teacher456',
            'role':'teacher'
        },
        {
            'user_id': 'admin',
            'password': 'admin',
            'role':'admin'
        },
        {
            'user_id': 'STU003',
            'password': 'password789',
            'role':'student'
        },
        {
            'user_id': 'STU004',
            'password': 'password101',
            'role':'student'
        },
        {
            'user_id': 'STU005',
            'password': 'password102',
            'role':'student'
        },
        {
            'user_id': 'STU006',
            'password': 'password103',
            'role':'student'
        },
        {
            'user_id': 'STU007',
            'password': 'password104',
            'role':'student'
        },
        {
            'user_id': 'STU008',
            'password': 'password105',
            'role':'student'
        },
        {
            'user_id': 'STU009',
            'password': 'password106',
            'role':'student'
        },
        {
            'user_id': 'STU010',
            'password': 'password107',
            'role':'student'
        }
    ]
    
    test_users = [
        {
            'user_id': 'STU001',
            'role': 'student',
        },
        {
            'user_id': 'STU002',
            'role': 'student',
        },
        {
            'user_id': 'TEA001',
            'role': 'teacher',
        },
        {
            'user_id': 'TEA002',
            'role': 'teacher',
        },
        {
            'user_id': 'STU003',
            'role': 'student',
        },
        {
            'user_id': 'STU004',
            'role': 'student',
        },
        {
            'user_id': 'STU005',
            'role': 'student',
        },
        {
            'user_id': 'STU006',
            'role': 'student',
        },
        {
            'user_id': 'STU007',
            'role': 'student',
        },
        {
            'user_id': 'STU008',
            'role': 'student',
        },
        {
            'user_id': 'STU009',
            'role': 'student',
        },
        {
            'user_id': 'STU010',
            'role': 'student',
        },
        {
            'user_id': 'admin',
            'role': 'admin',
        }
    ]
    
    # =========================
    # テスト用科目データ
    # =========================
    test_subjects = [
        {
            'name': 'プログラミング基礎',
            'department': '情報科学科',
            'category': 'required',
            'grade': 1,
            'credits': 2,
            'day': '月',
            'period': 1,
        },
        {
            'name': 'データベース概論',
            'department': '情報科学科',
            'category': 'required',
            'grade': 2,
            'credits': 2,
            'day': '火',
            'period': 3,
        },
        {
            'name': 'アルゴリズム',
            'department': '情報科学科',
            'category': 'required',
            'grade': 2,
            'credits': 3,
            'day': '水',
            'period': 2,
        },
        {
            'name': 'Webアプリケーション開発',
            'department': '情報科学科',
            'category': 'elective',
            'grade': 3,
            'credits': 2,
            'day': '木',
            'period': 4,
        },
        {
            'name': '人工知能入門',
            'department': '情報科学科',
            'category': 'elective',
            'grade': 3,
            'credits': 2,
            'day': '金',
            'period': 5,
        },
    ]
    
    for user_data in test_users:
        User.create(**user_data)
        print(f"✓ ユーザー作成: {user_data['user_id']} ({user_data['role']})")
    

    for subject_data in test_subjects:
        Subject.create(**subject_data)
        print(f"✓ 科目作成: {subject_data['name']} ({subject_data['day']}{subject_data['period']}限)")
        
    # 教員の作成
    for teacher_data in test_teachers:
        Teacher.create(**teacher_data)
        print(f"✓ 教員作成: {teacher_data['teacher_id']} ({teacher_data['name']})")
    
    # 学生の作成
    for student_data in test_students:
        Student.create(**student_data)
        print(f"✓ 学生作成: {student_data['student_id']} ({student_data['name']})")

    
    # 認証情報の作成
    for cred_data in test_credentials:
        Password.create_password(user_id=cred_data['user_id'], raw_password=cred_data['password'], role=cred_data['role'])
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