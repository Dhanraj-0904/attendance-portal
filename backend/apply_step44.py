def rename_rankings_header():
    # 1. Update index.html
    with open("backend/static/index.html", "r", encoding="utf-8") as f:
        html = f.read()

    html = html.replace("<h2>Teacher Rankings</h2>", "<h2>Teacher Attendance Summary</h2>")
    html = html.replace("app.js?v=40", "app.js?v=41")
    html = html.replace("style.css?v=40", "style.css?v=41")

    with open("backend/static/index.html", "w", encoding="utf-8") as f:
        f.write(html)
    print("Renamed Teacher Rankings to Teacher Attendance Summary in index.html.")

if __name__ == "__main__":
    rename_rankings_header()
