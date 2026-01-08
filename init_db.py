"""
データベースの初期化スクリプト
テスト用のユーザーデータを作成します
"""

from utils.db import db
from models import User
from datetime import date

def init_database():
    """データベーステーブルの作成とテストデータの挿入"""
    
    # テーブル作成
    db.create_tables([User], safe=True)
    print("✓ テーブルが作成されました")
    
    # テストユーザーの作成
    test_users = [
        {
            'user_id': 'STU001',
            'name': '山田太郎',
            'birth_date': date(2006, 4, 15),
            'role': 'student',
            'department': '情報科学科',
            'password_hash': 'password123'
        },
        {
            'user_id': 'TEA001',
            'name': '鈴木教子',
            'birth_date': date(1980, 6, 20),
            'role': 'teacher',
            'department': '情報科学科',
            'password_hash': 'teacher123'
        },
        {
            'user_id': 'ADM001',
            'name': '佐藤管理',
            'birth_date': date(1975, 3, 10),
            'role': 'admin',
            'department': None,
            'password_hash': 'admin123'
        }
    ]
    
    # 既存ユーザーを削除（開発環境用）
    User.delete().execute()
    print("✓ 既存ユーザーをリセットしました")
    
    # テストユーザーを作成
    for user_data in test_users:
        User.create(**user_data)
        print(f"✓ ユーザー作成: {user_data['user_id']} ({user_data['name']})")
    
    print("\n✅ データベース初期化が完了しました")
    print("\nテストユーザー:")
    print("1. 学生: STU001 / password123")
    print("2. 教師: TEA001 / teacher123")
    print("3. 管理者: ADM001 / admin123")

if __name__ == '__main__':
    init_database()
