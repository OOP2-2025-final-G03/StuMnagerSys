from flask import Blueprint, jsonify, request, render_template
from flask_login import login_required, current_user
from collections import defaultdict
from peewee import OperationalError, fn

from models import Grade, Subject, Student
from utils import calculate_gpa, score_to_eval


analytics_bp = Blueprint("analytic", __name__, url_prefix="/analytic")


def _load_subject_name_map() -> dict[int, str]:
    """
    subject テーブルが存在する場合だけ {subject_id: subject_name} を返す。
    無い/壊れている場合は空dictを返す（= 科目名は '科目{ID}' にfallback）。
    """
    try:
        rows = Subject.select(Subject.id, Subject.name)
        return {int(r.id): str(r.name) for r in rows}
    except (OperationalError, Exception):
        return {}


def _get_chart_all() -> dict:
    """
    全体の成績データを集計して返す。
    Returns:
        dict: {
            labels: GPA範囲のラベルリスト,
            data: 各GPA範囲の学生数,
            message: 分析メッセージ
        }。
    """
    students = Student.select()
    if not students:
        return {"labels": [], "data": [], "message": "学生データがありません。"}

    gpa_buckets = {
        "0.0~0.5": 0,
        "0.5~1.0": 0,
        "1.0~1.5": 0,
        "1.5~2.0": 0,
        "2.0~2.5": 0,
        "2.5~3.0": 0,
        "3.0~3.5": 0,
        "3.5~4.0": 0
    }

    total_gpa = 0.0
    valid_student_count = 0

    for student in students:
        gpa = calculate_gpa(student.student_id.user_id)
        if gpa > 0:
            total_gpa += gpa
            valid_student_count += 1

            if gpa < 0.5:
                gpa_buckets["0.0~0.5"] += 1
            elif gpa < 1.0:
                gpa_buckets["0.5~1.0"] += 1
            elif gpa < 1.5:
                gpa_buckets["1.0~1.5"] += 1
            elif gpa < 2.0:
                gpa_buckets["1.5~2.0"] += 1
            elif gpa < 2.5:
                gpa_buckets["2.0~2.5"] += 1
            elif gpa < 3.0:
                gpa_buckets["2.5~3.0"] += 1
            elif gpa < 3.5:
                gpa_buckets["3.0~3.5"] += 1
            else:
                gpa_buckets["3.5~4.0"] += 1

    labels = list(gpa_buckets.keys())
    scores = list(gpa_buckets.values())

    avg_gpa = round(total_gpa / valid_student_count, 2) if valid_student_count > 0 else 0.0
    message = f"全体の平均GPA: {avg_gpa} | 集計対象学生: {valid_student_count}名"

    return {"labels": labels, "data": scores, "message": message}


def _get_chart_by_student() -> dict:
    """
    学生別の成績データを集計して返す。
    Returns:
        dict: {
            labels: 科目名リスト,
            data: 評点リスト,
            message: 分析メッセージ
        }
    """
    student_id = request.args.get("student_id")
    if not student_id:
        student_id = getattr(current_user, "user_id", None)
        if not student_id:
            return {"labels": [], "data": [], "message": "学生IDが指定されていません。"}

        grades = Grade.select().where(Grade.student_id == student_id)
        if not grades:
            return {"labels": [], "data": [], "message": "成績データがありません。"}

        subject_map = _load_subject_name_map()
        labels = []
        scores = []
        for g in grades:
            labels.append(subject_map.get(g.subject_id, f"科目{g.subject_id}"))
            scores.append(g.score)

        message = None
        return {"labels": labels, "data": scores, "message": message}

    grades = Grade.select().where(Grade.student_id == student_id)
    if not grades:
        return {"labels": [], "data": [], "message": "成績データがありません。"}

    subject_map = _load_subject_name_map()

    labels = []
    scores = []
    for g in grades:
        labels.append(subject_map.get(g.subject_id, f"科目{g.subject_id}"))
        scores.append(g.score)

    message = None
    return {"labels": labels, "data": scores, "message": message}


