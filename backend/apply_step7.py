def apply_theme_refinements_for_undo():
    # 1. Update style.css to add select option styles and destructive button class
    with open("backend/static/style.css", "r", encoding="utf-8") as f:
        css = f.read()

    refinements = """
/* ================= UNDO THEME REFINEMENTS ================= */
.btn-destructive {
    background: rgba(255, 23, 68, 0.05);
    color: var(--status-impossible);
    border: 1px solid var(--status-impossible);
    box-shadow: none;
}

.btn-destructive:hover {
    background: var(--status-impossible) !important;
    color: white !important;
    box-shadow: 0 4px 15px rgba(255, 23, 68, 0.3);
    transform: translateY(-2px);
}

select option {
    background-color: #1a153b;
    color: white;
}

body.light-theme select option {
    background-color: white;
    color: #0f172a;
}
"""
    if "/* ================= UNDO THEME REFINEMENTS ================= */" not in css:
        css += refinements

    with open("backend/static/style.css", "w", encoding="utf-8") as f:
        f.write(css)
    print("Updated style.css with undo refinements.")

    # 2. Update index.html to use the new btn-destructive class
    with open("backend/static/index.html", "r", encoding="utf-8") as f:
        html = f.read()

    # Replace Revert button
    old_btn = '<button type="submit" class="btn btn-secondary btn-block" style="border-color: var(--status-impossible); color: var(--status-impossible);">'
    new_btn = '<button type="submit" class="btn btn-destructive btn-block">'
    
    html = html.replace(old_btn, new_btn)

    # Bump style version tag
    html = html.replace('style.css?v=6.1', 'style.css?v=7.1')

    with open("backend/static/index.html", "w", encoding="utf-8") as f:
        f.write(html)
    print("Updated index.html style version and button class successfully.")

if __name__ == "__main__":
    apply_theme_refinements_for_undo()
