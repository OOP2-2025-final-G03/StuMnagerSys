from flask import Blueprint, render_template, request, redirect, url_for
from utils.db import get_db_connection

subject_bp = Blueprint('subject', __name__, url_prefix='/subjects')

def is_not_admin():
    """管理権限がないかチェック（URL引数とフォーム両方を確認）"""
    # URLの ?role= か、フォームの <input name="role"> から取得
    role = request.args.get('role') or request.form.get('role')
    return role not in ['teacher', 'admin']

def get_current_role():
    """URLパラメータまたはフォームデータから現在のロールを特定する"""
    # POST時はformから、GET時はargsから取得
    role = request.form.get('role') or request.args.get('role', 'student')
    return role

@subject_bp.route('/')
def list():
    role_type = get_current_role()
    # 管理権限がない場合は学生画面へ飛ばす
    if role_type not in ['teacher', 'admin']:
        return redirect(url_for('enrollment.index', role='student'))

    category = request.args.get('category', 'all')
    keyword = request.args.get('keyword', '').strip()
    
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
    sorted_subjects = sorted(subjects, key=lambda x: (day_order.get(x['day'], 9), x['period']))

    return render_template(
        'subjects/subject_list.html',
        subjects=sorted_subjects,
        role=role_type,
        active_template=f'dashboard/{role_type}.html'
    )

@subject_bp.route('/create', methods=['GET', 'POST'])
def create():
    if is_not_admin():
        return redirect(url_for('enrollment.index', role='student'))

    role_type = request.args.get('role', 'teacher')
    if request.method == 'POST':
        # ★ POST時はフォームからroleを再取得
        role_type = request.form.get('role', role_type)
        grade_str = request.form.get('grades')
        
        conn = get_db_connection()
        conn.execute(
            "INSERT INTO subjects (name, major, category, grade, credits, day, period) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (request.form['name'], request.form['major'], request.form['category'], 
             grade_str, int(request.form['credits']), request.form['day'], int(request.form['period']))
        )
        conn.commit()
        conn.close()
        return redirect(url_for('subject.list', role=role_type))

    return render_template('subjects/subject_form.html', mode='create', subject=None, role=role_type, active_template=f'dashboard/{role_type}.html')

@subject_bp.route('/edit/<int:subject_id>', methods=['GET', 'POST'])
def edit(subject_id):
    role_type = get_current_role()
    if role_type not in ['teacher', 'admin']:
        return redirect(url_for('enrollment.index', role='student'))
    
    conn = get_db_connection()
    if request.method == 'POST':
        grade_str = request.form.get('grades')
        conn.execute(
            "UPDATE subjects SET name=?, major=?, category=?, grade=?, credits=?, day=?, period=? WHERE id=?",
            (request.form['name'], request.form['major'], request.form['category'], 
             grade_str, int(request.form['credits']), request.form['day'], int(request.form['period']), subject_id)
        )
        conn.commit()
        conn.close()
        return redirect(url_for('subject.list', role=role_type))

    cur = conn.cursor()
    cur.execute("SELECT * FROM subjects WHERE id=?", (subject_id,))
    subject = cur.fetchone()
    conn.close()

    return render_template(
        'subjects/subject_form.html', mode='edit', subject=subject, role=role_type,
        active_template=f'dashboard/{role_type}.html'
    )

@subject_bp.route('/delete/<subject_id>')
def delete(subject_id):
    role_type = get_current_role()
    if role_type not in ['teacher', 'admin']:
        return redirect(url_for('enrollment.index', role='student'))
        
    conn = get_db_connection()
    conn.execute("DELETE FROM subjects WHERE id=?", (subject_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('subject.list', role=role_type))

@subject_bp.route('/manage/<int:subject_id>')
def manage(subject_id):
    role_type = get_current_role()
    if role_type not in ['teacher', 'admin']:
        return redirect(url_for('enrollment.index', role='student'))
    
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM subjects WHERE id = ?", (subject_id,))
    subject = cur.fetchone()

    cur.execute("""
        SELECT e.student_id, st.名前, st.専攻, st.学年 FROM enrollments e
        LEFT JOIN students st ON e.student_id = st.学籍番号 WHERE e.subject_id = ?
    """, (subject_id,))
    enrolled_students = cur.fetchall()

    cur.execute("SELECT 学籍番号, 名前, 学年, 専攻 FROM students")
    all_students = cur.fetchall()
    conn.close()

    return render_template(
        'enrollments/enrollment_manage.html', 
        subject=subject, enrolled_students=enrolled_students, 
        all_students=all_students, role=role_type,
        active_template=f'dashboard/{role_type}.html'
    )