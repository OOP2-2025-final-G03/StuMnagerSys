from functools import wraps
from flask import abort
from flask_login import current_user

def role_required(*roles):
    """
    指定された権限（student / teacher / admin）を
    持つユーザーのみアクセス可能にする
    """

    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            if not current_user.is_authenticated:
                abort(401)
            if current_user.role not in roles:
                abort(403)
            return fn(*args, **kwargs)
        return wrapper
    return decorator
