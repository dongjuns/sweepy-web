from flask import Flask, request, jsonify
from sweepy import analyze

app = Flask(__name__)

@app.route('/')
def home():
    return {'status': 'ok', 'usage': 'GET /analyze?repo=<github_url>'}

@app.route('/analyze')
def analyze_repo():
    repo = request.args.get('repo')
    if not repo:
        return jsonify({'error': 'repo parameter required'}), 400
    
    result = analyze(repo)
    
    return jsonify({
        'repo': result.repo_path,
        'files_analyzed': result.files_analyzed,
        'unused_imports': [
            {'file': item.file, 'line': item.line, 'module': item.module}
            for item in result.unused_imports
        ]
    })
