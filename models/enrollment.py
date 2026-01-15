from peewee import Model, CharField, IntegerField, ForeignKeyField
from utils import db
from models import Subject, User

class Enrollment(Model):
    subject = ForeignKeyField(
        Subject, 
        backref='enrollments', 
        on_delete='CASCADE'
    )
    
    student_id = CharField()

    class Meta:
        database = db
        table_name = 'enrollments'