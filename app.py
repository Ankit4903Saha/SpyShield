# app.py

from flask import Flask, render_template, abort
from storage import load_apps

app = Flask(__name__)

# Load once at startup; for simplicity.
# If you want dynamic reload, you can call load_apps() inside each route instead.
APPS = load_apps()


@app.route("/")
def index():
    """
    Home page: list all apps with risk scores.
    """
    # Convert dict -> list for template
    apps_list = list(APPS.values())

    # Sort by risk score descending
    apps_list.sort(key=lambda x: x.get("risk_score", 0), reverse=True)

    return render_template("index.html", apps=apps_list)


@app.route("/app/<package_name>")
def app_detail(package_name: str):
    """
    Detail view for an individual app.
    """
    app_info = APPS.get(package_name)
    if not app_info:
        abort(404, description="App not found")

    return render_template("app_detail.html", app=app_info)


if __name__ == "__main__":
    # Run in debug mode for development
    app.run(host="0.0.0.0", port=5001, debug=True)
