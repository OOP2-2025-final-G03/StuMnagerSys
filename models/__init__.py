from .student import Student
from .teacher import Teacher
from .password import Password
from .subject import Subject
from .grade import Grade
from .user import User
from .enrollment import Enrollment
from .motivation import Motivation  

from utils import db

MODELS = [
    Password,
    Student,
    Teacher,
    Subject,
    Grade,
    User,
    Enrollment,
    Motivation,
]

__all__ = [
    "Student",
    "Teacher",
    "Password",
    "Subject",
    "Grade",
    "User",
    "Enrollment",
    "Motivation",
]

def create_admin_user():
    """
    管理者ユーザーを作成します。
    管理者ユーザーが既に存在する場合は、何もしません。
    """
    
    User.get_or_create(user_id='admin', defaults={'role': 'admin'})
    Password.create_password(user_id='admin', raw_password='admin', role='admin')

# データベースの初期化
def initialize_database():
    """
    データベースの初期化。
    既にデータベースが存在する場合は、初期化をスキップします。
    """
    
    from os import path
    if path.exists("database.db"):
        print("データベースが既に存在しているので、初期化をスキップします。")
        return

    db.connect()
    db.create_tables(MODELS, safe=True)
    create_admin_user()
    db.close()
