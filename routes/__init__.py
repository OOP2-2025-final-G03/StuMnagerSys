from .subject import subject_bp
from .user import users_bp
from .enrollments import enrollment_bp

# Blueprintをリストとしてまとめる
blueprints = [
    subject_bp,
    users_bp,
    enrollment_bp
]