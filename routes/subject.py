from flask import Blueprint, render_template, request, redirect, url_for
from utils.db import get_db_connection

subject_bp = Blueprint('subject', __name__, url_prefix='/subject')

@subject_bp.route('/list')
def list():
    category = request.args.get('category', 'all')
    keyword = request.args.get('keyword', '').strip()
    role_type = 'admin'

    conn = get_db_connection()
    cur = conn.cursor()

    sql = "SELECT * FROM subjects WHERE 1=1"
    params = []

    # 区分フィルタ
    if category in ('required', 'elective'):
        sql += " AND category = ?"
        params.append(category)

    # キーワード検索
    if keyword:
        sql += " AND (name LIKE ? OR major LIKE ? OR day LIKE ?)"
        like = f"%{keyword}%"
        params.extend([like, like, like])

    cur.execute(sql, params)
    subjects = cur.fetchall()
    conn.close()

    return render_template(
        'subject/subject_list.html',
        subjects=subjects,
        title='科目管理',
        role=role_type,
        active_template=f'dashboard/{role_type}.html'
    )




@subject_bp.route('/create', methods=['GET', 'POST'])
def create():
    role_type = 'admin'

    if request.method == 'POST':
        name = request.form['name']
        major = request.form['major']
        category = request.form['category']
        grade = int(request.form['grade'])
        credits = int(request.form['credits'])
        day = request.form['day']
        period = int(request.form['period'])

        conn = get_db_connection()
        conn.execute(
            """
            INSERT INTO subjects
            (name, major, category, grade, credits, day, period)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (name, major, category, grade, credits, day, period)
        )
        conn.commit()
        conn.close()

        return redirect(url_for('subject.list'))

    return render_template(
        'subject/subject_form.html',
        title='科目新規登録',
        subject=None,
        role=role_type,
        active_template=f'dashboard/{role_type}.html'
    )




@subject_bp.route('/edit/<int:subject_id>', methods=['GET', 'POST'])
def edit(subject_id):
    role_type = 'admin'
    conn = get_db_connection()
    cur = conn.cursor()

    if request.method == 'POST':
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
                int(request.form['grade']),
                int(request.form['credits']),
                request.form['day'],
                int(request.form['period']),
                subject_id
            )
        )
        conn.commit()
        conn.close()
        return redirect(url_for('subject.list'))

    cur.execute("SELECT * FROM subjects WHERE id=?", (subject_id,))
    subject = cur.fetchone()
    conn.close()

    return render_template(
        'subject/subject_form.html',
        title='科目編集',
        subject=subject,
        role=role_type,
        active_template=f'dashboard/{role_type}.html'
    )




@subject_bp.route('/delete/<subject_id>')
def delete(subject_id):
    conn = get_db_connection()
    conn.execute("DELETE FROM subjects WHERE id=?", (subject_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('subject.list'))