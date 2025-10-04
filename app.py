#!/usr/bin/env python3

import getpass
import os
from dataclasses import dataclass
from pathlib import Path

from flask import Flask, jsonify, render_template, send_from_directory, abort, request
from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import TextLexer, get_lexer_for_filename
from pygments.util import ClassNotFound

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
                with open(description_file, "r", encoding="utf-8") as f:
                    description = f.read().strip()
                    if (
                        description
                        == "Unnamed repository; edit this file 'description' to name the repository."
                    ):
                        description = "No description available"
            except OSError:
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
    base = Path(GIST_PATH).resolve()
    target = (base / filename).resolve()
    if base not in target.parents and base != target:
        abort(404)

    if not target.exists() or not target.is_file():
        abort(404)

    try:
        content = target.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return "Binary file cannot be displayed", 400
    except OSError:
        abort(404)

    try:
        lexer = get_lexer_for_filename(target.name)
    except ClassNotFound:
        lexer = TextLexer()

    formatter = HtmlFormatter(
        style="default",
        cssclass="highlight",
        linenos=False,
        noclasses=True,
        cssstyles="padding: 20px; font-size: 18px; background-color: #f8f8f8;",
    )
    highlighted = highlight(content, lexer, formatter)
    highlighted = highlighted.replace(
        '<td class="code">', '<td class="code" style="padding-left: 20px;">'
    )

    return render_template("gist.html", filename=filename, highlighted_code=highlighted)


@app.route("/<path:filename>")
def serve_gist_root(filename):
    head = filename.split("/", 1)[0]
    if head in {"styles", "scripts", "api", "gist"}:
        abort(404)
    host = request.host.split(":", 1)[0]
    if host in {"gist.barrettruth.com", "localhost", "127.0.0.1"}:
        return serve_gist(filename)
    abort(404)


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
    app.run(host="0.0.0.0", port=5000, debug=True)

