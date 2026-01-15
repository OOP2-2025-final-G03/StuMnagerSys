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
    department = CharField(null=True)  # 専攻
    grade = CharField(null=True)  # 学年

    class Meta:
        database = db
        table_name = 'students'
        
    def to_dict(self) -> dict:
        """
        学生情報を辞書形式に変換する。

        Returns:
            dict: 学生情報
        """
        user = self.student_id
        if self.gender == 'male':
            gender = '男性'
        elif self.gender == 'female':
            gender = '女性'
        else:
            gender = 'その他'
        return {
            "student_id": user.user_id,
            "role": user.role,
            "name": self.name,
            "birth_date": self.birth_date.isoformat() if self.birth_date else None,
            "gender": gender,
            "department": self.department,
            "grade": self.grade,
        }