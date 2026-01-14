from flask import Blueprint, render_template, request, current_app,url_for, session, abort
from flask_login import login_required,login_user,logout_user
from models import Credential, Student, Teacher
from flask import redirect, flash
from utils.auth import save_session_data, get_current_user_info, clear_session
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
    remember_me = request.form.get('remember_me') == 'on'

    try:
        credential = Credential.get(Credential.user_id == user_id)
        
        # パスワード照合
        if credential.check_password(password):
            # Flask-Loginのlogin_user（remember_me機能を有効化）
            login_user(credential, remember=remember_me)
            
            # ユーザー情報を取得
            user_info = _get_user_info(user_id, role)
            
            # セッションにユーザー情報を保存
            save_session_data(user_id, role, user_info)
            
            # ユーザーのロールに応じてリダイレクト先を変える
            return redirect(url_for('dashboard', role_type=role))
        else:
            flash('パスワードが違います', 'error')
            
    except Credential.DoesNotExist:
        flash('ログインできませんでした', 'error')

    # 失敗したらログイン画面に戻る
    return redirect(url_for('login', role_type=role))

def _get_user_info(user_id, role):
    """
    ユーザーIDとロールからユーザー情報を取得する。

    Args:
        user_id (str): ユーザーID
        role (str): ユーザーロール

    Returns:
        dict: ユーザー情報
    """
    try:
        if role == 'student':
            user = Student.get_or_none(Student.student_id == user_id)
            if user:
                return {
                    'id': user.student_id,
                    'name': user.name,
                    'role': 'student',
                    'birth_date': user.birth_date.isoformat() if user.birth_date else None,
                    'gender': user.gender,
                    'major': user.major,
                }
        elif role in ['teacher', 'admin']:
            user = Teacher.get_or_none(Teacher.teacher_id == user_id)
            if user:
                return {
                    'id': user.teacher_id,
                    'name': user.name,
                    'role': 'admin' if user.is_admin else 'teacher',
                    'age': user.age,
                    'department': user.department,
                }
    except Exception as e:
        print(f"Error getting user info: {e}")
    
    return {'id': user_id, 'role': role}

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
    # セッションをクリア
    clear_session()
    logout_user()
    return redirect(url_for('index'))


@auth_bp.route('/me')
@login_required
def profile():
    """
    ユーザープロフィールページ。
    """
    # セッションから現在のユーザー情報を取得
    current_user_info = get_current_user_info()
    
    if current_user_info is None:
        flash('ログインしてください', 'error')
        return redirect(url_for('login', role_type='student'))

    user_info = current_user_info.get('info', {})
    role = current_user_info.get('role', 'student')

    return render_template(
        "user/profile.html",
        active_template=f'dashboard/{role}.html',
        active_page='profile',
        user=user_info,
        role=role,
        title='アカウント設定',
        current_date=datetime.datetime.now().strftime('%Y年%m月%d日')
    )
    
@auth_bp.route("/me/settings")
@login_required
def settings():
    """
    ユーザー設定ページ。
    """
    pass
