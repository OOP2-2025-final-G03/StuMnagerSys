from peewee import (
    Model,
    CharField,
    ForeignKeyField,
)
from werkzeug.security import generate_password_hash, check_password_hash

from utils import db
from .user import User


class Password(Model):
    """
    パスワード情報を管理するモデル。
    パスワードは平文では保存せず、ハッシュ化して保存する。
    """

    user_id = ForeignKeyField(
        User, 
        backref='auth_info', 
        on_delete='CASCADE', 
        primary_key=True,
        column_name='user_id'
    )
    password_hash = CharField()
    role = CharField()

    class Meta:
        database = db
        table_name = 'passwords'
        
    @classmethod
    def create_password(cls, user_id: str, role: str, raw_password: str):
        """
        パスワードをハッシュ化して保存する。

        Args:
            user_id (str): 対象ユーザーの ID
            role (str): ユーザーのロール (student/teacher/admin)
            raw_password (str): 平文パスワード

        """
        Password.create(
            user_id=user_id,
            password_hash=generate_password_hash(raw_password),
            role=role
        )

    def verify_password(self, raw_password: str) -> bool:
        """
        入力されたパスワードが正しいか検証する。

        Args:
            raw_password (str): 入力された平文パスワード

        Returns:
            bool: 正しい場合 True
        """
        return check_password_hash(self.password_hash, raw_password)
    
    def update_password(self, raw_password: str):
        """
        ユーザーのパスワードを更新する。

        Args:
            raw_password (str): 新しい平文パスワード
        """
        self.password_hash = generate_password_hash(raw_password)
        self.save()