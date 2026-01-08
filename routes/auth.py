from flask import Blueprint, render_template, request, current_app,url_for, session, abort
from flask_login import login_required,login_user,logout_user
from models import Credential, Student, Teacher
from flask import redirect, flash
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
    password = request.form.get('password')
    role = request.form.get('role', 'student')

    try:
        credential = Credential.get(Credential.user_id == user_id)
        
        # パスワード照合
        if credential.check_password(password):
            login_user(credential)
            # ユーザーのロールに応じてリダイレクト先を変える
            return redirect(url_for('dashboard', role_type=role))
        else:
            flash('パスワードが違います', 'error')
            
    except Credential.DoesNotExist:
        flash('ログインできませんでした', 'error')

    # 失敗したらログイン画面に戻る
    return redirect(url_for('login', role_type=role))

# ログイン画面表示
@auth_bp.route('/login', methods=['GET'])
def login_page():
    """
    ログイン画面を表示する。
    """
    return redirect(url_for('login'))

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
