from .subject import subject_bp
from .user import users_bp

# Blueprintをリストとしてまとめる
blueprints = [
    subject_bp,
    users_bp
]