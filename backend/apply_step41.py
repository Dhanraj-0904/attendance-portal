def remove_created_at_column():
    # 1. Update index.html
    with open("backend/static/index.html", "r", encoding="utf-8") as f:
        html = f.read()

    html = html.replace("<th>Created At</th>", "")
    html = html.replace("app.js?v=37", "app.js?v=38")
    html = html.replace("style.css?v=37", "style.css?v=38")

    with open("backend/static/index.html", "w", encoding="utf-8") as f:
        f.write(html)
    print("Removed Created At column header from index.html.")

    # 2. Update app.js
    with open("backend/static/app.js", "r", encoding="utf-8") as f:
        js = f.read()

    old_row_renderer = """                <td>${t.subject || 'N/A'}</td>
                <td><span class="badge badge-success">Active</span></td>
                <td>Today</td>
                <td>"""

    new_row_renderer = """                <td>${t.subject || 'N/A'}</td>
                <td><span class="badge badge-success">Active</span></td>
                <td>"""

    js = js.replace(old_row_renderer, new_row_renderer)

    with open("backend/static/app.js", "w", encoding="utf-8") as f:
        f.write(js)
    print("Removed Created At cell data from app.js.")

if __name__ == "__main__":
    remove_created_at_column()
