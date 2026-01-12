from peewee import *
from utils.db import db

class Student(Model):
    # Credential.user_id と一致させる
    student_id = CharField(unique=True)

    # 最低限の情報
    name = CharField()
    class_name = CharField(null=True)

    class Meta:
        database = db
        table_name = 'students'
