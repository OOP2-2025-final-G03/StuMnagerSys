from flask import Blueprint, render_template, request, redirect, url_for
from utils.db import get_db_connection

subject_bp = Blueprint('subject', __name__, url_prefix='/subjects')

def is_not_admin():
    """管理権限がないかチェックする共通処理"""
    role = request.args.get('role', 'student')
    return role == 'student'

@subject_bp.route('/')
def list():
    # --- 以下、教師（admin/teacher）のみが実行される処理 ---
    category = request.args.get('category', 'all')
    keyword = request.args.get('keyword', '').strip()
    role_type = request.args.get('role', 'teacher')
    
    conn = get_db_connection()
    cur = conn.cursor()
    sql = "SELECT * FROM subjects WHERE 1=1"
    params = []

    if category in ('required', 'elective'):
        sql += " AND category = ?"
        params.append(category)

    if keyword:
        sql += " AND (name LIKE ? OR major LIKE ? OR day LIKE ?)"
        like = f"%{keyword}%"
        params.extend([like, like, like])

    cur.execute(sql, params)
    subjects = cur.fetchall()
    conn.close()

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
        'subjects/subject_list.html',
        subjects=sorted_subjects,
        title='科目管理',
        role=role_type,
        active_template=f'dashboard/{role_type}.html'
    )

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

        conn = get_db_connection()
        conn.execute(
            """
            INSERT INTO subjects (name, major, category, grade, credits, day, period)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (name, major, category, grade_str, credits, day, period)
        )
        conn.commit()
        conn.close()
        return redirect(url_for('subject.list'))

    return render_template(
        'subjects/subject_form.html',
        mode='create', # 追加：HTMLでのタイトル切り替え用
        subject=None,
        role=role_type,
        active_template=f'dashboard/{role_type}.html'
    )

@subject_bp.route('/edit/<int:subject_id>', methods=['GET', 'POST'])
def edit(subject_id):
    # ★ガード処理：学生なら一覧へ戻す
    if is_not_admin():
        return redirect(url_for('subject.list', role='student'))
    role_type = 'admin','teacher'
    conn = get_db_connection()
    
    if request.method == 'POST':
        # ★ 編集時も同様に複数選択を処理
        grade_list = request.form.getlist('grades')
        grade_str = ",".join(grade_list)

        conn.execute(
            """
            UPDATE subjects
            SET name=?, major=?, category=?, grade=?, credits=?, day=?, period=?
            WHERE id=?
            """,
            (
                request.form['name'],
                request.form['major'],
                request.form['category'],
                grade_str,
                int(request.form['credits']),
                request.form['day'],
                int(request.form['period']),
                subject_id
            )
        )
        conn.commit()
        conn.close()
        return redirect(url_for('subject.list'))

    cur = conn.cursor()
    cur.execute("SELECT * FROM subjects WHERE id=?", (subject_id,))
    subject = cur.fetchone()
    conn.close()

    return render_template(
        'subjects/subject_form.html',
        mode='edit', # 追加
        subject=subject,
        role=role_type,
        active_template=f'dashboard/{role_type}.html'
    )

@subject_bp.route('/detail/<int:subject_id>')
def detail(subject_id):
    role_type = request.args.get('role', 'student')
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM subjects WHERE id=?", (subject_id,))
    subject = cur.fetchone()
    conn.close()
    return render_template('subjects/subject_detail.html', subject=subject, role=role_type, active_template=f'dashboard/{role_type}.html')

@subject_bp.route('/delete/<subject_id>')
def delete(subject_id):
    conn = get_db_connection()
    conn.execute("DELETE FROM subjects WHERE id=?", (subject_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('subject.list'))

@subject_bp.route('/manage/<int:subject_id>')
def manage(subject_id):
    # ★ガード処理：学生なら一覧へ戻す
    if is_not_admin():
        return redirect(url_for('subject.list', role='student'))
    # 管理画面なので role は teacher か admin を想定
    role_type = request.args.get('role', 'teacher')
    
    conn = get_db_connection()
    cur = conn.cursor()

    # 1. 科目情報の取得
    cur.execute("SELECT * FROM subjects WHERE id = ?", (subject_id,))
    subject = cur.fetchone()
    
    if not subject:
        conn.close()
        return "科目が見つかりません", 404

    # 2. 現在の履修者リストの取得
    cur.execute("""
        SELECT e.student_id, st.名前, st.専攻, st.学年
        FROM enrollments e
        LEFT JOIN students st ON e.student_id = st.学籍番号
        WHERE e.subject_id = ?
    """, (subject_id,))
    enrolled_students = cur.fetchall()

    # 3. 全学生リスト（追加用チェックボックス用）
    cur.execute("SELECT 学籍番号, 名前, 学年, 専攻 FROM students")
    all_students = cur.fetchall()
    
    conn.close()

    return render_template(
        'enrollments/enrollment_manage.html', 
        subject=subject, 
        enrolled_students=enrolled_students, 
        all_students=all_students, 
        role=role_type,
        active_template=f'dashboard/{role_type}.html'
    )