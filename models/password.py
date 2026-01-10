from peewee import (
    Model,
    CharField,
    ForeignKeyField
)
from werkzeug.security import generate_password_hash, check_password_hash

from utils.db import db
from models.user import User


class Password(Model):
    """
    パスワード情報を管理するモデル。
    パスワードは平文では保存せず、ハッシュ化して保存する。
    """

    user = ForeignKeyField(
        User,
        backref='password',
        primary_key=True,
        on_delete='CASCADE'
    )
    password_hash = CharField()

    class Meta:
        database = db
        table_name = 'passwords'

    @classmethod
    def create_password(cls, user: User, raw_password: str):
        """
        パスワードをハッシュ化して保存する。

        Args:
            user (User): 対象ユーザー
            raw_password (str): 平文パスワード

        Returns:
            Password: 作成された Password インスタンス
        """
        return cls.create(
            user=user,
            password_hash=generate_password_hash(raw_password)
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
