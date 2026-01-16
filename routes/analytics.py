from collections import defaultdict

from flask import Blueprint, jsonify, request
from flask_login import current_user, login_required
from peewee import OperationalError

from models import Grade

# Subject が無い環境でも動かしたいので import は try
try:
    from models import Subject
except Exception:
    Subject = None


analytics_bp = Blueprint("analytics", __name__, url_prefix="/api/analytics")


def score_to_eval(score: int) -> int:
    """0-100(score) -> 評価(0-4)"""
    if score <= 59:
        return 0
    if score <= 69:
        return 1
    if score <= 79:
        return 2
    if score <= 89:
        return 3
    return 4


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


@analytics_bp.get("/grades/chart")
@login_required
def grades_chart():
    """
    グラフ表示用データを返す:
      - records: {student_number, subject_id, eval, unit_x_eval, unit, subject_name}
      - by_student: 学生別の合計(unit_x_eval)
      - by_subject: 科目別の合計(unit_x_eval)
    """
    student_number = (request.args.get("student_number") or "").strip()

    q = Grade.select()
    if student_number:
        q = q.where(Grade.student_id == student_number)

    subject_name_map = _load_subject_name_map()

    records = []
    sum_by_student = defaultdict(int)
    sum_by_subject = defaultdict(int)

    for g in q:
        s_no = g.student_id
        subj_id = int(g.subject_id)
        unit = int(g.unit)
        eval_ = score_to_eval(int(g.score))
        unit_x_eval = unit * eval_

        records.append(
            {
                "student_number": s_no,
                "subject_id": subj_id,
                "subject_name": subject_name_map.get(subj_id, f"科目{subj_id}"),
                "unit": unit,
                "eval": eval_,
                "unit_x_eval": unit_x_eval,
            }
        )

        sum_by_student[s_no] += unit_x_eval
        sum_by_subject[subj_id] += unit_x_eval

    # Chart.js 向け（labels/data）
    student_labels = sorted(sum_by_student.keys())
    student_data = [sum_by_student[k] for k in student_labels]

    subject_labels = sorted(sum_by_subject.keys())
    subject_data = [sum_by_subject[k] for k in subject_labels]
    subject_name_labels = [subject_name_map.get(sid, f"科目{sid}") for sid in subject_labels]

    return jsonify(
        {
            "records": records,
            "by_student": {"labels": student_labels, "data": student_data},
            "by_subject": {"labels": subject_labels, "label_names": subject_name_labels, "data": subject_data},
        }
    )
