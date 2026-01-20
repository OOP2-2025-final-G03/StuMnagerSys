from functools import wraps
from datetime import datetime

from flask import Blueprint, render_template, request, redirect, url_for, flash, abort, g, jsonify
from peewee import DoesNotExist, OperationalError
from flask_login import login_required, current_user

from utils import Config
from models import Grade, Subject, Student, User, Enrollment, Motivation

grade_bp = Blueprint('grade', __name__, url_prefix='/grade')


@grade_bp.url_value_preprocessor
def capture_role_type(endpoint, values):
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
    if not endpoint.startswith('grade.'):
        return
    if 'role_type' in values:
        return
    role = getattr(g, 'role_type', None)
    if role is None:
        role = (request.view_args or {}).get('role_type')
    if role is not None:
        values['role_type'] = role


def require_roles(*allowed_roles):
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


_EDIT_ROLES = [r for r in ('admin', 'teacher') if r in Config.ROLE_TITLES]
if not _EDIT_ROLES:
    _EDIT_ROLES = list(Config.ROLE_TITLES.keys())


@grade_bp.route('/<role_type>/list')
@login_required
def grade_list(role_type):
    # admin 以外は URLのrole_type と自分のroleを一致させる
    if current_user.role != 'admin' and current_user.role != role_type:
        abort(403)

    is_student_view = (current_user.role == 'student')
    current_filter = request.args.get('filter', 'all')
    subject = (request.args.get('subject') or '').strip()

    query = Grade.select()

    if is_student_view:
        query = query.where(Grade.student_id == current_user.get_id())
    else:
        student_number = (request.args.get('student_number') or '').strip()
        if student_number:
            query = query.where(Grade.student_id.contains(student_number))

    # 科目ID or 科目名
    if subject:
        if subject.isdigit():
            query = query.where(Grade.subject_id == int(subject))
        else:
            subject_ids = [s.id for s in Subject.select(Subject.id).where(Subject.name.contains(subject))]
            if subject_ids:
                query = query.where(Grade.subject_id.in_(subject_ids))
            else:
                query = query.where(Grade.subject_id == -1)

    # 合格/不合格
    if current_filter == 'pass':
        query = query.where(Grade.score >= 60)
    elif current_filter == 'fail':
        query = query.where(Grade.score < 60)

    query = query.order_by(Grade.student_id.asc(), Grade.subject_id.asc())
    grade_items = list(query)

    subject_map = {s.id: s.name for s in Subject.select(Subject.id, Subject.name)}

    student_name_map = {}
    if not is_student_view:
        student_ids = sorted({g.student_id for g in grade_items})
        if student_ids:
            rows = (
                Student.select(Student, User)
                .join(User)
                .where(User.user_id.in_(student_ids))
            )
            student_name_map = {st.student_id.user_id: st.name for st in rows}

    # 生徒の「今後の頑張り」初期値
    motivation_value = None
    if is_student_view:
        user = User.get_by_id(current_user.get_id())
        try:
            m = Motivation.get_or_none(Motivation.student_id == user)
            motivation_value = m.value if m else 50
        except OperationalError:
            # motivations テーブルが無い場合は作って復旧
            Motivation.create_table(safe=True)
            m = Motivation.get_or_none(Motivation.student_id == user)
            motivation_value = m.value if m else 50

    return render_template(
        'grades/grade_list.html',
        title='成績一覧',
        items=grade_items,
        active_template=f'dashboard/{role_type}.html',
        active_page='grades',
        subject_map=subject_map,
        student_name_map=student_name_map,
        is_student_view=is_student_view,
        motivation_value=motivation_value,
    )


@grade_bp.route('/<role_type>/motivation', methods=['GET', 'POST'])
@login_required
def motivation(role_type):
    # 生徒のみ利用可
    if current_user.role != 'student' or role_type != 'student':
        abort(403)

    user = User.get_by_id(current_user.get_id())

    # テーブルが無いなら作って復旧
    try:
        Motivation.create_table(safe=True)
    except Exception:
        pass

    if request.method == 'GET':
        m = Motivation.get_or_none(Motivation.student_id == user)
        return jsonify({"ok": True, "value": int(m.value if m else 50)})

    payload = request.get_json(silent=True) or {}
    raw = payload.get('value', None)
    if raw is None:
        raw = request.form.get('value')

    try:
        value = int(raw)
    except Exception:
        return jsonify({"ok": False, "error": "value must be int"}), 400

    value = max(0, min(100, value))

    m, created = Motivation.get_or_create(student_id=user, defaults={"value": value})
    if not created:
        m.value = value
        m.updated_at = datetime.now()
        m.save()

    return jsonify({"ok": True, "value": int(value)})


@grade_bp.route('/<role_type>/enrolled_subjects/<student_number>')
@login_required
@require_roles(*_EDIT_ROLES)
def enrolled_subjects(role_type, student_number):
    if current_user.role != 'admin' and current_user.role != role_type:
        abort(403)

    rows = (
        Enrollment.select(Enrollment, Subject)
        .join(Subject)
        .where(Enrollment.student_id == student_number)
        .order_by(Subject.id.asc())
    )

    data = [{"id": e.subject.id, "name": e.subject.name, "credits": e.subject.credits} for e in rows]
    return jsonify(data)


