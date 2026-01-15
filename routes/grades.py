from functools import wraps

from flask import Blueprint, render_template, request, redirect, url_for, flash, abort, g
from peewee import DoesNotExist
from flask_login import login_required, current_user

from utils import Config
from models import Grade, Subject, Student, User


# /grade/... に統一
grade_bp = Blueprint('grade', __name__, url_prefix='/grade')


# -----------------------------
# role_type の一括検証・自動注入
# -----------------------------

@grade_bp.url_value_preprocessor
def capture_role_type(endpoint, values):
    """
    URLに含まれる role_type をここで一括チェックして g に保存する。
    例: /grade/student/list なら g.role_type = "student"
    """
    if not values:
        return

    role_type = values.get('role_type')
    if role_type is None:
        return

    if role_type not in Config.ROLE_TITLES:
        abort(404)

    g.role_type = role_type


@grade_bp.url_defaults
def add_role_type(endpoint, values):
    """
    url_for('grade.xxx', ...) のとき role_type が渡されていなければ、
    現在のリクエストの role_type を自動で補う。
    """
    if not endpoint.startswith('grade.'):
        return

    if 'role_type' in values:
        return

    role = getattr(g, 'role_type', None)
    if role is None:
        role = (request.view_args or {}).get('role_type')

    if role is not None:
        values['role_type'] = role


# -----------------------------
# 権限チェック
# -----------------------------

def require_roles(*allowed_roles):
    """
    ログインユーザーの role が allowed_roles に含まれない場合 403。
    ※URLの role_type ではなく current_user.role を見る（重要）
    """
    def deco(view_func):
        @wraps(view_func)
        def wrapper(*args, **kwargs):
            if not current_user.is_authenticated:
                abort(403)
            if current_user.role not in allowed_roles:
                abort(403)
            return view_func(*args, **kwargs)
        return wrapper
    return deco


# 編集系を許可するロール（存在するものだけ）
_EDIT_ROLES = [r for r in ('admin', 'teacher') if r in Config.ROLE_TITLES]
if not _EDIT_ROLES:
    _EDIT_ROLES = list(Config.ROLE_TITLES.keys())


# -----------------------------
# 成績一覧（/grade/<role_type>/list）
# -----------------------------

@grade_bp.route('/<role_type>/list')
@login_required
def grade_list(role_type):
    """
    - student: 自分の成績だけ表示（student_number の検索は無視）
    - teacher/admin: 学籍番号・科目で検索できる
    """
    # admin 以外は URLのrole_type と自分のroleを一致させる
    if current_user.role != 'admin' and current_user.role != role_type:
        abort(403)

    current_filter = request.args.get('filter', 'all')
    subject = (request.args.get('subject') or '').strip()

    query = Grade.select()

    if role_type == 'student':
        # ★生徒は自分の学籍番号に固定
        query = query.where(Grade.student_id == current_user.get_id())
    else:
        student_number = (request.args.get('student_number') or '').strip()
        if student_number:
            query = query.where(Grade.student_id.contains(student_number))

    # 科目ID or 科目名で検索
    if subject:
        if subject.isdigit():
            query = query.where(Grade.subject_id == int(subject))
        else:
            subject_ids = [
                s.id for s in Subject.select(Subject.id).where(Subject.name.contains(subject))
            ]
            if subject_ids:
                query = query.where(Grade.subject_id.in_(subject_ids))
            else:
                query = query.where(Grade.subject_id == -1)

    # 合格/不合格フィルタ（点数で判定）
    if current_filter == 'pass':
        query = query.where(Grade.score >= 60)
    elif current_filter == 'fail':
        query = query.where(Grade.score < 60)

    query = query.order_by(Grade.student_id.asc(), Grade.subject_id.asc())

    return render_template(
        'grades/grade_list.html',
        title='成績一覧',
        items=query,
        active_template=f'dashboard/{role_type}.html',
        active_page='grades',
    )


# -----------------------------
# 成績作成（/grade/<role_type>/create）
# -----------------------------

