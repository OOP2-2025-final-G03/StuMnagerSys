from flask import Blueprint, render_template, request, redirect, url_for
from models import Subject, Enrollment, Student
from peewee import fn

subject_bp = Blueprint('subject', __name__, url_prefix='/subject')

def is_not_admin():
    """管理権限がないかチェックする共通処理"""
    role = request.args.get('role', 'student')
    return role == 'student'


# ========================
# 科目一覧
# ========================
@subject_bp.route('/list')
def subject_list():
    query = Subject.select()
    # --- 以下、教師（admin/teacher）のみが実行される処理 ---
    category = request.args.get('category', 'all')
    keyword = request.args.get('keyword', '').strip()
    role_type = request.args.get('role', 'teacher')

    params = []

    if category in ('required', 'elective'):
        query = query.where(Subject.category == category)

    if keyword:
        query = query.where(
            (Subject.name.contains(keyword)) |
            (Subject.major.contains(keyword)) |
            (Subject.day.contains(keyword))
        )

    subjects = list(query)

    day_order = {'月': 1, '火': 2, '水': 3, '木': 4, '金': 5, '土': 6, '日': 7}
    def sort_key(sub):
        d = day_order.get(sub['day'], 9)
        try:
            p = int(sub['period'])
        except (ValueError, TypeError):
            p = 9
        return (d, p)

    sorted_subjects = sorted(subjects, key=sort_key)

    return render_template(
        'subject/subject_list.html',
        active_page='subjects',
        subjects=sorted_subjects,
        title='科目管理',
        role=role_type,
        active_template=f'dashboard/{role_type}.html'
    )
    
# ========================
# 科目新規作成
# ========================
@subject_bp.route('/create', methods=['GET', 'POST'])
def create():
    # ★ガード処理：学生なら一覧へ戻す
    if is_not_admin():
        return redirect(url_for('subject.list', role='student'))

    role_type = 'admin','teacher'
    
    if request.method == 'POST':
        # ★ HTMLの name="grades" を getlist で取得してカンマ区切りにする
        grade_list = request.form.getlist('grades')
        grade_str = ",".join(grade_list)

        name = request.form['name']
        major = request.form['major']
        category = request.form['category']
        credits = int(request.form['credits'])
        day = request.form['day']
        period = int(request.form['period'])
        Subject.create(
            name=name,
            major=major,
            category=category,
            grade=grade_str,
            credits=credits,
            day=day,
            period=period
        )
        return redirect(url_for('subject.subject_list'))

    return render_template(
        'subjects/subject_form.html',
        mode='create', # 追加：HTMLでのタイトル切り替え用
        active_page='subjects',
        subject=None,
        role=role_type,
        active_template=f'dashboard/{role_type}.html'
    )

# ========================
# 科目編集
# ========================
@subject_bp.route('/edit/<int:subject_id>', methods=['GET', 'POST'])
def edit(subject_id):
    if is_not_admin():
        return redirect(url_for('subject.list', role='student'))
    role_type = 'admin','teacher'
    
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
        active_page='subjects',
        title='科目編集',
        mode='edit', # 追加
        subject=subject,
        role=role_type,
        active_template=f'dashboard/{role_type}.html'
    )

@subject_bp.route('/detail/<int:subject_id>')
def detail(subject_id):
    role_type = request.args.get('role', 'student')
    subject = Subject.get_or_none(Subject.id == subject_id)
    if subject is None:
        return redirect(url_for('subject.subject_list'))
    return render_template('subjects/subject_detail.html', subject=subject, role=role_type, active_template=f'dashboard/{role_type}.html')

@subject_bp.route('/delete/<int:subject_id>')
def delete(subject_id):
    Subject.delete_by_id(subject_id)
    return redirect(url_for('subject.subject_list'))

@subject_bp.route('/manage/<int:subject_id>')
def manage(subject_id):
    # ★ガード処理：学生なら一覧へ戻す
    if is_not_admin():
        return redirect(url_for('subject.list', role='student'))
    # 管理画面なので role は teacher か admin を想定
    role_type = request.args.get('role', 'teacher')
    
    subject = Subject.get_or_none(Subject.id == subject_id)
    if subject is None:
        return redirect(url_for('subject.subject_list'))
    
    if not subject:
        return "科目が見つかりません", 404

    # 2. 現在の履修者リストの取得
    enrolled_students = Enrollment.select().join(Student).where(Enrollment.subject_id == subject_id).dicts()

    # 3. 全学生リスト（追加用チェックボックス用）
    all_students = Student.select().dicts()
    

    return render_template(
        'enrollments/enrollment_manage.html', 
        active_page='subjects',
        subject=subject, 
        enrolled_students=enrolled_students, 
        all_students=all_students, 
        role=role_type,
        active_template=f'dashboard/{role_type}.html'
    )
