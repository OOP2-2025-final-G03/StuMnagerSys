from peewee import Model, IntegerField, CharField
from utils import db


class Subject(Model):
    """
    科目テーブルのモデル
    """

    subject_id = IntegerField(primary_key=True)  # 科目ID
    subject_name = CharField()                   # 科目名
    major = CharField()                          # 専攻
    credit_category = CharField()                # 単位区分
    target_grade = IntegerField()                # 対象学年
    credits = IntegerField()                     # 単位数
    day_of_week = CharField()                    # 曜日

    class Meta:
        database = db
        table_name = "subject"