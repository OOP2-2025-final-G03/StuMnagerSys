from peewee import Model, AutoField, CharField, IntegerField, SqliteDatabase
from utils import db

class Subject(Model):
    id = AutoField()                     # INTEGER PRIMARY KEY AUTOINCREMENT
    name = CharField()                   # 科目名
    major = CharField()                  # 専攻
    category = CharField()               # 単位区分（required / elective）
    grade = IntegerField()               # 対象学年
    credits = IntegerField()             # 単位数
    day = CharField()                    # 曜日（月・火など）
    period = IntegerField()              # 時間（1〜6）

    class Meta:
        database = db
        table_name = 'subjects'
