from flask import g, request
import jwt
from models.user import User

SECRET_KEY = "secret_key"

def load_current_user():
    """
    JWTからログイン中ユーザーを取得し g.current_user に設定する。
    """
    g.current_user = None

    auth_header = request.headers.get("Authorization")
    if not auth_header:
        return

    try:
        token = auth_header.split(" ")[1]
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        user_id = payload.get("user_id")
        g.current_user = User.get_or_none(User.user_id == user_id)
    except Exception:
        g.current_user = None