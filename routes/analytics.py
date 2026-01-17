from flask import Blueprint, jsonify, request, render_template
from flask_login import login_required
from collections import defaultdict
from peewee import OperationalError

from models import Grade, Subject
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
            学生ID,
            各科目のscore,
            メッセージ
            
        }。
    """
    
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
    """
    req_filter = request.args.get("filter", "all")
    
    if req_filter == "all":
        data = _get_chart_all()
    elif req_filter == "student":
        data = _get_chart_by_student()
    elif req_filter == "subject":
        data = _get_chart_by_subject()
    elif req_filter == "predict":
        data = _get_chart_by_predict()
    
    return render_template(
        "analytic/analytic.html",
        active_page='analytics',
        title=req_filter,
        data=data,
    )
