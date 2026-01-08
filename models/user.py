from peewee import (
    Model,
    CharField,
    DateField
)
from flask_login import UserMixin
from utils import db


class User(UserMixin,Model):
    """
    ユーザー情報を管理するモデル。
    学生・教師・スーパーユーザーを role で区別する。
    """

    user_id = CharField(primary_key=True)
    name = CharField()
    birth_date = DateField(null=True)
    role = CharField()  # 'student' / 'teacher' / 'superuser'
    department = CharField(null=True)
    password_hash = CharField()

    class Meta:
        database = db
        table_name = 'users'

    def get_id(self):
        """
        ユーザーの一意識別子を取得する。

        Returns:
            str: ユーザーID
        """
        return self.user_id
    
    def check_password(self, password_input):
        # ここでハッシュ化のチェックを行いますが、まずは単純比較でOKならこう書きます
        return self.password_hash == password_input

    def is_student(self) -> bool:
        """
        学生かどうかを判定する。

        Returns:
            bool: 学生の場合 True
        """
        return self.role == 'student'

    def is_teacher(self) -> bool:
        """
        教師かどうかを判定する。

        Returns:
            bool: 教師の場合 True
        """
        return self.role == 'teacher'

    def is_superuser(self) -> bool:
        """
        スーパーユーザーかどうかを判定する。

        Returns:
            bool: スーパーユーザーの場合 True
        """
        return self.role == 'superuser'
    

    def to_dict(self) -> dict:
        """
        ユーザー情報を辞書形式に変換する。
        APIレスポンス用。

        Returns:
            dict: ユーザー情報
        """
        return {
            "user_id": self.user_id,
            "name": self.name,
            "birth_date": self.birth_date.isoformat() if self.birth_date else None,
            "role": self.role,
            "department": self.department,
        }
    

