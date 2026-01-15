from peewee import Model, CharField, IntegerField
from utils import db

class Grade(Model):
    student_id = CharField()    # 学籍番号
    subject_id = IntegerField()     # 科目ID
    unit = IntegerField()           # 単位数
    score = IntegerField()          # 評定

    class Meta:
        database = db
        table_name = 'grades'
