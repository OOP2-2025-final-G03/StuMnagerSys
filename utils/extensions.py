from flask_login import LoginManager, AnonymousUserMixin, user_logged_in, user_logged_out
from flask import request
from datetime import datetime

login_manager = LoginManager()
login_manager.login_view = 'auth.login_page'

class AnonymousUser(AnonymousUserMixin):
    """
    ログインしていない場合のユーザークラス
    """
    def profile(self):
        """
        ログインしていない場合、空の辞書を返す
        """
        return None

    def profile_dict(self):
        """
        ログインしていない場合、空の辞書を返す
        """
        return {}

login_manager.anonymous_user = AnonymousUser

def register_login_signals(app):
    """
    ログイン信号を登録する関数
    """

    @user_logged_in.connect_via(app)
    def on_user_logged_in(sender, user):
        """
        ユーザーがログインした場合の処理(ログイン日時、ログインIPアドレスの記録)
        """
        user.last_login = datetime.now()
        user.last_login_ip = request.remote_addr
        user.save()

    @user_logged_out.connect_via(app)
    def on_user_logged_out(sender, user):
        """
        ユーザーがログアウトした場合の処理(ログアウト日時の記録)
        """
        user.last_logout = datetime.now()
        user.save()