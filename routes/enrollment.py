from flask import Blueprint, request, render_template, redirect, url_for, current_app
from flask_login import login_required, current_user
from models import Subject, Enrollment, Student
from utils import role_required
from datetime import datetime

enrollment_bp = Blueprint('enrollments', __name__, url_prefix='/enrollments')

@enrollment_bp.route('/')
@role_required('admin', 'teacher', 'student')
@login_required
def index():
    role = current_user.role
    
    # 修正ポイント: Subjectモデルのメソッドを呼ばず、Enrollmentと結合して直接取得する
    # ログイン中の学生ID（student_id）に紐づく科目をクエリします
    student_id = current_user.profile_dict().get('student_id')
    
    query = (Subject
             .select()
             .join(Enrollment, on=(Enrollment.subject_id == Subject.id))
             .where(Enrollment.student_id == student_id))
    
    subjects = list(query)
    
    # 曜日と時限でソート
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
        'enrollment/enrollment_list.html', 
        subjects=sorted_subjects, 
        role=role,
        active_template=f'dashboard/{role}.html',
        active_page='enrollments', 
        current_date=datetime.now().strftime('%Y年%m月%d日')
    )

@enrollment_bp.route('/create', methods=['POST'])
@role_required('admin', 'teacher')
@login_required
def create():

    role = current_user.role
    if role == 'student':
        return redirect(url_for('subject.subject_list', role='student'))

    student_id_list = request.form.getlist('student_ids')
    subject_id = request.form.get('subject_id')

    subject = Subject.get_or_none(Subject.id == subject_id)
    if not subject:
        return redirect(url_for('subject.manage', role=role, subject_id=subject_id))

    try:
        target_grades = str(subject.grade).split(',')

        for sid in student_id_list:
            student = Student.get_or_none(Student.student_id == sid)
            if not student:
                print(f"学生が存在しません: {sid}")
                continue

            grade_match = str(student.grade) in target_grades
            department_match = (subject.department == '全専攻' or student.department == subject.department)

            if not (grade_match and department_match):
                print(f"学生が受講可能な年級ではありません: {sid}")
                continue

            exists = Enrollment.get_or_none(
                (Enrollment.student_id == student) &
                (Enrollment.subject_id == subject)
            )

            if exists:
                print(f"学生がすでに受講しています: {sid}")
                continue

            Enrollment.create(
                student_id=student,
                subject_id=subject
            )

    except Exception as e:
        current_app.logger.exception(e)

    return redirect(url_for(
        'subject.manage',
        role=role,
        subject_id=subject_id
    ))


@enrollment_bp.route('/delete_bulk_by_id', methods=['POST'])
@role_required('admin', 'teacher')
@login_required
def delete_bulk_by_id():
    # ★ガード処理：学生なら一覧へ戻す
    if current_user.role == 'student':
        return redirect(url_for('subject.subject_list', role='student'))
    student_ids = request.form.getlist('student_ids')
    subject_id = request.form.get('subject_id')

    if student_ids:
        (
            Enrollment
            .delete()
            .where(
                (Enrollment.subject_id == subject_id) &
                (Enrollment.student_id.in_(student_ids))
            )
            .execute()
        )
    
    return redirect(url_for('subject.manage', subject_id=subject_id, current_date=datetime.now().strftime('%Y年%m月%d日')))
