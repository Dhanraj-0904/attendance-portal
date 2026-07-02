def add_global_fetch_interceptor():
    # 1. Update index.html
    with open("backend/static/index.html", "r", encoding="utf-8") as f:
        html = f.read()

    html = html.replace("app.js?v=41", "app.js?v=42")
    html = html.replace("style.css?v=41", "style.css?v=42")

    with open("backend/static/index.html", "w", encoding="utf-8") as f:
        f.write(html)
    print("Bumped version to v=42 in index.html.")

    # 2. Update app.js
    with open("backend/static/app.js", "r", encoding="utf-8") as f:
        js = f.read()

    # Find the state definition to inject the interceptor right after it or at the top of the file.
    # Let's define the interceptor at the very beginning of app.js.
    interceptor_code = """// Global Fetch Interceptor to handle session expiration (401 Unauthorized)
const originalFetch = window.fetch;
window.fetch = async function(...args) {
    const response = await originalFetch(...args);
    if (response.status === 401 && state.token) {
        state.token = null;
        state.role = null;
        state.username = null;
        localStorage.clear();
        document.getElementById("main-screen").classList.remove("active");
        document.getElementById("login-screen").classList.add("active");
        showToast("Session expired. Please log in again.", "error");
    }
    return response;
};

"""

    # Insert interceptor code after window.onerror
    js = js.replace("window.onerror = function(message, source, lineno, colno, error) {\n    showToast(`JS Error: ${message} (line ${lineno})`, \"error\");\n    console.error(error);\n    return false;\n};",
                    "window.onerror = function(message, source, lineno, colno, error) {\n    showToast(`JS Error: ${message} (line ${lineno})`, \"error\");\n    console.error(error);\n    return false;\n};\n\n" + interceptor_code.strip())

    with open("backend/static/app.js", "w", encoding="utf-8") as f:
        f.write(js)
    print("Added global fetch interceptor to app.js.")

if __name__ == "__main__":
    add_global_fetch_interceptor()
