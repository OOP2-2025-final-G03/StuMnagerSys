from flask_login import LoginManager, AnonymousUserMixin, user_logged_in, user_logged_out
from flask import request
from datetime import datetime

login_manager = LoginManager()
login_manager.login_view = 'auth.login_page'

class AnonymousUser(AnonymousUserMixin):
    def profile(self):
        return None

    def profile_dict(self):
        return {}

login_manager.anonymous_user = AnonymousUser

def register_login_signals(app):

    @user_logged_in.connect_via(app)
    def on_user_logged_in(sender, user):
        user.last_login = datetime.now()
        user.last_login_ip = request.remote_addr
        user.save()

    @user_logged_out.connect_via(app)
    def on_user_logged_out(sender, user):
        user.last_logout = datetime.now()
        user.save()