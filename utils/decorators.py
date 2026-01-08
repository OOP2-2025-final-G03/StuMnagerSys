from functools import wraps
from flask import g, abort


def login_required(func):
    """
    ログイン必須デコレータ
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not hasattr(g, "current_user") or g.current_user is None:
            abort(401, description="Login required")
        return func(*args, **kwargs)
    return wrapper


def role_required(*roles):
    """
    指定された権限を持つユーザーのみアクセス可能にする
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if g.current_user.role not in roles:
                abort(403, description="Permission denied")
            return func(*args, **kwargs)
        return wrapper

    return decorator
