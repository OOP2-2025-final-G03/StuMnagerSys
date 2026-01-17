from flask import Blueprint, render_template, request, redirect, url_for, flash, abort, g, jsonify
from flask_login import login_required, current_user
from peewee import DoesNotExist

from utils import role_required
from models import Grade, Subject, Student, User, Enrollment  # ★Enrollmentを追加


# /grade/... に統一
grade_bp = Blueprint('grade', __name__, url_prefix='/grade')

# -----------------------------
# 成績一覧（/grade/list）
# -----------------------------

@grade_bp.route('/list')
@login_required
def grade_list():
    """
    - student: 自分の成績だけ表示（student_number の検索は無視）
    - teacher/admin: 学籍番号・科目で検索できる
    """

    # 「生徒画面かどうか」は URL ではなくログインユーザーで判定
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

    # 合格/不合格フィルタ
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
                Student
                .select(Student, User)
                .join(User)
                .where(User.user_id.in_(student_ids))
            )
            student_name_map = {st.student_id.user_id: st.name for st in rows}

    return render_template(
        'grades/grade_list.html',
        title='成績一覧',
        items=grade_items,
        active_page='grades',
        subject_map=subject_map,
        student_name_map=student_name_map,
        is_student_view=is_student_view,
    )


# -----------------------------
# ★履修科目取得（AJAX用）
#   /grade/enrolled_subjects/<student_number>
# -----------------------------

@grade_bp.route('/enrolled_subjects/<student_number>')
@role_required('admin', 'teacher')
@login_required
def enrolled_subjects(student_number):
    rows = (
        Enrollment
        .select(Enrollment, Subject)
        .join(Subject)
        .where(Enrollment.student_id == student_number)
        .order_by(Subject.id.asc())
    )

    data = []
    for e in rows:
        data.append({
            "id": e.subject.id,
            "name": e.subject.name,
            "credits": e.subject.credits,
        })

    return jsonify(data)


# -----------------------------
# 成績作成（/grade/create）
# -----------------------------

@grade_bp.route('/create', methods=['GET', 'POST'])
@role_required('admin', 'teacher')
@login_required
def create():
    # 生徒一覧（Student + User）
    student_rows = (
        Student
        .select(Student, User)
        .join(User)
        .where(User.role == 'student')
        .order_by(User.user_id.asc())
    )
    students = [{"student_id": st.student_id.user_id, "name": st.name} for st in student_rows]

    # ★科目は「学籍番号選択後にAJAXで取得」するので、初期は空でOK
    subjects = []

    if request.method == 'POST':
        student_number = (request.form.get('student_number') or '').strip()
        subject_id_raw = (request.form.get('subject_id') or '').strip()
        score_raw = (request.form.get('score') or '').strip()

        if not student_number:
            flash('学籍番号を選択してください。', 'error')
            return render_template(
                'grades/grade_form.html',
                title='成績登録',
                mode='create',
                active_page='grades',
                students=students,
                subjects=subjects,
            )

        if not subject_id_raw.isdigit():
            flash('科目を選択してください。', 'error')
            return render_template(
                'grades/grade_form.html',
                title='成績登録',
                mode='create',
                active_page='grades',
                students=students,
                subjects=subjects,
            )

        if not score_raw.isdigit():
            flash('点数は数字で入力してください。', 'error')
            return render_template(
                'grades/grade_form.html',
                title='成績登録',
                mode='create',
                active_page='grades',
                students=students,
                subjects=subjects,
            )

        subject_id = int(subject_id_raw)
        score = int(score_raw)

        if not (0 <= score <= 100):
            flash('点数は0〜100で入力してください。', 'error')
            return render_template(
                'grades/grade_form.html',
                title='成績登録',
                mode='create',
                active_page='grades',
                students=students,
                subjects=subjects,
            )

        # ★この学生が本当に履修している科目かチェック（Enrollmentで検証）
        is_enrolled = Enrollment.select().where(
            (Enrollment.student_id == student_number) &
            (Enrollment.subject == subject_id)
        ).exists()
        if not is_enrolled:
            flash('この学生は選択した科目を履修していません。', 'error')
            return render_template(
                'grades/grade_form.html',
                title='成績登録',
                mode='create',
                active_page='grades',
                students=students,
                subjects=subjects,
            )

        # ★単位は科目マスタから自動確定（JSの入力は信用しない）
        try:
            sub = Subject.get_by_id(subject_id)
        except DoesNotExist:
            flash('選択した科目が存在しません。', 'error')
            return render_template(
                'grades/grade_form.html',
                title='成績登録',
                mode='create',
                active_page='grades',
                students=students,
                subjects=subjects,
            )

        unit = int(sub.credits)

        grade = Grade.select().where(
            (Grade.student_id == student_number) &
            (Grade.subject_id == subject_id)
        ).first()

        if grade:
            # アップデート
            grade.unit = unit
            grade.score = score
            grade.save()

            flash('既存の成績を更新しました。', 'success')
            return redirect(url_for('grade.grade_list'))
        else:
            # 新規作成
            Grade.create(
                student_id=student_number,
                subject_id=subject_id,
                unit=unit,
                score=score
            )
            flash('成績を登録しました。', 'success')

            return redirect(url_for('grade.grade_list'))

    return render_template(
        'grades/grade_form.html',
        title='成績登録',
        mode='create',
        active_page='grades',
        students=students,
        subjects=subjects,
    )


# -----------------------------
# 成績編集（/grade/edit/...）
# -----------------------------

@grade_bp.route('/edit/<student_number>/<int:subject_id>', methods=['GET', 'POST'])
@role_required('admin', 'teacher')
@login_required
def edit(student_number, subject_id):
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
                active_page='grades',
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
                active_page='grades',
            )

        if not (0 <= score <= 100):
            flash('点数は0〜100で入力してください。', 'error')
            return render_template(
                'grades/grade_form.html',
                title='成績編集',
                mode='edit',
                grade=grade,
                active_page='grades',
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
        active_page='grades',
    )


# -----------------------------
# 成績削除（/grade/delete/...）
# -----------------------------

@grade_bp.route('/delete/<student_number>/<int:subject_id>')
@role_required('admin', 'teacher')
@login_required
def delete(student_number, subject_id):
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
