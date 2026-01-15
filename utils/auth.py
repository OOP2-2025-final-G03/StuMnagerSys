from flask import g, request
import jwt
from flask_login import current_user
from models.user import User
from models.password import Password

SECRET_KEY = "secret_key"

def load_current_user():
    """
    セッション or JWT からログイン中ユーザーを取得
    """

    g.current_user = None
    g.current_role = None

    # ① Flask-Login（セッション）優先
    if current_user and not current_user.is_anonymous:
        g.current_user = current_user
        password = Password.get_or_none(Password.user_id == current_user.user_id)
        g.current_role = password.role if password else None
        return

    # ② JWT（API用・任意）
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        return

    try:
        token = auth_header.split(" ")[1]
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        user_id = payload.get("user_id")

        user = User.get_or_none(User.user_id == user_id)
        if not user:
            return

        password = Password.get_or_none(Password.user_id == user.user_id)
        g.current_user = user
        g.current_role = password.role if password else None

    except Exception:
        g.current_user = None
        g.current_role = None
