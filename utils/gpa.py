from models.grade import Grade

def score_to_eval(score: int) -> float:
    """
    点数を評価点に変換する関数

    Args:
        score (int): 点数

    Returns:
        float: 評価点
    """
    if score >= 90:
        return 4.0
    elif score >= 80:
        return 3.0
    elif score >= 70:
        return 2.0
    elif score >= 60:
        return 1.0
    else:
        return 0.0


def calculate_gpa(student_id: str) -> float:
    """
    学生のGPAを計算する関数

    Args:
        student_id (str): 学生ID

    Returns:
        float: GPA
    """
    
    # 学生の成績を取得
    grades = Grade.select().where(Grade.student_id == student_id)

    # 成績を集計
    total_units = 0
    total_points = 0.0
    
    for g in grades:
        eval_ = score_to_eval(g.score)
        total_units += g.unit
        total_points += eval_ * g.unit

    return round(total_points / total_units, 2) if total_units else 0.0