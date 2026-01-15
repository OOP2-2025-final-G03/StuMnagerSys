from .student import Student
from .teacher import Teacher
from .password import Password
from .subject import Subject
from .grade import Grade
from .user import User
from .enrollment import Enrollment

from utils import db

MODELS = [
    Password,
    Student,
    Teacher,
    Subject,
    Grade,
    User,
    Enrollment
]

def create_admin_user():
    User.get_or_create(user_id='admin', defaults={'role': 'admin'})
    Password.create_password(user_id='admin', raw_password='admin', role='admin')
    
# データベースの初期化
def initialize_database():
    db.connect()
    db.create_tables(MODELS, safe=True)
    create_admin_user()
    db.close()
