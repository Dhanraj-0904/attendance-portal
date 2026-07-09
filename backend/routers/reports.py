from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
import pandas as pd
import io
from ..database import get_db
from ..models import User, Batch, Student, Center, AttendanceRecord, AuditLog
from .auth import get_current_user, require_role
from .batches import get_batch_with_stats
from .students import get_student_with_stats
from ..services.pdf_generator import generate_batch_pdf

router = APIRouter(prefix="/reports", tags=["Reports"])

@router.get("/batch/{id}/pdf")
def get_batch_pdf_report(
    id: int, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    """
    Downloads a professional PDF report containing enrollment, eligibility, and details for a batch.
    """
    batch = db.query(Batch).filter(Batch.id == id).first()
    if not batch:
        raise HTTPException(status_code=404, detail="Batch not found")

    # Access check: Teachers can only download reports for their own batches
    if current_user.role == "teacher" and batch.teacher_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to access reports for this batch"
        )

    # Get batch details and stats
    batch_stats = get_batch_with_stats(batch, db)
    
    # Calculate extra stats needed for header box
    students = db.query(Student).filter(Student.batch_id == id).all()
    students_list = []
    eligible_students_count = 0
    for s in students:
        s_stats = get_student_with_stats(s, db)
        students_list.append(s_stats)
        if s_stats["status"] == "ELIGIBLE":
            eligible_students_count += 1
            
    batch_stats["eligible_students_count"] = eligible_students_count

    # Generate PDF
    pdf_bytes = generate_batch_pdf(batch_stats, students_list)
    
    filename = f"batch_{batch.sid_batch_id}_report.pdf"
    return StreamingResponse(
        io.BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )

@router.get("/batch/{id}/excel")
def get_batch_excel_report(
    id: int, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    """
    Downloads an Excel spreadsheet (.xlsx) containing full attendance details for a batch.
    """
    batch = db.query(Batch).filter(Batch.id == id).first()
    if not batch:
        raise HTTPException(status_code=404, detail="Batch not found")

    if current_user.role == "teacher" and batch.teacher_id != current_user.id:
        raise HTTPException(status_code=403, detail="Unauthorized")

    students = db.query(Student).filter(Student.batch_id == id).all()
    
    records_data = []
    for s in students:
        s_stats = get_student_with_stats(s, db)
        from ..services.eligibility import format_hours_py
        records_data.append({
            "SID Student ID": s_stats["sid_student_id"],
            "Student Name": s_stats["name"],
            "Phone Number": s_stats["phone"] or "N/A",
            "Total Sessions": batch.total_sessions,
            "Attended": float(format_hours_py(s_stats["attended_sessions"])),
            "Missed": float(format_hours_py(s_stats["missed_sessions"])),
            "Attendance %": f"{s_stats['attendance_pct']}%",
            "Eligibility Status": s_stats["status"],
            "Sessions Needed to Qualify": s_stats["still_need_to_attend"]
        })

    # Create DataFrame
    df = pd.DataFrame(records_data)
    
    # Save to Excel in memory
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name="Attendance Summary")
        
    output.seek(0)
    
    filename = f"batch_{batch.sid_batch_id}_export.xlsx"
    return StreamingResponse(
        output,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )

@router.get("/global")
def get_global_admin_stats(
    db: Session = Depends(get_db), 
    current_user: User = Depends(require_role(["admin"]))
):
    """
    Returns data for the NGO Coordinator Dashboard:
    - Global stats (student count, batch count, at-risk count).
    - Center-wise comparison.
    - Teacher ranking.
    - Audit Logs.
    """
    total_students = db.query(Student).count()
    total_batches = db.query(Batch).count()
    total_centers = db.query(Center).count()
    
    # Calculate at risk students globally
    at_risk_count = 0
    all_students = db.query(Student).all()
    for s in all_students:
        s_stats = get_student_with_stats(s, db)
        if s_stats["status"] in ["AT_RISK", "IMPOSSIBLE"]:
            at_risk_count += 1

    # Center-wise comparison
    centers = db.query(Center).all()
    center_stats = []
    for c in centers:
        batches = db.query(Batch).filter(Batch.center_id == c.id).all()
        c_student_count = 0
        total_pct_sum = 0.0
        active_batches_count = len(batches)
        
        for b in batches:
            b_students = db.query(Student).filter(Student.batch_id == b.id).all()
            c_student_count += len(b_students)
            for s in b_students:
                s_stats = get_student_with_stats(s, db)
                total_pct_sum += s_stats["attendance_pct"]
                
        avg_attendance = round(total_pct_sum / c_student_count, 1) if c_student_count > 0 else 0.0
        center_stats.append({
            "id": c.id,
            "name": c.name,
            "district": c.district,
            "nsdc_code": c.nsdc_center_code,
            "batches_count": active_batches_count,
            "students_count": c_student_count,
            "average_attendance": avg_attendance
        })

    # Teacher rankings
    teachers = db.query(User).filter(User.role == "teacher").all()
    teacher_stats = []
    for t in teachers:
        t_batches = db.query(Batch).filter(Batch.teacher_id == t.id).all()
        t_student_count = 0
        t_pct_sum = 0.0
        
        for b in t_batches:
            b_students = db.query(Student).filter(Student.batch_id == b.id).all()
            t_student_count += len(b_students)
            for s in b_students:
                s_stats = get_student_with_stats(s, db)
                t_pct_sum += s_stats["attendance_pct"]
                
        avg_attendance = round(t_pct_sum / t_student_count, 1) if t_student_count > 0 else 0.0
        teacher_stats.append({
            "id": t.id,
            "username": t.username,
            "email": t.email,
            "phone": t.phone,
            "subject": t.subject,
            "plain_password": t.plain_password,
            "batches_count": len(t_batches),
            "students_count": t_student_count,
            "average_attendance": avg_attendance
        })
        
    # Sort teacher rankings by average attendance descending
    teacher_stats.sort(key=lambda x: x["average_attendance"], reverse=True)

    # Audit logs
    logs = db.query(AuditLog).order_by(AuditLog.timestamp.desc()).limit(50).all()
    audit_data = []
    for l in logs:
        user = db.query(User).filter(User.id == l.user_id).first()
        audit_data.append({
            "id": l.id,
            "user_id": l.user_id,
            "username": user.username if user else "Deleted User",
            "action": l.action,
            "table_name": l.table_name,
            "record_id": l.record_id,
            "timestamp": l.timestamp.strftime("%Y-%m-%d %H:%M:%S")
        })

    return {
        "global": {
            "total_students": total_students,
            "total_batches": total_batches,
            "total_centers": total_centers,
            "at_risk_students_count": at_risk_count
        },
        "centers": center_stats,
        "teachers": teacher_stats,
        "audit_logs": audit_data
    }
