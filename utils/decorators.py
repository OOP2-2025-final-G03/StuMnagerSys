from functools import wraps
from flask import g, abort


def login_required(func):
    """
    ログイン必須デコレータ
    JWT認証済みユーザーのみアクセス可能
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        # 認証されていない場合
        if not hasattr(g, "current_user") or g.current_user is None:
            abort(401, description="Login required")
        return func(*args, **kwargs)
    return wrapper


def role_required(*roles):
    """
    指定された権限（student / teacher / admin）を
    持つユーザーのみアクセス可能にする
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # 未ログイン
            if not hasattr(g, "current_user") or g.current_user is None:
                abort(401, description="Login required")

            # role が設定されていない場合
            if not hasattr(g, "current_role") or g.current_role is None:
                abort(403, description="Permission denied")

            # 権限チェック
            if g.current_role not in roles:
                abort(403, description="Permission denied")
            return func(*args, **kwargs)
        return wrapper

    return decorator
