from peewee import *
from utils.db import db

class Teacher(Model):
    # Credential.user_id と一致
    teacher_id = CharField(unique=True)

    name = CharField()
    subject = CharField(null=True)

    class Meta:
        database = db
        table_name = 'teachers'
