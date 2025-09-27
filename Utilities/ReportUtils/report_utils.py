import json
from datetime import datetime

import allure


# ---------- HTML ----------
def generate_html(results, out="report.html"):
    with open(out, "w", encoding="utf-8") as f:
        f.write(f"<h1>Test Report {datetime.now()}</h1><table border=1>")
        f.write("<tr><th>Test</th><th>Status</th><th>Duration</th></tr>")
        for r in results:
            f.write(f"<tr><td>{r['test']}</td><td>{r['status']}</td><td>{r['duration']}s</td></tr>")
        f.write("</table>")


# ---------- JSON ----------
def save_json(results, out="results.json"):
    with open(out, "w", encoding="utf-8") as f:
        json.dump({"time": str(datetime.now()), "results": results}, f, indent=4)


# ---------- Allure ----------
def log_step(name):
    def decorator(func):
        def wrapper(*a, **kw):
            with allure.step(name):
                return func(*a, **kw)

        return wrapper

    return decorator


def attach_text(name, content):
    allure.attach(content, name=name, attachment_type=allure.attachment_type.TEXT)


def attach_screenshot(name, path):
    with open(path, "rb") as f:
        allure.attach(f.read(), name=name, attachment_type=allure.attachment_type.PNG)
