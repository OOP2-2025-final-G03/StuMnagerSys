from peewee import Model, CharField
from flask_login import UserMixin
from utils.db import db

class User(UserMixin, Model):
    user_id = CharField(primary_key=True)
    role = CharField()   # student / teacher / admin

    class Meta:
        database = db
        table_name = "users"
    
    def get_id(self):
        """
        ユーザーIDを返す。
        """
        return self.user_id
