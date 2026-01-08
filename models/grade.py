from peewee import Model, CharField, IntegerField
from .db import db

class Grade(Model):
    student_number = CharField()    # 学籍番号
    subject_id = IntegerField()     # 科目ID
    unit = IntegerField()           # 単位数
    score = IntegerField()          # 評定

    class Meta:
        database = db