from peewee import Model, CharField, DateField, ForeignKeyField
from utils.db import db
from .user import User

class Teacher(Model):
    teacher_id = ForeignKeyField(
        User, 
        backref='teacher_profile', 
        on_delete='CASCADE', 
        primary_key=True,
        column_name='teacher_id'
    )
    name = CharField()
    birth_date = DateField(null=True)  # 生年月日
    gender = CharField(null=True)  # 性別
    department = CharField(null=True)  # 学科

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
                "birth_date": self.birth_date.strftime("%Y-%m-%d") if self.birth_date else None,
                "department": self.department,
                "gender": self.gender,
            }