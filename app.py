#!/usr/bin/env python3

import getpass
import os
from dataclasses import dataclass
from pathlib import Path

from flask import Flask, jsonify, render_template, send_from_directory, abort
from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import TextLexer, get_lexer_for_filename

app = Flask(__name__, static_folder=None)

GIT_REPO_PATH = str(Path.home() / "dev")
GIST_PATH = str(Path.home() / "gists")
EXPORT_MARKER = "readme.md"
if getpass.getuser() == "apache":
    GIT_REPO_PATH = "/srv/git"
    GIST_PATH = "/srv/gists"
    EXPORT_MARKER = "git-daemon-export-ok"


@dataclass
class Repository:
    name: str
    description: str
    path: str
    exported: bool


def get_repositories():
    repositories = []

    if not os.path.exists(GIT_REPO_PATH):
        return repositories

    for item in os.listdir(GIT_REPO_PATH):
        repo_path = os.path.join(GIT_REPO_PATH, item)

        if not os.path.isdir(repo_path):
            continue

        if not (
            os.path.exists(os.path.join(repo_path, ".git"))
            or os.path.exists(os.path.join(repo_path, "HEAD"))
        ):
            continue

        exported = os.path.exists(os.path.join(repo_path, EXPORT_MARKER))

        description = "No description available"
        description_file = os.path.join(repo_path, "description")
        if os.path.exists(description_file):
            try:
                with open(description_file, "r") as f:
                    description = f.read().strip()
                    if (
                        description
                        == "Unnamed repository; edit this file 'description' to name the repository."
                    ):
                        description = "No description available"
            except _ as _:
                pass

        display_name = item
        if display_name.lower().endswith(".git"):
            display_name = display_name[:-4]

        repositories.append(
            Repository(
                name=display_name,
                description=description,
                path=repo_path,
                exported=exported,
            )
        )

    repositories.sort(key=lambda repo: repo.name.lower())

    return repositories


@app.route("/")
def index():
    repositories = [repo for repo in get_repositories() if repo.exported]
    return render_template("index.html", repositories=repositories)


@app.route("/styles/<path:filename>")
def serve_styles(filename):
    return send_from_directory("styles", filename)


@app.route("/scripts/<path:filename>")
def serve_scripts(filename):
    return send_from_directory("scripts", filename)


@app.route("/gist/<path:filename>")
def serve_gist(filename):
    file_path = os.path.join(GIST_PATH, filename)

    if not os.path.exists(file_path) or not os.path.isfile(file_path):
        abort(404)

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
    except UnicodeDecodeError:
        return "Binary file cannot be displayed", 400

    try:
        lexer = get_lexer_for_filename(filename)
    except:
        lexer = TextLexer()

    formatter = HtmlFormatter(style="default", cssclass="highlight", linenos=True, noclasses=True, cssstyles="padding: 20px; font-size: 18px; background-color: #f8f8f8;") 
    highlighted = highlight(content, lexer, formatter)
    highlighted = highlighted.replace('<td class="code">', '<td class="code" style="padding-left: 20px;">')

    return render_template("gist.html", filename=filename, highlighted_code=highlighted)


@app.errorhandler(404)
def not_found(error):
    return render_template("404.html"), 404


@app.route("/api/repo/<int:repo_id>")
def get_repo(repo_id):
    repositories = [repo for repo in get_repositories() if repo.exported]

    if repo_id < 0 or repo_id >= len(repositories):
        return jsonify({"error": "Repository not found"}), 404

    repo = repositories[repo_id]
    return jsonify(
        {"name": repo.name, "description": repo.description, "path": repo.path}
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
