from flask import Blueprint, render_template, request, current_app, abort, g, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
import datetime
from models import Student, Teacher, User, Password
from utils import role_required

users_bp = Blueprint('user', __name__, url_prefix='/user')

@users_bp.route('/list')
@role_required('admin')
@login_required
def user_list():
    """
    ユーザー管理ページ。
    管理者以外のアクセスは禁止されています。
    """
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
    

@users_bp.route('/search')
@login_required
def user_search():
    print("DEBUG current_user:", g.current_user)
    """
    ユーザー名・ID検索（Subject検索方式）
    """

    keyword = request.args.get('keyword', '').strip()
    role = request.args.get('role', 'all')
    current_user = g.current_user

    if current_user is None:
        abort(401)

    users = []

    # =========================
    # 学生：自分のみ
    # =========================
    if current_user.role == 'student':
        student = Student.get_or_none(Student.student_id == current_user.user_id)
        if student and (
            not keyword or
            keyword in student.student_id or
            keyword in student.name
        ):
            users.append(dict(student.to_dict(), role='student'))

    # =========================
    # 教師・管理者
    # =========================
    else:
        if role in ('student', 'all'):
            query = Student.select()
            if keyword:
                query = query.where(
                    (Student.student_id.contains(keyword)) |
                    (Student.name.contains(keyword))
                )
            users += [dict(s.to_dict(), role='student') for s in query]

        if role in ('teacher', 'all'):
            query = Teacher.select()
            if keyword:
                query = query.where(
                    (Teacher.teacher_id.contains(keyword)) |
                    (Teacher.name.contains(keyword))
                )
            users += [dict(t.to_dict(), role='teacher') for t in query]

    return render_template(
        "user/user_list.html",
        active_template='dashboard/admin.html',
        role=current_user.role,
        active_page='users',
        title='検索結果',
        users=users,
        current_date=datetime.datetime.now().strftime('%Y年%m月%d日')
    )




# =====================
# ユーザー詳細
# =====================
@users_bp.route('/detail', methods=['GET'])
@login_required
def user_detail():
    user_id = request.args.get('user_id')
    user = User.get_or_none(User.user_id == user_id)
    if not user:
        abort(400, description='user_id required')

    if user.role == "student":
        profile = Student.get_or_none(Student.student_id == user_id)
    elif user.role == "teacher":
        profile = Teacher.get_or_none(Teacher.teacher_id == user_id)
    else:
        abort(403)

    if g.current_user.is_student() and g.current_user.user_id != user.user_id:
        abort(403)
        
        user_data = {
            "user_id": profile.student_id if user.role == "teacher" else profile.teacher_id,
            "name": profile.name,
            "role": user.role,
            "department": profile.department if user.role == "teacher" else profile.department,
            "gender": profile.gender,
            "birth_date": profile.birth_date.strftime("%Y-%m-%d") if profile.birth_date else None,
        }

    return jsonify(user_data)



# =====================
# ユーザー作成
# =====================
@users_bp.route('/create', methods=['POST'])
@role_required('admin')
@login_required
def create_user():
    data = request.json
    user_id=data.get('user_id')
    name=data.get('name')
    birth_date=data.get('birth_date')
    role=data.get('role')
    department=data.get('department')
    gender=data.get('gender')
    password_raw=data.get('password')
    
    if role not in ["student", "teacher"]:
        return jsonify({'error': 'Invalid role'}), 400
    try:
        # ユーザーを作成
        User.create(
            user_id=user_id,
            role=role
        )

        # 学生または教員を作成
        if role == "student":
            Student.create(
                student_id=user_id,
                name=name,
                birth_date=birth_date,
                department=department,
                gender=gender
            )
        elif role == "teacher":
            Teacher.create(
                teacher_id=user_id,
                name=name,
                birth_date=birth_date,
                department=department,
                gender=gender
            )
        else:
            return jsonify({'error': 'Invalid role'}), 400

        # パスワードを保存
        Password.create_password(user_id=user_id, raw_password=password_raw, role=role)

        return jsonify({'message': 'ユーザーが作成されました'}), 201

    except Exception as e:
        # ユーザー作成中にエラーが発生した場合
        return jsonify({'error': str(e)}), 500

