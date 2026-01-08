from flask import Blueprint, render_template, request, redirect, url_for
import datetime

subject_bp = Blueprint('subject', __name__, url_prefix='/subjects')

# ---- デモ用：科目データ（create/edit/delete 用） ----
SUBJECTS = [
        {'id': 'SUB001', 'name': 'プログラミング基礎', 'teacher': '11 先生', 'credits': 2, 'type': 'required', 'schedule': '月2'},
        {'id': 'SUB002', 'name': 'Web開発演習',       'teacher': '22先生', 'credits': 4, 'type': 'required', 'schedule': '火3-4'},
        {'id': 'SUB003', 'name': 'データベース論',     'teacher': '33 先生', 'credits': 2, 'type': 'elective', 'schedule': '水1'},
        {'id': 'SUB004', 'name': 'AIシステム概論',     'teacher': '44 先生', 'credits': 2, 'type': 'elective', 'schedule': '金2'},
        {'id': 'SUB005', 'name': 'ビジネス英語',       'teacher': '55 先生',   'credits': 1, 'type': 'elective', 'schedule': '木1'},
    ]

@subject_bp.route('/')
def list():
    """
    科目管理ページ
    """
    # ロールタイプを取得 
    # TODO:
    # ここでセッションや認証情報をチェックして、
    # ユーザーが正しいロールでログインしているか確認する必要があります。
    role_type = 'admin'  # 仮のロールタイプ。実際にはセッションから取得する。

    filter_type = request.args.get('type', 'all')
    
    # デモ用の静的データ
    all_subjects = [
        {'id': 'SUB001', 'name': 'プログラミング基礎', 'teacher': '11 先生', 'credits': 2, 'type': 'required', 'schedule': '月2'},
        {'id': 'SUB002', 'name': 'Web開発演習',       'teacher': '22先生', 'credits': 4, 'type': 'required', 'schedule': '火3-4'},
        {'id': 'SUB003', 'name': 'データベース論',     'teacher': '33 先生', 'credits': 2, 'type': 'elective', 'schedule': '水1'},
        {'id': 'SUB004', 'name': 'AIシステム概論',     'teacher': '44 先生', 'credits': 2, 'type': 'elective', 'schedule': '金2'},
        {'id': 'SUB005', 'name': 'ビジネス英語',       'teacher': '55 先生',   'credits': 1, 'type': 'elective', 'schedule': '木1'},
    ]

    all_subjects = SUBJECTS

    # フィルタリングロジック
    display_data = []
    if filter_type == 'required':
        display_data = [s for s in all_subjects if s['type'] == 'required']
        page_title = '科目管理 (必修のみ)'
    elif filter_type == 'elective':
        display_data = [s for s in all_subjects if s['type'] == 'elective']
        page_title = '科目管理 (選択のみ)'
    else:
        display_data = all_subjects
        page_title = '科目管理 (すべて)'

    active_template = f"dashboard/{role_type}.html"

    return render_template(
        "subjects/subject_list.html",
        active_template=active_template,
        active_page='subjects', 
        role=role_type,
        title=page_title,
        subjects=display_data,
        current_date=datetime.datetime.now().strftime('%Y年%m月%d日')
    )

@subject_bp.route('/create', methods=['GET', 'POST'])
def create():
    """
    科目新規登録
    """
    role_type = 'admin'  # 仮

    if request.method == 'POST':
        new_subject = {
            'id': f"SUB{len(SUBJECTS)+1:03}",
            'name': request.form['name'],
            'teacher': request.form['teacher'],
            'type': request.form['type'],
            'credits': int(request.form['credits']),
            'schedule': request.form['schedule']
        }
        SUBJECTS.append(new_subject)
        return redirect(url_for('subject.list'))

    return render_template(
        'subjects/subject_form.html',
        title='科目新規登録',
        role=role_type,
        active_template=f'dashboard/{role_type}.html'
    )

@subject_bp.route('/edit/<subject_id>', methods=['GET', 'POST'])
def edit(subject_id):
    """
    科目編集
    """
    role_type = 'admin'
    subject = next((s for s in SUBJECTS if s['id'] == subject_id), None)

    if subject is None:
        return redirect(url_for('subject.list'))

    if request.method == 'POST':
        subject['name'] = request.form['name']
        subject['teacher'] = request.form['teacher']
        subject['type'] = request.form['type']
        subject['credits'] = int(request.form['credits'])
        subject['schedule'] = request.form['schedule']
        return redirect(url_for('subject.list'))

    return render_template(
        'subjects/subject_form.html',
        title='科目編集',
        subject=subject,
        role=role_type,
        active_template=f'dashboard/{role_type}.html'
    )

@subject_bp.route('/delete/<subject_id>')
def delete(subject_id):
    """
    科目削除
    """
    global SUBJECTS
    SUBJECTS = [s for s in SUBJECTS if s['id'] != subject_id]
    return redirect(url_for('subject.list'))

