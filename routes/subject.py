from flask import Blueprint, render_template, request
import datetime

subject_bp = Blueprint('subject', __name__, url_prefix='/subject')

@subject_bp.route('/list')
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
        "subject/subject_list.html",
        active_template=active_template,
        active_page='subjects', 
        role=role_type,
        title=page_title,
        subjects=display_data,
        current_date=datetime.datetime.now().strftime('%Y年%m月%d日')
    )