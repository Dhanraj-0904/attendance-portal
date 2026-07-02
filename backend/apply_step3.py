def apply_flex_layout_to_actions():
    # 1. Update style.css to add flex styles for action containers
    with open("backend/static/style.css", "r", encoding="utf-8") as f:
        css = f.read()

    action_layouts = """
/* ================= ACTION WRAPPER FLEX LAYOUTS ================= */
.header-actions {
    display: flex;
    align-items: center;
    gap: 12px;
}

.actions-cell {
    display: flex;
    align-items: center;
    gap: 8px;
    flex-wrap: nowrap;
}
"""
    if "/* ================= ACTION WRAPPER FLEX LAYOUTS ================= */" not in css:
        css += action_layouts

    with open("backend/static/style.css", "w", encoding="utf-8") as f:
        f.write(css)
    print("Updated style.css with action flex styling.")

    # 2. Update app.js to wrap buttons in actions-cell divs
    with open("backend/static/app.js", "r", encoding="utf-8") as f:
        js = f.read()

    # Replace Admin Batches list actions
    old_batches_actions = """                    <td>
                        <button class="btn btn-primary btn-small" onclick="viewAdminBatchDetails(${b.id})" style="margin-right: 5px;">🔍 View</button>
                        <button class="btn btn-secondary btn-small" onclick="deleteBatch(${b.id})">🗑️ Delete</button>
                    </td>"""

    new_batches_actions = """                    <td>
                        <div class="actions-cell">
                            <button class="btn btn-primary btn-small" onclick="viewAdminBatchDetails(${b.id})">🔍 View</button>
                            <button class="btn btn-secondary btn-small" onclick="deleteBatch(${b.id})">🗑️ Delete</button>
                        </div>
                    </td>"""

    js = js.replace(old_batches_actions, new_batches_actions)

    # Replace Admin Centers list actions
    old_centers_actions = """                <td>
                    <button class="btn btn-secondary btn-small" onclick="deleteCenter(${c.id})">🗑️ Delete</button>
                </td>"""

    new_centers_actions = """                <td>
                    <div class="actions-cell">
                        <button class="btn btn-secondary btn-small" onclick="deleteCenter(${c.id})">🗑️ Delete</button>
                    </div>
                </td>"""

    js = js.replace(old_centers_actions, new_centers_actions)

    with open("backend/static/app.js", "w", encoding="utf-8") as f:
        f.write(js)
    print("Updated app.js with actions-cell wrappers.")

    # 3. Update index.html version parameter to force stylesheet reload
    with open("backend/static/index.html", "r", encoding="utf-8") as f:
        html = f.read()

    html = html.replace('style.css?v=5', 'style.css?v=5.1')

    with open("backend/static/index.html", "w", encoding="utf-8") as f:
        f.write(html)
    print("Updated index.html style version successfully.")

if __name__ == "__main__":
    apply_flex_layout_to_actions()
