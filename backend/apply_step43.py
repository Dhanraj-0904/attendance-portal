def remove_status_column():
    # 1. Update index.html
    with open("backend/static/index.html", "r", encoding="utf-8") as f:
        html = f.read()

    html = html.replace("<th>Status</th>", "")
    html = html.replace("app.js?v=39", "app.js?v=40")
    html = html.replace("style.css?v=39", "style.css?v=40")

    with open("backend/static/index.html", "w", encoding="utf-8") as f:
        f.write(html)
    print("Removed Status column header from index.html.")

    # 2. Update app.js
    with open("backend/static/app.js", "r", encoding="utf-8") as f:
        js = f.read()

    old_row_renderer = """                <td>${t.subject || 'N/A'}</td>
                <td><span class="badge badge-success">Active</span></td>
                <td>"""

    new_row_renderer = """                <td>${t.subject || 'N/A'}</td>
                <td>"""

    js = js.replace(old_row_renderer, new_row_renderer)
    js = js.replace('colspan="6" class="text-center">No teachers registered', 'colspan="5" class="text-center">No teachers registered')

    with open("backend/static/app.js", "w", encoding="utf-8") as f:
        f.write(js)
    print("Removed Status cell data and updated colspan in app.js.")

if __name__ == "__main__":
    remove_status_column()
