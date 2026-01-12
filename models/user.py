from peewee import *
from .db import db

class User(Model):
    user_id = CharField(unique=True)
    name = CharField()
    birth_date = DateField(null=True)
    department = CharField(null=True)

    class Meta:
<<<<<<< HEAD
        database = db
=======
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
    

>>>>>>> a4f91b23361916b38a4e31635da66e4d029f1380
