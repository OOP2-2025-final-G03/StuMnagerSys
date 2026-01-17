from peewee import Model, CharField, ForeignKeyField
from utils import db
from models import Subject

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