from peewee import (
    Model,
    CharField,
    DateField,
    IntegerField,
    ForeignKeyField,
    BooleanField
)
from flask_login import UserMixin
from utils import db


class Credential(UserMixin, Model):
    """
    ユーザー認証情報を管理するモデル。
    パスワードとユーザー識別を一元管理する。
    """
    user_id = CharField(primary_key=True)
    password_hash = CharField()

    class Meta:
        database = db
        table_name = 'credentials'

    def get_id(self):
        """
        ユーザーの一意識別子を取得する。

        Returns:
            str: ユーザーID
        """
        return self.user_id
    
    def check_password(self, password_input):
        """
        入力されたパスワードとハッシュを比較する。

        Args:
            password_input (str): 入力されたパスワード

        Returns:
            bool: パスワードが一致する場合 True
        """
        return self.password_hash == password_input


class Student(Model):
    """
    学生情報を管理するモデル。
    """
    student_id = CharField(primary_key=True)  # 学籍番号
    name = CharField()
    birth_date = DateField()
    gender = CharField()  # 'male' / 'female' / 'other'
    major = CharField()  # 専攻

    class Meta:
        database = db
        table_name = 'students'

    def to_dict(self) -> dict:
        """
        学生情報を辞書形式に変換する。

        Returns:
            dict: 学生情報
        """
        return {
            "student_id": self.student_id,
            "name": self.name,
            "birth_date": self.birth_date.isoformat() if self.birth_date else None,
            "gender": self.gender,
            "major": self.major,
        }


class Teacher(Model):
    """
    教員情報を管理するモデル。
    """
    teacher_id = CharField(primary_key=True)  # 教員ID
    name = CharField()
    age = IntegerField()
    department = CharField()  # 学科
    is_admin = BooleanField(default=False)  # 管理者権限フラグ

    class Meta:
        database = db
        table_name = 'teachers'

    def to_dict(self) -> dict:
        """
        教員情報を辞書形式に変換する。

        Returns:
            dict: 教員情報
        """
        return {
            "teacher_id": self.teacher_id,
            "name": self.name,
            "age": self.age,
            "department": self.department,
        }


# 互換性のため User エイリアスを提供
class User(Credential):
    """
    認証用のエイリアスクラス。
    ログイン処理で Credential を User として扱うために使用。
    """
    @staticmethod
    def get(query):
        """
        ユーザーIDで認証情報を取得する。
        
        Args:
            query: peewee のクエリ条件
        
        Returns:
            Credential: マッチしたユーザーの認証情報
        """
        return Credential.get(query)
    
    @staticmethod
    def select():
        """
        全ユーザーの認証情報を取得する。
        
        Returns:
            Query: 全ユーザー
        """
        return Credential.select()
    

