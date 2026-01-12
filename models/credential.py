from peewee import *
from utils.db import db
from .student import Student
from .teacher import Teacher

class Credential(Model):
    user_id = CharField(unique=True)
    password = CharField()
    role = CharField()   # 'student' / 'teacher' / 'superuser'

    class Meta:
        database = db

    def get_user_data(self):
        """
        role に応じて Student / Teacher を取得
        """
        if self.role == "student":
            return Student.get_or_none(Student.student_id == self.user_id)

        elif self.role == "teacher":
            return Teacher.get_or_none(Teacher.teacher_id == self.user_id)

        elif self.role == "superuser":
            return self   # superuser は自分自身でOK

        return None
