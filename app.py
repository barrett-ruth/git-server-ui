#!/usr/bin/env python3

import getpass
import os
from dataclasses import dataclass
from pathlib import Path

from flask import Flask, abort, jsonify, render_template, request, send_from_directory

app = Flask(__name__, static_folder=None)

git_repo_path = str(Path.home() / "dev")
gist_path = str(Path.home() / "gists")
export_marker = "readme.md"
if getpass.getuser() == "apache":
    git_repo_path = "/srv/git"
    gist_path = "/srv/gists"
    export_marker = "git-daemon-export-ok"


@dataclass
class Repository:
    name: str
    description: str
    path: str
    exported: bool


def get_repositories():
    repositories = []

    if not os.path.exists(git_repo_path):
        return repositories

    for item in os.listdir(git_repo_path):
        repo_path = os.path.join(git_repo_path, item)

        if not os.path.isdir(repo_path):
            continue

        if not (
            os.path.exists(os.path.join(repo_path, ".git"))
            or os.path.exists(os.path.join(repo_path, "HEAD"))
        ):
            continue

        exported = os.path.exists(os.path.join(repo_path, export_marker))

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


@app.route("/gist/<path:filename>")
def serve_gist(filename):
    base = Path(gist_path).resolve()
    target = (base / filename).resolve()
    if base not in target.parents and base != target:
        abort(404)
    if not target.exists() or not target.is_file():
        abort(404)

    try:
        content = target.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return "Binary file cannot be displayed", 400

    ext = target.suffix.lstrip(".") or "plaintext"
    return render_template("gist.html", filename=filename, code=content, lang=ext)


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
