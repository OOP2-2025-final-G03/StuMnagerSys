from flask import Blueprint, render_template, request, url_for, session, abort
from flask_login import login_required,login_user,logout_user, current_user
from models import Password, Student, Teacher, User
from flask import redirect, flash
from utils import Config, login_manager
import datetime

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@login_manager.user_loader
def load_user(user_id):
    try:
        return User.get(User.user_id == user_id)
    except User.DoesNotExist:
        return None
# ログイン処理
@auth_bp.route('/login', methods=['POST'])
def login():
    """
    ユーザーログイン処理。
    フォームから送信されたユーザーIDとパスワードを検証し、ログインを行う。
    """
    user_id = request.form.get('user_id')
    raw_password = request.form.get('password')
    remember = 'remember' in request.form

    password = Password.get_or_none(Password.user_id == user_id)
    if not password or not password.verify_password(raw_password):
        flash("ID またはパスワードが違います")
        return redirect(url_for("auth.login_page"), title="学生管理システム")

    user = User.get_or_none(User.user_id == user_id)
    if not user:
        flash("ユーザー情報が存在しません")
        return redirect(url_for("auth.login_page"), title="学生管理システム")
    print(remember)

    login_user(user, remember=remember)

    # ログイン成功後、ユーザーのロールに応じたダッシュボードにリダイレクト
    if current_user.role == user.role:
        return redirect(url_for('dashboard'))
    
    # ロールが一致しない場合はログイン画面に戻る
    flash("ロールが一致しません")
    return redirect(url_for("auth.login_page"), title="学生管理システム")

# ログイン画面表示
@auth_bp.route('/login', methods=['GET'])
def login_page():
    return render_template("login.html", title="学生管理システム")

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
    current_user_data = {
        'id': current_user.user_id,
        'name': current_user.profile_dict().get('name', 'ユーザー'),
        'role': current_user.role,
        'grade': current_user.profile_dict().get('grade', '未設定'),
        'last_login_ip': current_user.last_login_ip,
        'last_login_date': current_user.last_login,
        'birth_date': current_user.profile_dict().get('birth_date', '未設定'),
        'gender': current_user.profile_dict().get('gender', '未設定'),
        'department': current_user.profile_dict().get('department', '未設定'),
    }

    return render_template(
        "user/profile.html",
        active_template=f'dashboard/{current_user.role}.html',
        active_page='profile',
        user=current_user_data,
        title='アカウント設定',
        current_date=datetime.datetime.now().strftime('%Y年%m月%d日')
    )
    
@auth_bp.route("/me/settings")
def settings():
    """
    ユーザー設定ページ。
    """
    pass
