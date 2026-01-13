from flask import Blueprint, request, render_template, redirect, url_for
from utils.db import get_db_connection

enrollment_bp = Blueprint('enrollment', __name__, url_prefix='/enrollments')

def is_not_admin():
    """管理権限がないかチェックする共通処理"""
    role = request.args.get('role', 'student')
    return role == 'student'

@enrollment_bp.route('/')
def index():
    # 学生用のマイページ（履修一覧）機能のみ残す
    role_type = request.args.get('role', 'student')
    if role_type != 'student':
        # 教師がアクセスした場合は科目一覧へ戻す
        return redirect(url_for('subject.list', role=role_type))

    student_id = "K24000"
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT s.* FROM subjects s
        JOIN enrollments e ON s.id = e.subject_id
        WHERE e.student_id = ?
    """, (student_id,))
    subjects = cur.fetchall()
    day_order = {'月': 1, '火': 2, '水': 3, '木': 4, '金': 5, '土': 6, '日': 7}
    sorted_subjects = sorted(subjects, key=lambda x: (day_order.get(x['day'], 9), x['period']))
    conn.close()

    return render_template(
        'enrollments/enrollment_list.html', 
        subjects=sorted_subjects, 
        role=role_type,
        active_template=f'dashboard/{role_type}.html'
    )

@enrollment_bp.route('/create', methods=['POST'])
def create():
    # ★ガード処理：学生なら一覧へ戻す
    if is_not_admin():
        return redirect(url_for('subject.list', role='student'))
    student_id_list = request.form.getlist('student_ids')
    subject_id = request.form.get('subject_id')
    role = request.form.get('role', 'teacher')

    conn = get_db_connection()
    cur = conn.cursor()

    # バリデーション：科目の対象学年と専攻を取得
    cur.execute("SELECT grade, major FROM subjects WHERE id = ?", (subject_id,))
    sub_data = cur.fetchone()

    try:
        for student_id in student_id_list:
            cur.execute("SELECT 学年, 専攻 FROM students WHERE 学籍番号 = ?", (student_id,))
            student = cur.fetchone()

            if student and sub_data:
                # ★修正：複数学年対応（文字列の中に学生の学年が含まれているか）
                # sub_data['grade'] が "1,2" のような文字列であることを想定
                target_grades = str(sub_data['grade']).split(',')
                grade_match = str(student['学年']) in target_grades
                
                major_match = (sub_data['major'] == '全専攻' or student['専攻'] == sub_data['major'])
                if grade_match and major_match:
                    # 既に登録されているか最終確認
                    cur.execute("SELECT 1 FROM enrollments WHERE student_id = ? AND subject_id = ?", (student_id, subject_id))
                    if not cur.fetchone():
                        conn.execute(
                            "INSERT INTO enrollments (student_id, subject_id) VALUES (?, ?)",
                            (student_id, subject_id)
                        )
        conn.commit()
    except Exception as e:
        print(f"Error during enrollment: {e}")
    finally:
        conn.close()
    return redirect(url_for('subject.manage', role=role, subject_id=subject_id))

@enrollment_bp.route('/delete_bulk_by_id', methods=['POST'])
def delete_bulk_by_id():
    # ★ガード処理：学生なら一覧へ戻す
    if is_not_admin():
        return redirect(url_for('subject.list', role='student'))
    student_ids = request.form.getlist('student_ids')
    subject_id = request.form.get('subject_id')
    role = request.form.get('role', 'teacher')

    if student_ids:
        conn = get_db_connection()
        placeholders = ', '.join(['?'] * len(student_ids))
        sql = f"DELETE FROM enrollments WHERE subject_id = ? AND student_id IN ({placeholders})"
        conn.execute(sql, [subject_id] + student_ids)
        conn.commit()
        conn.close()
    
    return redirect(url_for('subject.manage', role=role, subject_id=subject_id))
