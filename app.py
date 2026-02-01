from flask import Flask, request, jsonify, render_template_string
from sweepy import analyze

app = Flask(__name__)

HTML = '''
<!DOCTYPE html>
<html>
<head>
    <title>sweepy</title>
    <style>
        * { box-sizing: border-box; }
        body { font-family: -apple-system, sans-serif; max-width: 800px; margin: 0 auto; padding: 40px 20px; background: #0d1117; color: #c9d1d9; }
        .header { display: flex; align-items: center; gap: 16px; margin-bottom: 8px; }
        .logo-image { width: 56px; height: 56px; }
        h1 { color: #58a6ff; margin: 0; }
        input { width: 100%; padding: 12px; font-size: 16px; border: 1px solid #30363d; border-radius: 6px; background: #161b22; color: #c9d1d9; margin-bottom: 12px; }
        button { padding: 12px 24px; font-size: 16px; background: #238636; color: white; border: none; border-radius: 6px; cursor: pointer; }
        button:hover { background: #2ea043; }
        button:disabled { background: #30363d; cursor: wait; }
        #result { margin-top: 24px; padding: 16px; background: #161b22; border-radius: 6px; white-space: pre-wrap; font-family: monospace; display: none; }
        .file { color: #58a6ff; font-weight: bold; margin-top: 12px; }
        .line { color: #8b949e; }
        .module { color: #f97583; }
        .success { color: #3fb950; }
        .error { color: #f85149; }
        .summary { color: #8b949e; margin-bottom: 16px; border-bottom: 1px solid #30363d; padding-bottom: 12px; }
    </style>
</head>
<body>
    <div class="header">
        <img src="/static/sweepy.png" alt="sweepy" class="logo-image">
        <h1>sweepy</h1>
    </div>
    <p>Sweep away unused imports from your codebase.</p>
    <input type="text" id="repo" placeholder="https://github.com/user/repo">
    <button onclick="analyze()">Analyze</button>
    <div id="result"></div>
    <script>
        async function analyze() {
            const repo = document.getElementById('repo').value;
            const btn = document.querySelector('button');
            const result = document.getElementById('result');
            
            if (!repo) return;
            
            btn.disabled = true;
            btn.textContent = 'Analyzing...';
            result.style.display = 'block';
            result.innerHTML = 'Cloning repository and analyzing imports. <br>This may take a moment for large repos.';
            
            const res = await fetch('/analyze?repo=' + encodeURIComponent(repo));
            const data = await res.json();
            
            btn.disabled = false;
            btn.textContent = 'Analyze';
            
            if (data.error) {
                result.innerHTML = '<span class="error">Error: ' + data.error + '</span>';
                return;
            }
            
            let html = '<div class="summary">';
            html += 'Repository: ' + data.repo + '<br>';
            if (data.branch) {
                html += 'Branch: ' + data.branch + '<br>';
            }
            html += 'Files analyzed: ' + data.files_analyzed + '<br>';
            html += 'Unused imports: ' + data.unused_imports.length + '</div>';
            
            if (data.unused_imports.length === 0) {
                html += '<span class="success">No unused imports found!</span>';
            } else {
                let currentFile = '';
                data.unused_imports.forEach(item => {
                    if (item.file !== currentFile) {
                        currentFile = item.file;
                        html += '<div class="file">' + item.file + '</div>';
                    }
                    html += '<div><span class="line">Line ' + item.line + ':</span> <span class="module">' + item.module + '</span></div>';
                });
            }
            
            result.innerHTML = html;
        }
    </script>
</body>
</html>
'''

@app.route('/')
def home():
    return render_template_string(HTML)

@app.route('/analyze')
def analyze_repo():
    repo = request.args.get('repo')
    if not repo:
        return jsonify({'error': 'repo parameter required'}), 400
    
    result = analyze(repo)
    
    return jsonify({
        'repo': result.repo_path,
        'branch': result.branch,
        'files_analyzed': result.files_analyzed,
        'unused_imports': [
            {'file': item.file, 'line': item.line, 'module': item.module}
            for item in result.unused_imports
        ]
    })

if __name__ == '__main__':
    app.run(debug=True)
