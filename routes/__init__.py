from .subject import subject_bp
from .user import users_bp
from .auth import auth_bp

# Blueprintをリストとしてまとめる
blueprints = [
    subject_bp,
    users_bp,
    auth_bp
]