def _get_chart_by_subject() -> dict:
    """
    科目別の成績データを集計して返す。
    Returns:
        dict: {
            "labels": 科目名リスト,
            "data": 全科目の平均評点,
            "message": メッセージ
        }。
    """
    subject_map = _load_subject_name_map()

    query = (Grade
             .select(Grade.subject_id, fn.AVG(Grade.score).alias('avg_score'))
             .group_by(Grade.subject_id))

    avg_map = {subject_map.get(q.subject_id, f"科目{q.subject_id}"): round(float(q.avg_score), 1) for q in query}

    message = "成績データがありません。"
    if avg_map:
        max_sub = max(avg_map, key=avg_map.get)
        min_sub = min(avg_map, key=avg_map.get)
        message = f"全体では{min_sub}が平均的に低く({avg_map[min_sub]}点)、{max_sub}が高い傾向にあります({avg_map[max_sub]}点)。"
        message += f"   - 全体の平均点は{sum(avg_map.values()) / len(avg_map):.1f}点です。"

    return {"labels": list(avg_map.keys()),
            "data": list(avg_map.values()),
            "message": message
            }


def _get_chart_by_predict() -> dict:
    """
    予測GPAを計算して「全体平均 / 現在のGPA / 予測」を返す。
    予測GPA = 現在のGPA + (現在のGPA - (4 * (やる気値/100)))
    """
    # 対象学生ID（指定がなければログインユーザー）
    student_id = request.args.get("student_id")
    if not student_id:
        student_id = getattr(current_user, "user_id", None)
    if not student_id:
        return {"labels": [], "data": [], "message": "学生IDが指定されていません。"}

    # 現在GPA
    try:
        current_gpa = float(calculate_gpa(student_id) or 0.0)
    except Exception:
        current_gpa = 0.0

    # 全体平均GPA
    total_gpa = 0.0
    valid_student_count = 0
    for stu in Student.select():
        try:
            gpa = float(calculate_gpa(stu.student_id.user_id) or 0.0)
        except Exception:
            gpa = 0.0
        if gpa > 0:
            total_gpa += gpa
            valid_student_count += 1
    avg_gpa = round(total_gpa / valid_student_count, 2) if valid_student_count > 0 else 0.0

    # やる気値（motivationsテーブルから。無ければ50）
    motivation = 50
    try:
        db = Grade._meta.database
        cur = db.execute_sql(
            "SELECT value FROM motivations WHERE student_id = ? LIMIT 1",
            (student_id,)
        )
        row = cur.fetchone()
        if row and row[0] is not None:
            motivation = int(row[0])
    except Exception:
        motivation = 50

    # 予測GPA（指定式）
    predicted = current_gpa + (avg_gpa * (motivation / 100.0))
    predicted = max(0.0, min(4.0, predicted))

    current_gpa_r = round(current_gpa, 2)
    predicted_r = round(predicted, 2)

    if current_gpa_r <= 0:
        message = "成績データがないため、GPA予測ができません。"
    elif predicted_r > current_gpa_r:
        message = f"やる気値{motivation}に基づく予測では、GPAが上がる可能性があります。"
    elif predicted_r < current_gpa_r:
        message = f"やる気値{motivation}に基づく予測では、GPAが下がる可能性があります。"
    else:
        message = f"やる気値{motivation}に基づく予測では、GPAはほぼ変わらない見込みです。"

    return {
        "labels": ["全体平均", "現在のGPA", "予測"],
        "data": [avg_gpa, current_gpa_r, predicted_r],
        "message": message
    }


@analytics_bp.get("/")
@login_required
def analytic():
    """
    分析データを返す。学生リストも渡す。
    """
    req_filter = request.args.get("filter", "all") if current_user.role != 'student' else request.args.get("filter", "student")
    student_id = request.args.get("student_id")

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
        req_filter=req_filter,
        analysis_message=data.get("message"),
        data=data,
        students=students,
        selected_student_id=student_id,
        student_name=student_name
    )
