from flask import Blueprint, render_template, request, redirect, url_for
from models import Subject
from peewee import fn

subject_bp = Blueprint('subject', __name__, url_prefix='/subject')


# ========================
# 科目一覧
# ========================
@subject_bp.route('/list')
def subject_list():
    category = request.args.get('category', 'all')
    keyword = request.args.get('keyword', '').strip()
    role_type = 'admin'

    query = Subject.select()

    # 区分フィルタ
    if category in ('required', 'elective'):
        query = query.where(Subject.category == category)

    # キーワード検索
    if keyword:
        query = query.where(
            (Subject.name.contains(keyword)) |
            (Subject.major.contains(keyword)) |
            (Subject.day.contains(keyword))
        )

    subjects = list(query)

    return render_template(
        'subject/subject_list.html',
        subjects=subjects,
        title='科目管理',
        role=role_type,
        active_template=f'dashboard/{role_type}.html'
    )


# ========================
# 科目新規作成
# ========================
@subject_bp.route('/create', methods=['GET', 'POST'])
def create():
    role_type = 'admin'

    if request.method == 'POST':
        Subject.create(
            name=request.form['name'],
            major=request.form['major'],
            category=request.form['category'],
            grade=int(request.form['grade']),
            credits=int(request.form['credits']),
            day=request.form['day'],
            period=int(request.form['period'])
        )
        return redirect(url_for('subject.subject_list'))

    return render_template(
        'subject/subject_form.html',
        title='科目新規登録',
        subject=None,
        role=role_type,
        active_template=f'dashboard/{role_type}.html'
    )


# ========================
# 科目編集
# ========================
@subject_bp.route('/edit/<int:subject_id>', methods=['GET', 'POST'])
def edit(subject_id):
    role_type = 'admin'
    subject = Subject.get_or_none(Subject.id == subject_id)

    if subject is None:
        return redirect(url_for('subject.subject_list'))

    if request.method == 'POST':
        subject.name = request.form['name']
        subject.major = request.form['major']
        subject.category = request.form['category']
        subject.grade = int(request.form['grade'])
        subject.credits = int(request.form['credits'])
        subject.day = request.form['day']
        subject.period = int(request.form['period'])
        subject.save()

        return redirect(url_for('subject.subject_list'))

    return render_template(
        'subject/subject_form.html',
        title='科目編集',
        subject=subject,
        role=role_type,
        active_template=f'dashboard/{role_type}.html'
    )


# ========================
# 科目削除
# ========================
@subject_bp.route('/delete/<int:subject_id>')
def delete(subject_id):
    Subject.delete_by_id(subject_id)
    return redirect(url_for('subject.subject_list'))
