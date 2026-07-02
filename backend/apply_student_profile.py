def inject_student_profile_endpoint():
    with open("backend/routers/students.py", "r", encoding="utf-8") as f:
        content = f.read()

    my_profile_code = """
@router.get("/my-profile")
def get_my_student_profile(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.role != "student":
        raise HTTPException(status_code=403, detail="Only students can access this profile")
        
    student = db.query(Student).filter(Student.user_id == current_user.id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student profile not found")
        
    stats = get_student_with_stats(student, db)
    
    # Generate calendar logs
    records = db.query(AttendanceRecord).filter(
        AttendanceRecord.student_id == student.id
    ).order_by(AttendanceRecord.session_date.asc()).all()
    
    calendar_logs = []
    for i, r in enumerate(records, start=1):
        calendar_logs.append({
            "day_number": i,
            "date": r.session_date.strftime("%Y-%m-%d"),
            "status": "PRESENT" if r.status == "present" else "ABSENT"
        })
        
    stats["calendar_logs"] = calendar_logs
    stats["sessions_attended"] = stats["attended_sessions"]
    stats["sessions_missed"] = stats["missed_sessions"]
    stats["sessions_remaining"] = stats["remaining_sessions"]
    stats["sessions_needed_for_75"] = stats["still_need_to_attend"]
    
    return stats
"""

    if '/my-profile' not in content:
        # Insert before @router.get("/{id}"
        content = content.replace('@router.get("/{id}"', my_profile_code + '\n@router.get("/{id}"')

    with open("backend/routers/students.py", "w", encoding="utf-8") as f:
        f.write(content)
    print("Injected /students/my-profile endpoint into students.py successfully.")

if __name__ == "__main__":
    inject_student_profile_endpoint()
