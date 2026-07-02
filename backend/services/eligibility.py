import math

def calculate_student_eligibility(total_hours: float, attended_hours: float, remaining_hours: float):
    """
    Calculates student attendance percentage, hours needed, and eligibility status.
    
    Status definitions:
      - ELIGIBLE: Current attendance >= 75%.
      - AT_RISK: Current attendance < 75%, but possible to reach 75% if they attend remaining hours.
      - IMPOSSIBLE: Attendance is < 75% and even if they attend all remaining hours, they cannot reach 75%.
    """
    if total_hours <= 0:
        return {
            "current_pct": 0.0,
            "min_sessions_needed": 0.0,
            "still_need_to_attend": 0.0,
            "can_skip": 0.0,
            "status": "ELIGIBLE"
        }

    hours_held = total_hours - remaining_hours
    current_pct = min(100.0, round((attended_hours / hours_held) * 100, 1)) if hours_held > 0 else 100.0

    target_hours = total_hours * 0.75
    still_need = max(0.0, target_hours - attended_hours)
    can_skip = max(0.0, remaining_hours - still_need)

    if still_need > remaining_hours:
        status = "IMPOSSIBLE"
    elif current_pct >= 75.0:
        status = "ELIGIBLE"
    else:
        status = "AT_RISK"

    return {
        "current_pct": current_pct,
        "min_sessions_needed": round(target_hours, 2),
        "still_need_to_attend": round(still_need, 2),
        "can_skip": round(can_skip, 2),
        "status": status
    }

def calculate_batch_eligibility(students_eligibility_list):
    """
    Calculates class-level eligibility.
    Rule: At least 75% of students in the batch must have >= 75% attendance by the end.
    
    Returns:
        dict: {
            "total_students": int,
            "eligible_students_count": int,
            "eligible_students_pct": float,
            "impossible_students_count": int,
            "status": str  # 'ELIGIBLE', 'AT_RISK', 'IMPOSSIBLE'
        }
    """
    total = len(students_eligibility_list)
    if total == 0:
        return {
            "total_students": 0,
            "eligible_students_count": 0,
            "eligible_students_pct": 100.0,
            "impossible_students_count": 0,
            "status": "ELIGIBLE"
        }

    # Students who currently have >= 75% attendance (ELIGIBLE)
    eligible_count = sum(1 for s in students_eligibility_list if s["status"] == "ELIGIBLE")
    # Students who can NEVER reach 75% attendance (IMPOSSIBLE)
    impossible_count = sum(1 for s in students_eligibility_list if s["status"] == "IMPOSSIBLE")
    # Students who are currently below 75% but could reach it (AT_RISK)
    at_risk_count = sum(1 for s in students_eligibility_list if s["status"] == "AT_RISK")

    eligible_pct = round((eligible_count / total) * 100, 1)
    
    # Check class-level rules
    # If the number of impossible students exceeds 25% of the class, the class can NEVER reach 75% eligibility
    max_impossible_allowed = math.floor(total * 0.25)
    
    if impossible_count > max_impossible_allowed:
        status = "IMPOSSIBLE"  # Too many students are failed; batch cannot meet the 75-75 rule
    elif eligible_count >= math.ceil(total * 0.75):
        status = "ELIGIBLE"    # Batch is currently meeting the 75-75 rule
    else:
        status = "AT_RISK"      # Batch is currently below 75-75 but could recover if AT_RISK students improve

    return {
        "total_students": total,
        "eligible_students_count": eligible_count,
        "eligible_students_pct": eligible_pct,
        "impossible_students_count": impossible_count,
        "at_risk_students_count": at_risk_count,
        "status": status
    }
