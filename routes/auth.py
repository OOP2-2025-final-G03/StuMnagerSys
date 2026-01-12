from flask import Blueprint, render_template, request, current_app,url_for, session, abort
from flask_login import login_required,login_user,logout_user
from models import Password, Student, Teacher, User
from flask import redirect, flash
from utils import Config
import datetime

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

# ログイン処理
@auth_bp.route('/login', methods=['POST'])
def login():
    """
    ユーザーログイン処理。
    フォームから送信されたユーザーIDとパスワードを検証し、ログインを行う。
    """
    user_id = request.form.get('user_id')
    raw_password = request.form.get('password')
    role = request.form.get('role', 'student')

    password = Password.get_or_none(Password.user_id == user_id)
    if not password or not password.verify_password(raw_password):
        flash("ID またはパスワードが違います")
        return redirect(url_for("auth.login_page", role_type=role))

    user = User.get_or_none(User.user_id == user_id)
    if not user:
        flash("ユーザー情報が存在しません")
        return redirect(url_for("auth.login_page", role_type=role))

    login_user(user)

    # ログイン成功後、ユーザーのロールに応じたダッシュボードにリダイレクト
    if role == 'student':
        return redirect(url_for('dashboard', role_type=role))
    elif role == 'teacher':
        return redirect(url_for('dashboard', role_type=role))
    elif role == 'admin':
        return redirect(url_for('dashboard', role_type=role))
    
    # ロールが一致しない場合はログイン画面に戻る
    flash("ロールが一致しません")
    return redirect(url_for("auth.login_page", role_type=role))

# ログイン画面表示
@auth_bp.route('/login/<role_type>', methods=['GET'])
def login_page(role_type):
    if role_type not in Config.ROLE_TITLES:
        abort(404)
    
    page_title = Config.ROLE_TITLES[role_type]

    return render_template("login.html", title=page_title, role=role_type)

# ログアウト処理
@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


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
