#!/usr/bin/env python3
import os
import subprocess
import json
from dataclasses import dataclass
from flask import Flask, render_template, request, jsonify, send_from_directory

app = Flask(__name__, static_folder=None)  # Disable default static folder

GIT_REPO_PATH = "/home/frozenpipe/dev"  # Default path for git repositories
EXPORT_MARKER = "readme.md"

@dataclass
class Repository:
    name: str
    description: str
    path: str
    exported: bool

def get_repositories():
    """
    Scan the git repository directory and return a list of Repository objects
    """
    repositories = []
    
    # Make sure the git repository path exists
    if not os.path.exists(GIT_REPO_PATH):
        return repositories
    
    # List all subdirectories that are git repositories (have a .git dir or are bare repos)
    for item in os.listdir(GIT_REPO_PATH):
        repo_path = os.path.join(GIT_REPO_PATH, item)
        
        # Skip if not a directory
        if not os.path.isdir(repo_path):
            continue
            
        # Check if it's a git repository (either has a .git directory or is a bare repo with HEAD file)
        if not (os.path.exists(os.path.join(repo_path, ".git")) or 
                os.path.exists(os.path.join(repo_path, "HEAD"))):
            continue
        
        # Check if the git-daemon-export-ok file exists
        exported = os.path.exists(os.path.join(repo_path, EXPORT_MARKER))
        
        # Try to get the repository description from the description file only
        description = ""
        description_file = os.path.join(repo_path, "description")
        if os.path.exists(description_file):
            try:
                with open(description_file, 'r') as f:
                    description = f.read().strip()
                    # Skip default description
                    if description == "Unnamed repository; edit this file 'description' to name the repository.":
                        description = "No description available"
            except:
                description = "No description available"
        else:
            description = "No description available"
        
        repositories.append(Repository(
            name=item,
            description=description,
            path=repo_path,
            exported=exported
        ))
    
    # Sort repositories by name
    repositories.sort(key=lambda repo: repo.name.lower())
    
    return repositories

@app.route('/')
def index():
    repositories = [repo for repo in get_repositories() if repo.exported]
    return render_template('index.html', repositories=repositories)

@app.route('/styles/<path:filename>')
def serve_styles(filename):
    return send_from_directory('styles', filename)

@app.route('/scripts/<path:filename>')
def serve_scripts(filename):
    return send_from_directory('scripts', filename)

@app.route('/api/repo/<int:repo_id>')
def get_repo(repo_id):
    repositories = [repo for repo in get_repositories() if repo.exported]
    
    if repo_id < 0 or repo_id >= len(repositories):
        return jsonify({"error": "Repository not found"}), 404
    
    repo = repositories[repo_id]
    return jsonify({
        "name": repo.name,
        "description": repo.description,
        "path": repo.path
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)
