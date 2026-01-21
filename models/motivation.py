from datetime import datetime
from peewee import Model, IntegerField, DateTimeField, ForeignKeyField
from utils import db
from .user import User


class Motivation(Model):
    # 学籍番号(user_id)に紐づける
    student_id = ForeignKeyField(
        User,
        backref='motivation_setting',
        on_delete='CASCADE',
        primary_key=True,
        column_name='student_id'
    )

    # やる気（-100〜100）
    value = IntegerField(default=50)

    updated_at = DateTimeField(default=datetime.now)

    class Meta:
        database = db
        table_name = 'motivations'
