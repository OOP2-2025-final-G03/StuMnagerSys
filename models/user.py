from peewee import Model, CharField, DateTimeField
from flask_login import UserMixin
from utils.db import db

class User(UserMixin, Model):
    user_id = CharField(primary_key=True)
    role = CharField()   # student / teacher / admin
    last_login = DateTimeField(null=True) # 最終ログイン日時
    last_logout = DateTimeField(null=True) # 最終ログアウト日時
    last_login_ip = CharField(null=True) # 最終ログインIPアドレス

    class Meta:
        database = db
        table_name = "users"
    
    def get_id(self):
        """
        ユーザーIDを返す。
        """
        return self.user_id

    @property
    def profile(self):
        """
        role に応じて Student / Teacher のプロフィールを返す
        """
        if self.role == 'student':
            return self.student_profile.get()
        elif self.role == 'teacher':
            return self.teacher_profile.get()
        elif self.role == 'admin':
            return {
                "user_id": self.user_id,
                "name": self.user_id,
                "role": self.role,
            }
        return None
    
    def profile_dict(self) -> dict | None:
        """
        role に応じたプロフィール情報を dict で返す
        """
        if self.role == 'admin':
            return {
                "user_id": self.user_id,
                "name": self.user_id,
                "role": self.role,
            }
        profile = self.profile
        return profile.to_dict() if profile else {}