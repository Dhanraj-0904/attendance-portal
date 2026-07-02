def apply_batch_table_styling_fix():
    # 1. Update app.js
    with open("backend/static/app.js", "r", encoding="utf-8") as f:
        js = f.read()

    # Replace teacher_username with teacher_name and add title to code tag
    old_row_html = """                <tr>
                    <td><code>${b.sid_batch_id}</code></td>
                    <td><strong>${b.course_name}</strong></td>
                    <td>${b.center_name}</td>
                    <td>${b.teacher_username}</td>"""

    new_row_html = """                <tr>
                    <td><code title="${b.sid_batch_id}">${b.sid_batch_id}</code></td>
                    <td><strong>${b.course_name}</strong></td>
                    <td>${b.center_name}</td>
                    <td>${b.teacher_name || 'Unassigned'}</td>"""

    js = js.replace(old_row_html, new_row_html)

    # Bump version in index.html to bust cache
    with open("backend/static/index.html", "r", encoding="utf-8") as f:
        html = f.read()
    html = html.replace("app.js?v=20", "app.js?v=21")
    html = html.replace("style.css?v=20", "style.css?v=21")
    with open("backend/static/index.html", "w", encoding="utf-8") as f:
        f.write(html)

    with open("backend/static/app.js", "w", encoding="utf-8") as f:
        f.write(js)
    print("Fixed app.js table column mapper and tooltip definitions.")

    # 2. Update style.css
    with open("backend/static/style.css", "r", encoding="utf-8") as f:
        css = f.read()

    table_code_styles = """
/* ================= TABLE BATCH ID ELLIPSIS STYLE ================= */
.data-table td code {
    display: inline-block;
    max-width: 140px;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
    vertical-align: middle;
}
"""
    if ".data-table td code" not in css:
        css += table_code_styles

    with open("backend/static/style.css", "w", encoding="utf-8") as f:
        f.write(css)
    print("Appended data-table ellipsis styles to style.css.")

if __name__ == "__main__":
    apply_batch_table_styling_fix()
