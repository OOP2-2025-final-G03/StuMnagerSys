from peewee import Model, CharField, DateField, ForeignKeyField
from utils.db import db
from .user import User



class Student(Model):
    # user.user_id と一致させる
    # userが削除するときに、student_profileも削除する
    student_id = ForeignKeyField(
        User, 
        backref='student_profile', 
        on_delete='CASCADE', 
        primary_key=True,
        column_name='student_id'
    )
    name = CharField()
    birth_date = DateField(null=True)
    gender = CharField(null=True)  # 'male' / 'female' / 'other'
    major = CharField(null=True)  # 専攻

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