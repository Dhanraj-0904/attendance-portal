def apply_option_font_color_refinements():
    # 1. Update style.css to add styled option colors for select dropdowns
    with open("backend/static/style.css", "r", encoding="utf-8") as f:
        css = f.read()

    option_color_styles = """
/* ================= DROPDOWN OPTION FONT COLORS ================= */
select option {
    color: #e2e8f0; /* soft light gray for standard options in dark mode */
}

select option[value=""] {
    color: #718096 !important; /* muted gray for '-- Choose Batch --' placeholder in dark mode */
}

body.light-theme select option {
    color: #1e293b; /* dark slate for options in light mode */
}

body.light-theme select option[value=""] {
    color: #94a3b8 !important; /* muted gray for '-- Choose Batch --' placeholder in light mode */
}
"""
    if "/* ================= DROPDOWN OPTION FONT COLORS ================= */" not in css:
        css += option_color_styles

    with open("backend/static/style.css", "w", encoding="utf-8") as f:
        f.write(css)
    print("Updated style.css with dropdown option font colors.")

    # 2. Update index.html to bump stylesheet version parameter
    with open("backend/static/index.html", "r", encoding="utf-8") as f:
        html = f.read()

    html = html.replace('style.css?v=7.2', 'style.css?v=7.3')

    with open("backend/static/index.html", "w", encoding="utf-8") as f:
        f.write(html)
    print("Updated index.html style version to v=7.3 successfully.")

if __name__ == "__main__":
    apply_option_font_color_refinements()
