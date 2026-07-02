import io
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

def generate_batch_pdf(batch_info: dict, students_list: list) -> bytes:
    """
    Generates a professional PDF report for a batch using ReportLab.
    Returns:
        bytes: PDF binary content
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40
    )

    story = []
    styles = getSampleStyleSheet()

    # Define custom styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=24,
        leading=28,
        textColor=colors.HexColor('#1e293b'),
        spaceAfter=15
    )
    
    meta_style = ParagraphStyle(
        'MetaText',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        textColor=colors.HexColor('#475569')
    )

    h2_style = ParagraphStyle(
        'Heading2',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=14,
        leading=18,
        textColor=colors.HexColor('#0f172a'),
        spaceBefore=15,
        spaceAfter=10
    )

    # Document Header
    story.append(Paragraph("LIVELIHOOD SKILLS TRAINING PORTAL", ParagraphStyle('SubTitle', fontName='Helvetica-Bold', fontSize=10, textColor=colors.HexColor('#2563eb'), spaceAfter=5)))
    story.append(Paragraph("Batch Attendance & Eligibility Report", title_style))
    story.append(Spacer(1, 10))

    # Batch Details Grid
    details_data = [
        [
            Paragraph(f"<b>Course Name:</b> {batch_info['course_name']}", meta_style),
            Paragraph(f"<b>Training Center:</b> {batch_info['center_name']}", meta_style)
        ],
        [
            Paragraph(f"<b>SID Batch ID:</b> {batch_info['sid_batch_id']}", meta_style),
            Paragraph(f"<b>Assigned Teacher:</b> {batch_info['teacher_name']}", meta_style)
        ],
        [
            Paragraph(f"<b>Start Date:</b> {batch_info['start_date']}", meta_style),
            Paragraph(f"<b>End Date:</b> {batch_info['end_date']}", meta_style)
        ],
        [
            Paragraph(f"<b>Total Course Hours:</b> {batch_info.get('total_hours', 330)} hrs", meta_style),
            Paragraph(f"<b>Generated At:</b> {datetime.now().strftime('%Y-%m-%d %H:%M')}", meta_style)
        ]
    ]
    
    details_table = Table(details_data, colWidths=[270, 270])
    details_table.setStyle(TableStyle([
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('TOPPADDING', (0,0), (-1,-1), 6),
    ]))
    
    story.append(details_table)
    story.append(Spacer(1, 15))

    # Class Eligibility Status Block
    status_color = '#10b981'  # Green
    if batch_info['class_status'] == 'AT_RISK':
        status_color = '#f59e0b'  # Yellow/Orange
    elif batch_info['class_status'] == 'IMPOSSIBLE':
        status_color = '#ef4444'  # Red

    eligibility_box_data = [
        [
            Paragraph(f"<font color='white'><b>CLASS ELIGIBILITY SUMMARY</b><br/>"
                      f"Eligible Students: {batch_info['class_eligibility_pct']}% "
                      f"({batch_info['eligible_students_count']}/{batch_info['students_count']})<br/>"
                      f"Current Class Status: <b>{batch_info['class_status']}</b></font>", 
                      ParagraphStyle('WhiteText', fontName='Helvetica', fontSize=11, leading=16))
        ]
    ]
    eligibility_table = Table(eligibility_box_data, colWidths=[540])
    eligibility_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor(status_color)),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 12),
        ('BOTTOMPADDING', (0,0), (-1,-1), 12),
        ('LEFTPADDING', (0,0), (-1,-1), 15),
        ('RIGHTPADDING', (0,0), (-1,-1), 15),
    ]))
    
    story.append(eligibility_table)
    story.append(Spacer(1, 20))

    # Student Table Header
    story.append(Paragraph("Student List & Attendance Details", h2_style))
    
    table_header_style = ParagraphStyle(
        'HeaderStyle',
        fontName='Helvetica-Bold',
        fontSize=9,
        leading=11,
        textColor=colors.HexColor('#0f172a')
    )

    table_cell_style = ParagraphStyle(
        'CellStyle',
        fontName='Helvetica',
        fontSize=9,
        leading=12,
        textColor=colors.HexColor('#334155')
    )

    table_data = [
        [
            Paragraph("<b>Sl No</b>", table_header_style),
            Paragraph("<b>SID ID</b>", table_header_style),
            Paragraph("<b>Student Name</b>", table_header_style),
            Paragraph("<b>Attended (hrs)</b>", table_header_style),
            Paragraph("<b>Missed (hrs)</b>", table_header_style),
            Paragraph("<b>Attendance %</b>", table_header_style),
            Paragraph("<b>Status</b>", table_header_style),
        ]
    ]

    for idx, s in enumerate(students_list, start=1):
        pct_color = '#0f172a'
        status_text_color = '#10b981' # Green
        
        if s['status'] == 'AT_RISK':
            status_text_color = '#d97706' # Orange
        elif s['status'] == 'IMPOSSIBLE':
            status_text_color = '#dc2626' # Red
            
        table_data.append([
            Paragraph(str(idx), table_cell_style),
            Paragraph(s['sid_student_id'], table_cell_style),
            Paragraph(s['name'], table_cell_style),
            Paragraph(f"{round(s['attended_sessions'], 1)} hrs", table_cell_style),
            Paragraph(f"{round(s['missed_sessions'], 1)} hrs", table_cell_style),
            Paragraph(f"<b>{s['attendance_pct']}%</b>", table_cell_style),
            Paragraph(f"<font color='{status_text_color}'><b>{s['status']}</b></font>", table_cell_style),
        ])

    student_table = Table(table_data, colWidths=[40, 95, 155, 60, 50, 80, 60])
    student_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#f1f5f9')),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
    ]))
    
    # Alternate row colors
    for i in range(1, len(table_data)):
        if i % 2 == 0:
            student_table.setStyle(TableStyle([
                ('BACKGROUND', (0,i), (-1,i), colors.HexColor('#f8fafc'))
            ]))

    story.append(student_table)

    # Footer helper
    def add_footer(canvas, doc):
        canvas.saveState()
        canvas.setFont('Helvetica', 8)
        canvas.setFillColor(colors.HexColor('#94a3b8'))
        canvas.drawString(40, 20, "Confidential - NGO Internal Attendance Records")
        canvas.drawRightString(doc.pagesize[0] - 40, 20, f"Page {doc.page}")
        canvas.restoreState()

    doc.build(story, onFirstPage=add_footer, onLaterPages=add_footer)
    
    buffer.seek(0)
    pdf_bytes = buffer.getvalue()
    buffer.close()
    return pdf_bytes
