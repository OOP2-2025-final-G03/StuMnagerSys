from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import login_required, current_user
from models import Subject, Enrollment, Student
from utils import role_required
from datetime import datetime

subject_bp = Blueprint('subject', __name__, url_prefix='/subject')

# ========================
# 科目一覧
# ========================
@subject_bp.route('/list')
@role_required('admin', 'teacher')
@login_required
def subject_list():
    query = Subject.select()
    # --- 以下、教師（admin/teacher）のみが実行される処理 ---
    category = request.args.get('category', 'all')
    keyword = request.args.get('keyword', '').strip()
    role = current_user.role

    if category in ('required', 'elective'):
        query = query.where(Subject.category == category)

    if keyword:
        query = query.where(
            (Subject.name.contains(keyword)) |
            (Subject.department.contains(keyword)) |
            (Subject.day.contains(keyword))
        )

    subjects = list(query)

    day_order = {'月': 1, '火': 2, '水': 3, '木': 4, '金': 5, '土': 6, '日': 7}
    def sort_key(sub):
        d = day_order.get(sub.day, 9)
        try:
            p = int(sub.period)
        except (ValueError, TypeError):
            p = 9
        return (d, p)

    sorted_subjects = sorted(subjects, key=sort_key)

    return render_template(
        'subject/subject_list.html',
        active_page='subjects',
        subjects=sorted_subjects,
        title='科目管理',
        active_template=f'dashboard/{role}.html',
        current_date=datetime.now().strftime('%Y年%m月%d日')
    )
    
# ========================
# 科目新規作成
# ========================
@subject_bp.route('/create', methods=['GET', 'POST'])
@role_required('admin', 'teacher')
@login_required
def create():
    # ★ガード処理：学生なら一覧へ戻す
    role_type = current_user.role
    
    if request.method == 'POST':
        # ★ HTMLの name="grades" を getlist で取得してカンマ区切りにする
        grade_list = request.form.getlist('grades')
        grade_str = ",".join(grade_list)

        name = request.form['name']
        department = request.form['department']
        category = request.form['category']
        credits = int(request.form['credits'])
        day = request.form['day']
        period = int(request.form['period'])
        Subject.create(
            name=name,
            department=department,
            category=category,
            grade=grade_str,
            credits=credits,
            day=day,
            period=period
        )
        return redirect(url_for('subject.subject_list'))

    return render_template(
        'subject/subject_form.html',
        mode='create', # 追加：HTMLでのタイトル切り替え用
        active_page='subjects',
        subject=None,
        role=role_type,
        active_template=f'dashboard/{role_type}.html',
        current_date=datetime.now().strftime('%Y年%m月%d日')
    )

# ========================
# 科目編集
# ========================
@subject_bp.route('/edit/<int:subject_id>', methods=['GET', 'POST'])
@role_required('admin', 'teacher')
@login_required
def edit(subject_id):
    # ★ガード処理：学生なら一覧へ戻す
    role_type = current_user.role
    
    subject = Subject.get_or_none(Subject.id == subject_id)

    if subject is None:
        return redirect(url_for('subject.subject_list'))

    if request.method == 'POST':
        subject.name = request.form.get('name', subject.name)
        subject.department = request.form.get('department', subject.department)
        subject.category = request.form.get('category', subject.category)
        subject.grade = request.form.get('grade', subject.grade)
        subject.credits = int(request.form.get('credits', subject.credits))
        subject.day = request.form.get('day', subject.day)
        subject.period = int(request.form.get('period', subject.period))
        subject.save()

        return redirect(url_for('subject.subject_list'))

    return render_template(
        'subject/subject_form.html',
        active_page='subjects',
        title='科目編集',
        mode='edit', # 追加
        subject=subject,
        role=role_type,
        active_template=f'dashboard/{role_type}.html',
        current_date=datetime.now().strftime('%Y年%m月%d日')
    )

@subject_bp.route('/detail/<int:subject_id>')
@role_required('admin', 'teacher', 'student')
@login_required
def detail(subject_id):
    role_type = request.args.get('role', 'student')
    subject = Subject.get_or_none(Subject.id == subject_id)
    if subject is None:
        return redirect(url_for('subject.subject_list'))
    return render_template('subjects/subject_detail.html', subject=subject, role=role_type, active_template=f'dashboard/{role_type}.html')

@subject_bp.route('/delete/<int:subject_id>')
@role_required('admin', 'teacher')
@login_required
def delete(subject_id):
    Subject.delete_by_id(subject_id)
    return redirect(url_for('subject.subject_list', current_date=datetime.now().strftime('%Y年%m月%d日')))

@subject_bp.route('/manage/<int:subject_id>')
@role_required('admin', 'teacher')
@login_required
def manage(subject_id):
    subject = Subject.get_or_none(Subject.id == subject_id)
    if subject is None:
        return redirect(url_for('subject.subject_list'))
    
    if not subject:
        return "科目が見つかりません", 404

    # 2. 現在の履修者リストの取得
    enrolled_students = Student.select().join(Enrollment, on=(Enrollment.student_id == Student.student_id)).where(Enrollment.subject_id == subject_id).dicts()

    # 3. 全学生リスト（追加用チェックボックス用）
    all_students = Student.select().dicts()
    

    return render_template(
        'enrollment/enrollment_manage.html', 
        active_page='subjects',
        subject=subject, 
        enrolled_students=enrolled_students, 
        all_students=all_students, 
        active_template=f'dashboard/{current_user.role}.html',
        current_date=datetime.now().strftime('%Y年%m月%d日')
    )
