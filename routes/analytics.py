from flask import Blueprint, jsonify, request, render_template
from flask_login import login_required, current_user
from peewee import OperationalError

from models import Grade, Subject, Student
from utils import calculate_gpa, score_to_eval


analytics_bp = Blueprint("analytic", __name__, url_prefix="/analytic")

def _load_subject_name_map() -> dict[int, str]:
    """
    subject テーブルが存在する場合だけ {subject_id: subject_name} を返す。
    無い/壊れている場合は空dictを返す（= 科目名は '科目{ID}' にfallback）。
    """
    if Subject is None:
        return {}

    try:
        # subject テーブルが無いとここで OperationalError
        rows = Subject.select(Subject.subject_id, Subject.subject_name)
        return {int(r.subject_id): str(r.subject_name) for r in rows}
    except OperationalError:
        return {}
    except Exception:
        return {}
    
def _get_chart_all() -> dict:
    """
    全体の成績データを集計して返す。
    
    Returns:
        dict: {
            0~0.5
            0.5~1
            ...
            3.5~4.0
            以上各GPA範囲の人数の分布
        }。
    """
    
    
def _get_chart_by_student() -> dict:
    """
    学生別の成績データを集計して返す。
    Returns:
        dict: {
            labels: 科目名リスト,
            scores: 評点リスト,
            message: 分析メッセージ
        }
    """

    # 学生ID取得（引数優先、なければリクエスト、なければログインユーザー）
    student_id = request.args.get("student_id")
    if not student_id:
        student_id = getattr(current_user, "user_id", None)
        if not student_id:
            return {"labels": [], "scores": [], "message": "学生IDが指定されていません。"}

        grades = Grade.select().where(Grade.student_id == student_id)
        if not grades:
            return {"labels": [], "scores": [], "message": "成績データがありません。"}

        subject_map = {s.id: s.name for s in Subject.select()}
        labels = []
        scores = []
        for g in grades:
            labels.append(subject_map.get(g.subject_id, f"科目{g.subject_id}"))
            scores.append(g.score)
        # 学生は「あなた」固定
        name = "あなた" if getattr(current_user, 'role', None) == 'student' else student_id
        message = f"{name}の成績分布"
        return {"labels": labels, "scores": scores, "message": message}

    # 成績データ取得
    grades = Grade.select().where(Grade.student_id == student_id)
    if not grades:
        return {"labels": [], "scores": [], "message": "成績データがありません。"}

    # 科目名取得用マップ
    subject_map = {s.id: s.name for s in Subject.select()}

    labels = []
    scores = []
    for g in grades:
        labels.append(subject_map.get(g.subject_id, f"科目{g.subject_id}"))
        scores.append(g.score)

    # print("labels:", labels)
    # print("scores:", scores)

    # print("student_id:", student_id)
    grades = Grade.select().where(Grade.student_id == student_id)
    # print("grades:", list(grades))

    message = f"{student_id}の成績分布"
    return {"labels": labels, "scores": scores, "message": message}
def _get_chart_by_subject() -> dict:
    """
    科目別の成績データを集計して返す。
    Returns:
        dict: {
            全科目の平均score,
            全科目ID,
            メッセージ
        }。
    """



def _get_chart_by_predict() -> dict:
    """
    予測成績データを集計して返す。
    Returns:
        dict: {
            学生ID,
            平均GPA,
            学生のGPA,
            予測GPA,
            メッセージ
        }。
    """


@analytics_bp.get("/analytic")
@login_required
def analytic():
    """
    分析データを返す。
    学生リストも渡す。
    """
    # フィルターパラメータを取得（学生ログイン時は自動的に"student"としてフィルターを適用）
    req_filter = request.args.get("filter", "all") if current_user.role != 'student' else request.args.get("filter", "student")
    student_id = request.args.get("student_id")

    # 学生リスト取得
    students = [s.to_dict() for s in Student.select()]

    if req_filter == "all":
        data = _get_chart_all()
    elif req_filter == "student":
        data = _get_chart_by_student()
    elif req_filter == "subject":
        data = _get_chart_by_subject()
    elif req_filter == "predict":
        data = _get_chart_by_predict()
    else:
        data = {}

    # 学生名をテンプレートに渡す（学生ログイン時は必ずセット）
    student_name = ""
    if hasattr(current_user, 'role') and current_user.role == 'student':
        try:
            stu = Student.get(Student.student_id == current_user.user_id)
            student_name = stu.name if stu.name else "あなた"
        except Exception:
            student_name = "あなた"
    elif isinstance(data, dict) and data.get("student_name"):
        student_name = data["student_name"]

    return render_template(
        "analytic/analytic.html",
        active_page='analytics',
        title=req_filter,
        data=data,
        students=students,
        selected_student_id=student_id,
        req_filter=req_filter,
        student_name=student_name
    )
