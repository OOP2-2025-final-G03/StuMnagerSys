from flask import Blueprint, render_template, request, current_app, abort
import datetime

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/me')
def profile():
    """
    ユーザープロフィールページ。
    """

    # デモ用の静的データ
    current_user = {
        'id': 'ADM001',
        'name': 'Admin User',
        'role': 'admin',
        'email': 'admin@system.edu',
        'phone': '090-1234-5678',
        'bio': 'システム管理者です。全ての権限を持っています。',
        'joined_at': '2024年4月1日'
    }

    return render_template(
        "user/profile.html",
        active_template='dashboard/admin.html',
        active_page='profile',
        user=current_user,
        role=current_user['role'],
        title='アカウント設定',
        current_date=datetime.datetime.now().strftime('%Y年%m月%d日')
    )
    
@auth_bp.route("/me/settings")
def settings():
    """
    ユーザー設定ページ。
    """
    pass

@auth_bp.route("/me/logout")
def logout():
    """
    ユーザーログアウト。
    """
    pass
