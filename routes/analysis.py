from flask import Blueprint, render_template
from flask_login import login_required, current_user

from models import Grade, Subject

analysis_bp = Blueprint('analysis', __name__, url_prefix='/analysis')


def score_to_gpa(score: float) -> int:
    """
    0-100 の点数を GPA(0-4) に変換
    """
    if score <= 59:
        return 0
    elif score <= 69:
        return 1
    elif score <= 79:
        return 2
    elif score <= 89:
        return 3
    else:
        return 4


@analysis_bp.route('/list')
@login_required
def analysis_list():
    """
    成績分析（得意/苦手）
    - 得意科目: GPA >= 3（平均点 >= 80）
    - 苦手科目: GPA <= 2（平均点 <= 79）
    表示項目：科目名 / 単位数 / GPA
    """
    # 「自分の成績」だけを対象
    grades = list(
        Grade.select().where(Grade.student_id == current_user.get_id())
    )

    # subject_id -> {name, credits}
    subject_info = {
        s.id: {"name": s.name, "credits": s.credits}
        for s in Subject.select(Subject.id, Subject.name, Subject.credits)
    }

    # 科目ごとに平均点を算出
    stats = {}  # subject_id -> {count, sum_score}
    for g in grades:
        sid = g.subject_id
        row = stats.setdefault(sid, {"count": 0, "sum_score": 0})
        row["count"] += 1
        row["sum_score"] += g.score

    rows = []
    for subject_id, row in stats.items():
        count = row["count"]
        avg_score = (row["sum_score"] / count) if count else 0
        gpa = score_to_gpa(avg_score)

        info = subject_info.get(subject_id, {"name": "（不明）", "credits": ""})

        rows.append({
            "subject_id": subject_id,
            "subject_name": info["name"],
            "credits": info["credits"],
            "gpa": gpa,
            "avg_score": avg_score,  # 並び替え用（表示はしない）
        })

    # 得意/苦手に分類
    strong_items = [r for r in rows if r["gpa"] >= 3]
    weak_items = [r for r in rows if r["gpa"] <= 2]

    # 並び替え（得意は高い順、苦手は低い順）
    strong_items.sort(key=lambda x: (-x["gpa"], -x["avg_score"], x["subject_id"]))
    weak_items.sort(key=lambda x: (x["gpa"], x["avg_score"], x["subject_id"]))

    # 並び替えキーとして使った avg_score はテンプレに不要なので落とす
    for r in strong_items:
        r.pop("avg_score", None)
    for r in weak_items:
        r.pop("avg_score", None)

    return render_template(
        'analysis/analysis_list.html',
        title='成績分析（得意・苦手）',
        strong_items=strong_items,
        weak_items=weak_items,
        active_template=f"dashboard/{current_user.role}.html",
        active_page='analysis',
    )