@grade_bp.route('/<role_type>/create', methods=['GET', 'POST'])
@login_required
@require_roles(*_EDIT_ROLES)
def create(role_type):
    student_rows = (
        Student.select(Student, User)
        .join(User)
        .where(User.role == 'student')
        .order_by(User.user_id.asc())
    )
    students = [{"student_id": st.student_id.user_id, "name": st.name} for st in student_rows]

    # 科目は「学籍番号選択後にAJAXで取得」するので初期は空
    subjects = []

    if request.method == 'POST':
        student_number = (request.form.get('student_number') or '').strip()
        subject_id_raw = (request.form.get('subject_id') or '').strip()
        score_raw = (request.form.get('score') or '').strip()

        if not student_number:
            flash('学籍番号を選択してください。', 'error')
            return render_template('grades/grade_form.html', title='成績登録', mode='create',
                                   active_template='content_base.html', role=role_type, role_type=role_type,
                                   students=students, subjects=subjects)

        if not subject_id_raw.isdigit():
            flash('科目を選択してください。', 'error')
            return render_template('grades/grade_form.html', title='成績登録', mode='create',
                                   active_template='content_base.html', role=role_type, role_type=role_type,
                                   students=students, subjects=subjects)

        if not score_raw.isdigit():
            flash('点数は数字で入力してください。', 'error')
            return render_template('grades/grade_form.html', title='成績登録', mode='create',
                                   active_template='content_base.html', role=role_type, role_type=role_type,
                                   students=students, subjects=subjects)

        subject_id = int(subject_id_raw)
        score = int(score_raw)

        if not (0 <= score <= 100):
            flash('点数は0〜100で入力してください。', 'error')
            return render_template('grades/grade_form.html', title='成績登録', mode='create',
                                   active_template='content_base.html', role=role_type, role_type=role_type,
                                   students=students, subjects=subjects)

        # 履修チェック
        is_enrolled = Enrollment.select().where(
            (Enrollment.student_id == student_number) &
            (Enrollment.subject == subject_id)
        ).exists()
        if not is_enrolled:
            flash('この学生は選択した科目を履修していません。', 'error')
            return render_template('grades/grade_form.html', title='成績登録', mode='create',
                                   active_template='content_base.html', role=role_type, role_type=role_type,
                                   students=students, subjects=subjects)

        # 単位は科目マスタから確定
        try:
            sub = Subject.get_by_id(subject_id)
        except DoesNotExist:
            flash('選択した科目が存在しません。', 'error')
            return render_template('grades/grade_form.html', title='成績登録', mode='create',
                                   active_template='content_base.html', role=role_type, role_type=role_type,
                                   students=students, subjects=subjects)

        unit = int(sub.credits)

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

    return render_template('grades/grade_form.html', title='成績登録', mode='create',
                           active_template='content_base.html', role=role_type, role_type=role_type,
                           students=students, subjects=subjects)


@grade_bp.route('/<role_type>/edit/<student_number>/<int:subject_id>', methods=['GET', 'POST'])
@login_required
@require_roles(*_EDIT_ROLES)
def edit(role_type, student_number, subject_id):
    try:
        grade = Grade.get((Grade.student_id == student_number) & (Grade.subject_id == subject_id))
    except DoesNotExist:
        flash('対象の成績が見つかりませんでした。', 'error')
        return redirect(url_for('grade.grade_list'))

    if request.method == 'POST':
        unit_raw = (request.form.get('unit') or '').strip()
        score_raw = (request.form.get('score') or '').strip()

        if not (unit_raw.isdigit() and score_raw.isdigit()):
            flash('単位 / 点数 は数字で入力してください。', 'error')
            return render_template('grades/grade_form.html', title='成績編集', mode='edit',
                                   grade=grade, active_template='content_base.html',
                                   role=role_type, role_type=role_type)

        unit = int(unit_raw)
        score = int(score_raw)

        if unit < 0:
            flash('単位は0以上で入力してください。', 'error')
            return render_template('grades/grade_form.html', title='成績編集', mode='edit',
                                   grade=grade, active_template='content_base.html',
                                   role=role_type, role_type=role_type)

        if not (0 <= score <= 100):
            flash('点数は0〜100で入力してください。', 'error')
            return render_template('grades/grade_form.html', title='成績編集', mode='edit',
                                   grade=grade, active_template='content_base.html',
                                   role=role_type, role_type=role_type)

        grade.unit = unit
        grade.score = score
        grade.save()

        flash('成績を更新しました。', 'success')
        return redirect(url_for('grade.grade_list'))

    return render_template('grades/grade_form.html', title='成績編集', mode='edit',
                           grade=grade, active_template='content_base.html',
                           role=role_type, role_type=role_type)


@grade_bp.route('/<role_type>/delete/<student_number>/<int:subject_id>')
@login_required
@require_roles(*_EDIT_ROLES)
def delete(role_type, student_number, subject_id):
    try:
        grade = Grade.get((Grade.student_id == student_number) & (Grade.subject_id == subject_id))
        grade.delete_instance()
        flash('成績を削除しました。', 'success')
    except DoesNotExist:
        flash('対象の成績が見つかりませんでした。', 'error')

    return redirect(url_for('grade.grade_list'))
