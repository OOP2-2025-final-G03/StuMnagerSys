from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import login_required, current_user

from models import Subject, Enrollment, Student
from utils import role_required
from datetime import datetime

subject_bp = Blueprint('subject', __name__, url_prefix='/subject')

@subject_bp.route('/list')
@role_required('admin', 'teacher','student')
@login_required
def subject_list():
    """
    科目一覧
    """
    query = Subject.select()
    # --- 以下、教師（admin/teacher）のみが実行される処理 ---
    category = request.args.get('category', 'all')
    keyword = request.args.get('keyword', '').strip()

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
    
    # --- ページネーション処理 ---
    offset = int(request.args.get('offset', 0))
    limit = 50
    
    # Pythonリストのスライスでページング
    paged_subjects = sorted_subjects[offset : offset + limit]
    has_more = (offset + limit) < len(sorted_subjects)

    # AJAXリクエスト（スクロール時）の場合
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return render_template(
            'subject/subject_rows.html',
            subjects=paged_subjects,
        )

    return render_template(
        'subject/subject_list.html',
        active_page='subjects',
        subjects=sorted_subjects,
        title='科目管理',
        has_more=has_more,
    )
    
@subject_bp.route('/create', methods=['GET', 'POST'])
@role_required('admin', 'teacher')
@login_required
def create():
    """
    科目新規作成
    """
    if request.method == 'POST':
        # ★ HTMLの name="grades" を getlist で取得してカンマ区切りにする
        grade_list = request.form.getlist('grade')
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
    )

@subject_bp.route('/edit/<int:subject_id>', methods=['GET', 'POST'])
@role_required('admin', 'teacher')
@login_required
def edit(subject_id):
    """
    科目編集
    """
    
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
    )

@subject_bp.route('/detail/<int:subject_id>')
@role_required('admin', 'teacher', 'student')
@login_required
def detail(subject_id):
    """
    科目詳細
    """

    subject = Subject.get_or_none(Subject.id == subject_id)
    if subject is None:
        return redirect(url_for('subject.subject_list'))
    return render_template('subjects/subject_detail.html', subject=subject)

@subject_bp.route('/delete/<int:subject_id>')
@role_required('admin', 'teacher')
@login_required
def delete(subject_id):
    """
    科目削除
    """
    Subject.delete_by_id(subject_id)
    return redirect(url_for('subject.subject_list'))

@subject_bp.route('/manage/<int:subject_id>')
@role_required('admin', 'teacher')
@login_required
def manage(subject_id):
    """
    科目履修管理
    """
    subject = Subject.get_or_none(Subject.id == subject_id)
    if subject is None:
        return redirect(url_for('subject.subject_list'))
    
    if not subject:
        return "科目が見つかりません", 404

    # 履修者リストのページネーション
    offset = int(request.args.get('offset', 0))
    limit = 50

    # 履修者のクエリ構築
    query_enrolled = (
        Student
        .select()
        .join(Enrollment, on=(Enrollment.student_id == Student.student_id))
        .where(Enrollment.subject_id == subject_id)
        .order_by(Student.student_id)
    )

    # 現在のページのデータを取得
    enrolled_students = list(query_enrolled.dicts().offset(offset).limit(limit))
    
    # 次のページがあるか判定
    has_more = len(enrolled_students) >= limit

    # AJAXリクエスト
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return render_template(
            'enrollment/enrollment_manage_rows.html',
            enrolled_students=enrolled_students
        )

    # 初回ロード時のみ全学生リストを取得
    # 注意: 全学生リストはフォーム機能のためページネーションせず全件取得します
    all_students = Student.select().dicts()

    return render_template(
        'enrollment/enrollment_manage.html', 
        active_page='subjects',
        subject=subject, 
        enrolled_students=enrolled_students, 
        all_students=all_students, 
        has_more=has_more,
    )

@subject_bp.route('/my-list')
@role_required('student')
@login_required
def my_subject_list():
    """
    履修済科目一覧 (学生専用)
    """
    
    # ログイン中のユーザーが履修登録(Enrollment)している科目のみを抽出
    query = (Subject
             .select()
             .join(Enrollment, on=(Enrollment.subject_id == Subject.id))
             .where(Enrollment.student_id == current_user.id)) 

    subjects = list(query)
    
    # ソート処理（既存のロジックと同一）
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
        active_page='my_subjects', # サイドバーの判定用
        subjects=sorted_subjects,
        title='履修済科目',
    )