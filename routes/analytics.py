from flask import Blueprint, jsonify, request, render_template
from flask_login import login_required, current_user
from collections import defaultdict
from peewee import OperationalError, fn

from models import Grade, Subject, Student
from utils import calculate_gpa


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
            0~0.5
            0.5~1
            ...
            3.5~4.0
            以上各GPA範囲の人数の分布
        }。
    """
    # 全学生のIDを取得
    all_students = Student.select()
    
    # GPAの範囲ごとの人数を初期化
    # 0.0~0.5, 0.5~1.0, ..., 3.5~4.0
    bins = [0.0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0]
    labels = [f"{b}~{round(b+0.5, 1)}" for b in bins[:-1]]
    counts = [0] * len(labels)
    
    for s in all_students:
        sid = s.student_id.user_id if hasattr(s.student_id, 'user_id') else s.student_id
        gpa = calculate_gpa(sid)
        for i in range(len(bins)-1):
            if bins[i] <= gpa < bins[i+1] or (i == len(bins)-2 and gpa == 4.0):
                counts[i] += 1
                break
                
    return {
        "labels": labels,
        "data": counts,
        "message": "全学生のGPA分布を表示しています。"
    }
    
    
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
    subject_map = _load_subject_name_map()
    uid = current_user.get_id()
    
    # 学生が自分自身を見る場合を想定
    grades = Grade.select().where(Grade.student_id == uid)
    
    data_map = {subject_map.get(g.subject_id, f"科目{g.subject_id}"): g.score for g in grades}
    
    # メッセージの生成（最高・最低評価の抽出）
    message = "データがありません。"
    if data_map:
        max_sub = max(data_map, key=data_map.get)
        min_sub = min(data_map, key=data_map.get)
        message = f"あなたは{min_sub}が苦手、{max_sub}が得意です。"

    return {
        "labels": list(data_map.keys()),
        "data": list(data_map.values()),
        "message": message
    }
    
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
    subject_map = _load_subject_name_map()
    
    # 教師権限等を想定し、科目ごとの全体平均を計算
    query = (Grade
             .select(Grade.subject_id, fn.AVG(Grade.score).alias('avg_score'))
             .group_by(Grade.subject_id))
    
    avg_map = {subject_map.get(q.subject_id, f"科目{q.subject_id}"): round(float(q.avg_score), 1) for q in query}

    message = "成績データがありません。"
    if avg_map:
        max_sub = max(avg_map, key=avg_map.get)
        min_sub = min(avg_map, key=avg_map.get)
        message = f"全体では{min_sub}が平均的に低く、{max_sub}が高い傾向にあります。"

    return {"labels": list(avg_map.keys()), 
            "data": list(avg_map.values()), 
            "message": message
            }

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
    all_students = Student.select()
    uids = [s.student_id.user_id if hasattr(s.student_id, 'user_id') else s.student_id for s in all_students]
    # 全体平均GPAの計算
    all_gpas = [calculate_gpa(uid) for uid in uids]
    avg_total_gpa = sum(all_gpas) / len(all_gpas) if all_gpas else 0
    
    # 自分のGPA
    my_gpa = calculate_gpa(current_user.get_id())
    
    # 予測式に基づいた計算
    predicted_gpa = avg_total_gpa + (my_gpa - avg_total_gpa)
    # GPAの範囲(0~4)にクランプ
    predicted_gpa = max(0.0, min(4.0, round(predicted_gpa, 2)))

    return {
        "labels": ["全体平均", "あなたのGPA", "予測GPA"],
        "data": [round(avg_total_gpa, 2), round(my_gpa, 2), predicted_gpa],
        "message": f"現在の傾向に基づくと、次学期の予測GPAは {predicted_gpa} です。"
    }


@analytics_bp.get("/")
@login_required
def analytic():  # 関数名を analytic に戻す
    req_filter = request.args.get("filter", "all")
    
    # 学生の場合はデフォルトを 'student' に
    if current_user.role == 'student' and req_filter == 'all':
        req_filter = 'student'
    
    # フィルタに応じたデータ取得
    if req_filter == "all":
        data = _get_chart_all()
    elif req_filter == "student":
        data = _get_chart_by_student()
    elif req_filter == "subject":
        data = _get_chart_by_subject()
    elif req_filter == "predict":
        data = _get_chart_by_predict()
    else:
        data = {"labels": [], "data": [], "message": ""}
    
    return render_template(
        "analytic/analytic.html",
        active_template=f"dashboard/{current_user.role}.html",
        active_page='analytics',
        req_filter=req_filter,
        user_role=current_user.role,
        analysis_message=data.get("message"),
        data=data,
        title=f"成績分析 - {req_filter}"
    )