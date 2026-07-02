def apply_mobile_responsive_styles():
    # 1. Update style.css to add mobile responsiveness
    with open("backend/static/style.css", "r", encoding="utf-8") as f:
        css = f.read()

    mobile_styles = """
/* ================= RESPONSIVE MOBILE MEDIA QUERIES ================= */
@media (max-width: 768px) {
    .app-layout {
        flex-direction: column;
    }
    
    .sidebar {
        width: 100%;
        border-right: none;
        border-bottom: 1px solid var(--card-border);
        padding: 12px 15px;
        display: flex;
        flex-direction: row;
        overflow-x: auto;
        gap: 10px;
        position: sticky;
        top: 70px;
        background: rgba(12, 8, 30, 0.95);
        z-index: 99;
    }
    
    /* Make the navigation items scroll horizontally on mobile */
    .nav-group {
        display: flex;
        flex-direction: row;
        align-items: center;
        width: 100%;
        overflow-x: auto;
        gap: 8px;
    }
    
    .nav-group h3 {
        display: none !important;
    }
    
    .nav-item {
        margin-bottom: 0;
        white-space: nowrap;
        padding: 8px 12px;
        font-size: 13px;
    }
    
    .content-area {
        padding: 20px 15px;
    }
    
    .metrics-grid {
        grid-template-columns: repeat(2, 1fr);
        gap: 12px;
    }
    
    .metric-card {
        padding: 16px;
        flex-direction: column;
        text-align: center;
        gap: 10px;
    }
    
    .metric-icon {
        width: 40px;
        height: 40px;
        font-size: 18px;
    }
    
    .content-grid {
        grid-template-columns: 1fr;
        gap: 20px;
    }
    
    .student-profile-layout {
        grid-template-columns: 1fr;
        gap: 20px;
    }
    
    .progress-ring-container {
        width: 140px;
        height: 140px;
    }
    
    .class-summary-grid {
        grid-template-columns: repeat(2, 1fr);
        gap: 12px;
    }
    
    .login-card {
        padding: 24px;
        margin: 15px;
    }
    
    .flex-header {
        flex-direction: column;
        align-items: flex-start;
        gap: 15px;
    }
    
    #batch-detail-actions, #admin-batch-detail-actions {
        width: 100%;
        display: flex;
        gap: 10px;
    }
    
    #batch-detail-actions button, #admin-batch-detail-actions button {
        flex: 1;
        font-size: 12px;
        padding: 8px 12px;
    }
}

/* Light Theme overrides for mobile horizontal bar background */
body.light-theme .sidebar {
    background: rgba(248, 250, 252, 0.95);
}
"""
    if "/* ================= RESPONSIVE MOBILE MEDIA QUERIES ================= */" not in css:
        css += mobile_styles

    with open("backend/static/style.css", "w", encoding="utf-8") as f:
        f.write(css)
    print("Updated style.css with mobile responsive rules.")

    # 2. Update index.html version parameter to force stylesheet reload
    with open("backend/static/index.html", "r", encoding="utf-8") as f:
        html = f.read()

    html = html.replace('style.css?v=6', 'style.css?v=6.1')

    with open("backend/static/index.html", "w", encoding="utf-8") as f:
        f.write(html)
    print("Updated index.html style version successfully.")

if __name__ == "__main__":
    apply_mobile_responsive_styles()
