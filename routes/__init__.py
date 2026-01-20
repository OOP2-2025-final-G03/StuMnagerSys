from .subject import subject_bp
from .user import users_bp
from .auth import auth_bp
from .grades import grade_bp
from .analytics import analytics_bp
from .enrollment import enrollment_bp
from .analysis import analysis_bp
# Blueprintをリストとしてまとめる
blueprints = [
    subject_bp,
    users_bp,
    auth_bp,
    grade_bp,
    analytics_bp,
    enrollment_bp,
    analysis_bp
]