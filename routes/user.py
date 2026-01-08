from flask import Blueprint, render_template, request, current_app, abort
import datetime

users_bp = Blueprint('user', __name__, url_prefix='/user')

@users_bp.route('/list')
def user_list():
    """
    ユーザー管理ページ。
    管理者以外のアクセスは禁止されています。
    """
    
    # TODO:重要
    # ここでセッションや認証情報をチェックして、
    # ユーザーが正しいロールでログインしているか確認する必要があります。
    # role_type = session.get('role')
    # if role_type != 'admin':
    #    abort(404)

    filter_role = request.args.get('role', 'all')
    # デモ用の静的データ
    students = [
        {'id': 'S001', 'name': '11 太郎', 'role': 'student', 'info': '1-A', 'status': '在籍'},
        {'id': 'S002', 'name': '22 花子', 'role': 'student', 'info': '1-B', 'status': '在籍'},
    ]
    teachers = [
        {'id': 'T001', 'name': '11 先生', 'role': 'teacher', 'info': '数学', 'status': '常勤'},
        {'id': 'T002', 'name': '22 先生', 'role': 'teacher', 'info': '英語', 'status': '非常勤'},
    ]

    users_data = []
    if filter_role == 'student':
        users_data = students
        page_title = 'ユーザー管理 (学生)'
    elif filter_role == 'teacher':
        users_data = teachers
        page_title = 'ユーザー管理 (教員)'
    else:
        users_data = students + teachers
        page_title = 'ユーザー管理 (すべて)'

    return render_template(
        "user/user_list.html",
        active_template='dashboard/admin.html',
        role='admin', 
        active_page='users',
        user_role_name=current_app.config['ROLE_TITLES']['admin'],
        title=page_title,
        users=users_data,
        current_date=datetime.datetime.now().strftime('%Y年%m月%d日')
    )
