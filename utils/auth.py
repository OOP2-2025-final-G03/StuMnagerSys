from flask import g, request, session
from models import Credential, Student, Teacher

def load_current_user():
    """
    セッションからログイン中ユーザー情報を取得し g.current_user に設定する。
    """
    g.current_user = None
    g.user_role = None
    g.user_info = None

    if 'user_id' not in session:
        return

    try:
        user_id = session.get('user_id')
        credential = Credential.get_or_none(Credential.user_id == user_id)
        
        if credential:
            g.current_user = credential
            g.user_role = session.get('role')
            g.user_info = session.get('user_info', {})
    except Exception:
        g.current_user = None
        g.user_role = None
        g.user_info = None

def save_session_data(user_id, role, user_info=None):
    """
    ユーザーセッション情報をセッションに保存する。

    Args:
        user_id (str): ユーザーID
        role (str): ユーザーロール ('student', 'teacher', 'admin')
        user_info (dict): ユーザー情報（オプション）
    """
    session['user_id'] = user_id
    session['role'] = role
    session['user_info'] = user_info or {}
    session.modified = True

def get_current_user_info():
    """
    現在のログインユーザー情報を取得する。

    Returns:
        dict: ユーザー情報、ログインしていない場合は None
    """
    if 'user_id' not in session:
        return None
    
    return {
        'user_id': session.get('user_id'),
        'role': session.get('role'),
        'info': session.get('user_info', {})
    }

def is_logged_in():
    """
    ユーザーがログイン状態かどうかを確認する。

    Returns:
        bool: ログイン状態の場合 True
    """
    return 'user_id' in session

def get_user_role():
    """
    現在のログインユーザーのロールを取得する。

    Returns:
        str: ユーザーロール（student, teacher, admin）
    """
    return session.get('role')

def clear_session():
    """
    セッションをクリアする。
    """
    session.clear()