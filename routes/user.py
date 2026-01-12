from flask import Blueprint, render_template, request, current_app, abort, g, jsonify, flash, redirect, url_for
import datetime
from models import Credential, Student, Teacher, Password
from models.user import User
from utils.decorators import login_required, role_required

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

    users = []

    if filter_role == "student":
        role_title = '学生'
        students = Student.select()
        users = [dict(s.to_dict(), role='student') for s in students]
    elif filter_role == "teacher":
        role_title = '教員  '
        teachers = Teacher.select()
        users = [dict(t.to_dict(), role='teacher') for t in teachers]
    else:
        role_title = '全体'
        students = Student.select()
        users = [dict(s.to_dict(), role='student') for s in students]
        teachers = Teacher.select()
        users += [dict(t.to_dict(), role='teacher') for t in teachers]

    return render_template(
        "user/user_list.html",
        active_template='dashboard/admin.html',
        role='admin', 
        active_page='users',
        user_role_name=current_app.config['ROLE_TITLES']['admin'],
        title=role_title,
        users=users,
        current_date=datetime.datetime.now().strftime('%Y年%m月%d日')
    )

    """
    ユーザー一覧を取得するAPIエンドポイント。
    学生は自分自身の情報のみ取得可能。
    教師・スーパーユーザーは全ユーザー情報を取得可能。
    current_user = g.current_user

    if current_user.is_student():
        users = [current_user]
    else:
        users = User.select()

    return jsonify([u.to_dict() for u in users])
    """
    

# =====================
# ユーザー詳細
# =====================
@users_bp.route('/detail', methods=['GET'])
@login_required
def user_detail():
    user_id = request.args.get('user_id')
    if not user_id:
        abort(400, description='user_id required')

    target = User.get_or_none(User.user_id == user_id)
    if not target:
        abort(404)

    if g.current_user.is_student() and g.current_user.user_id != target.user_id:
        abort(403)

    return jsonify(target.to_dict())

# =====================
# ユーザー作成
# =====================
@users_bp.route('/create', methods=['POST'])
#@login_required
#@role_required('superuser')
def create_user():
    data = request.json

    user = User.create(
        user_id=data['user_id'],
        name=data['name'],
        birth_date=data.get('birth_date'),
        role=data['role'],
        department=data.get('department')
    )

    Password.create_password(user, data['password'])

    return jsonify({'message': 'ユーザーが作成されました'}), 201

# =====================
# ユーザー更新
# =====================
@users_bp.route('/update', methods=['POST'])
#@login_required
#@role_required('superuser')
def update_user():
    data = request.json

    user = User.get_or_none(User.user_id == data['user_id'])
    if not user:
        abort(404)

    user.name = data.get('name', user.name)
    user.role = data.get('role', user.role)
    user.department = data.get('department', user.department)
    user.save()

    return jsonify({'message': 'ユーザーが更新されました'})

# =====================
# ユーザー削除
# =====================
@users_bp.route('/delete', methods=['POST'])
#@login_required
#@role_required('superuser')
def delete_user():
    data = request.json

    user = User.get_or_none(User.user_id == data['user_id'])
    if not user:
        abort(404)

    user.delete_instance(recursive=True)
    return jsonify({'message': 'ユーザーが削除されました'})

# =====================
# ユーザー新規作成フォーム表示
# =====================
@users_bp.route('/new', methods=['GET'])
#@login_required
#@role_required('superuser')
def new_user_form():    
    return render_template("user/user_form.html",
                           active_template='dashboard/admin.html',
                           user=None,
                           role='admin', 
                           active_page='users',
                           user_role_name=current_app.config['ROLE_TITLES']['admin'],
                           title='ユーザー新規登録',
                           current_date=datetime.datetime.now().strftime('%Y年%m月%d日')) 

# =====================
#  ユーザー編集フォーム表示
# =====================
@users_bp.route('/<string:user_id>/edit')
#@login_required
#@role_required('superuser')
def edit(user_id):
    user = Credential.get_by_id(user_id)
    return render_template('user/user_form.html',
                            user=user
    )

# =====================
# 更新処理
# =====================
@users_bp.route('/<string:user_id>/edit', methods=['POST'])
#@login_required
#@role_required('superuser')
def update(user_id):
    user = Credential.get_by_id(user_id)

    user.name = request.form['name']
    user.role = request.form['role']
    user.save()

    password = request.form.get('password')
    if password:
        Password.update_password(user, password)

    flash('ユーザー情報を更新しました')
    return redirect(url_for('user.list'))
  

# =====================
# 学生一覧（教師・管理者）
# =====================
@users_bp.route('/students', methods=['GET'])
#@login_required
#@role_required('teacher', 'superuser')
def list_students():
    students = User.select().where(User.role == 'student')
    return jsonify([s.to_dict() for s in students])