# =====================
# ユーザー更新
# =====================
@users_bp.route('/update', methods=['POST'])
@role_required('admin')
@login_required
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
@users_bp.route('/delete/<string:user_id>', methods=['POST'])
@role_required('admin')
@login_required
def delete_user(user_id):
    user = User.get_or_none(User.user_id == user_id)
    if not user:
        return jsonify({'error': 'ユーザーが見つかりません'}), 404

    try:
        user.delete_instance(recursive=True)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
    return redirect(url_for('user.user_list'))

# =====================
# ユーザー新規作成フォーム表示
# =====================
@users_bp.route('/new', methods=['GET'])
@role_required('admin')
@login_required
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
@users_bp.route('/<string:user_id>/edit', methods=['GET'])
@role_required('admin')
@login_required
def edit(user_id):
    user = User.get_or_none(User.user_id == user_id)
    if not user:
        abort(404)

    if user.role == "student":
        profile = Student.get_or_none(Student.student_id == user_id)
    elif user.role == "teacher":
        profile = Teacher.get_or_none(Teacher.teacher_id == user_id)
    else:
        abort(403)
    
    user_data = {
        "user_id": profile.teacher_id if user.role == "teacher" else profile.student_id,
        "name": profile.name,
        "role": user.role,
        "department": profile.department if user.role == "teacher" else profile.department,
        "gender": profile.gender,
        "birth_date": profile.birth_date.strftime("%Y-%m-%d") if profile.birth_date else None,
    }

    return render_template(
        "user/user_form.html",
        active_template='dashboard/admin.html',
        user=user_data,
        role='admin', 
        active_page='users',
        user_role_name=current_app.config['ROLE_TITLES']['admin'],
        title='ユーザー新規登録',
        current_date=datetime.datetime.now().strftime('%Y年%m月%d日')
    ) 

# =====================
# 更新処理
# =====================
@users_bp.route('/<string:user_id>/edit', methods=['POST'])
@role_required('admin')
@login_required
def update(user_id):
    # ユーザー情報を取得
    data = request.json
    if not data:
        data = request.form
    
    # ユーザーを取得
    user = User.get_or_none(User.user_id == user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404

    # プロフィールを取得
    if user.role == "student":
        profile = Student.get_or_none(Student.student_id == user_id)
    elif user.role == "teacher":
        profile = Teacher.get_or_none(Teacher.teacher_id == user_id)
    else:
        return jsonify({'error': 'Invalid role'}), 403

    if not profile:
         return jsonify({'error': 'Profile not found'}), 404

    # プロフィール情報を設定
    profile.name = data.get('name')
    profile.birth_date = data.get('birth_date')
    profile.gender = data.get('gender')
    
    # ユーザーロールに応じて department/department を設定
    if user.role == "student":
        profile.department = data.get('department')
    else:
        profile.department = data.get('department')
    
    profile.save()
    
    # 更新パスワードを設定
    password = data.get('password')
    if password:
       pwd_entry = Password.get_or_none(Password.user_id == user_id)
       if pwd_entry:
           pwd_entry.update_password(password)
       else:
           Password.create_password(user_id=user_id, raw_password=password, role=user.role)
    return jsonify({'message': 'ユーザー情報が更新されました'}), 200
  

# =====================
# 学生一覧（教師・管理者）
# =====================
@users_bp.route('/students', methods=['GET'])
@role_required('teacher', 'admin')
@login_required
def list_students():
    users = User.select().where(User.role == 'student')
    students = Student.select().where(Student.student_id << [s.user_id for s in users])
    return jsonify([s.to_dict() for s in students])