@grade_bp.route('/<role_type>/create', methods=['GET', 'POST'])
@login_required
@require_roles(*_EDIT_ROLES)
def create(role_type):
    # 生徒一覧（Student + User）
    student_rows = (
        Student
        .select(Student, User)
        .join(User)
        .where(User.role == 'student')
        .order_by(User.user_id.asc())
    )
    students = [{"student_id": st.student_id.user_id, "name": st.name} for st in student_rows]

    # 科目一覧
    subjects = list(Subject.select().order_by(Subject.id.asc()))

    if request.method == 'POST':
        student_number = (request.form.get('student_number') or '').strip()
        subject_id_raw = (request.form.get('subject_id') or '').strip()
        unit_raw = (request.form.get('unit') or '').strip()
        score_raw = (request.form.get('score') or '').strip()

        if not student_number:
            flash('学籍番号を選択してください。', 'error')
            return render_template(
                'grades/grade_form.html',
                title='成績登録',
                mode='create',
                active_template='content_base.html',
                role=role_type,
                role_type=role_type,
                students=students,
                subjects=subjects,
            )

        if not subject_id_raw.isdigit():
            flash('科目を選択してください。', 'error')
            return render_template(
                'grades/grade_form.html',
                title='成績登録',
                mode='create',
                active_template='content_base.html',
                role=role_type,
                role_type=role_type,
                students=students,
                subjects=subjects,
            )

        if not (unit_raw.isdigit() and score_raw.isdigit()):
            flash('単位 / 点数 は数字で入力してください。', 'error')
            return render_template(
                'grades/grade_form.html',
                title='成績登録',
                mode='create',
                active_template='content_base.html',
                role=role_type,
                role_type=role_type,
                students=students,
                subjects=subjects,
            )

        subject_id = int(subject_id_raw)
        unit = int(unit_raw)
        score = int(score_raw)

        if unit < 0:
            flash('単位は0以上で入力してください。', 'error')
            return render_template(
                'grades/grade_form.html',
                title='成績登録',
                mode='create',
                active_template='content_base.html',
                role=role_type,
                role_type=role_type,
                students=students,
                subjects=subjects,
            )

        if not (0 <= score <= 100):
            flash('点数は0〜100で入力してください。', 'error')
            return render_template(
                'grades/grade_form.html',
                title='成績登録',
                mode='create',
                active_template='content_base.html',
                role=role_type,
                role_type=role_type,
                students=students,
                subjects=subjects,
            )

        exists = Grade.select().where(
            (Grade.student_id == student_number) &
            (Grade.subject_id == subject_id)
        ).exists()
        if exists:
            flash('同じ学籍番号・科目IDの成績が既に存在します。編集してください。', 'error')
            return redirect(url_for('grade.grade_list'))

        Grade.create(student_id=student_number, subject_id=subject_id, unit=unit, score=score)
        flash('成績を登録しました。', 'success')
        return redirect(url_for('grade.grade_list'))

    return render_template(
        'grades/grade_form.html',
        title='成績登録',
        mode='create',
        active_template='content_base.html',
        role=role_type,
        role_type=role_type,
        students=students,
        subjects=subjects,
    )


# -----------------------------
# 成績編集（/grade/<role_type>/edit/...）
# -----------------------------

@grade_bp.route('/<role_type>/edit/<student_number>/<int:subject_id>', methods=['GET', 'POST'])
@login_required
@require_roles(*_EDIT_ROLES)
def edit(role_type, student_number, subject_id):
    try:
        grade = Grade.get(
            (Grade.student_id == student_number) &
            (Grade.subject_id == subject_id)
        )
    except DoesNotExist:
        flash('対象の成績が見つかりませんでした。', 'error')
        return redirect(url_for('grade.grade_list'))

    if request.method == 'POST':
        unit_raw = (request.form.get('unit') or '').strip()
        score_raw = (request.form.get('score') or '').strip()

        if not (unit_raw.isdigit() and score_raw.isdigit()):
            flash('単位 / 点数 は数字で入力してください。', 'error')
            return render_template(
                'grades/grade_form.html',
                title='成績編集',
                mode='edit',
                grade=grade,
                active_template='content_base.html',
                role=role_type,
                role_type=role_type
            )

        unit = int(unit_raw)
        score = int(score_raw)

        if unit < 0:
            flash('単位は0以上で入力してください。', 'error')
            return render_template(
                'grades/grade_form.html',
                title='成績編集',
                mode='edit',
                grade=grade,
                active_template='content_base.html',
                role=role_type,
                role_type=role_type
            )

        if not (0 <= score <= 100):
            flash('点数は0〜100で入力してください。', 'error')
            return render_template(
                'grades/grade_form.html',
                title='成績編集',
                mode='edit',
                grade=grade,
                active_template='content_base.html',
                role=role_type,
                role_type=role_type
            )

        grade.unit = unit
        grade.score = score
        grade.save()

        flash('成績を更新しました。', 'success')
        return redirect(url_for('grade.grade_list'))

    return render_template(
        'grades/grade_form.html',
        title='成績編集',
        mode='edit',
        grade=grade,
        active_template='content_base.html',
        role=role_type,
        role_type=role_type
    )


# -----------------------------
# 成績削除（/grade/<role_type>/delete/...）
# -----------------------------

@grade_bp.route('/<role_type>/delete/<student_number>/<int:subject_id>')
@login_required
@require_roles(*_EDIT_ROLES)
def delete(role_type, student_number, subject_id):
    try:
        grade = Grade.get(
            (Grade.student_id == student_number) &
            (Grade.subject_id == subject_id)
        )
        grade.delete_instance()
        flash('成績を削除しました。', 'success')
    except DoesNotExist:
        flash('対象の成績が見つかりませんでした。', 'error')

    return redirect(url_for('grade.grade_list'))
