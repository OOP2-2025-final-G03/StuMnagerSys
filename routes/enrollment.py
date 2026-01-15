from flask import Blueprint, request, render_template, redirect, url_for, current_app
from flask_login import login_required, current_user
from models import Subject, Enrollment, Student
from utils import role_required
from datetime import datetime

enrollment_bp = Blueprint('enrollment', __name__, url_prefix='/enrollment')

@enrollment_bp.route('/')
@role_required('admin', 'teacher', 'student')
@login_required
def index():
    # 学生用のマイページ（履修一覧）機能のみ残す
    role = current_user.role
    if role == 'student':
        # 教師がアクセスした場合は科目一覧へ戻す
        return redirect(url_for('subject.subject_list', role=role))

    student_id = "K24000"
    subjects = Subject.get_enrolled_subjects(student_id)
    day_order = {'月': 1, '火': 2, '水': 3, '木': 4, '金': 5, '土': 6, '日': 7}
    sorted_subjects = sorted(subjects, key=lambda x: (day_order.get(x['day'], 9), x['period']))

    return render_template(
        'enrollment/enrollment_list.html', 
        subjects=sorted_subjects, 
        role=role,
        active_template=f'dashboard/{role}.html',
        active_page='enrollment',
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
