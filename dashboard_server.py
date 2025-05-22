from flask import Flask, send_from_directory
import os

app = Flask(__name__, static_folder=".", static_url_path="")

@app.route('/')
def index():
    # Serve index.html if available
    if os.path.exists('index.html'):
        return app.send_static_file('index.html')
    return '<h1>Capsule Dashboard</h1>'

@app.route('/<path:filename>')
def static_files(filename):
    # Serve any other static file in the repository directory
    if os.path.exists(filename):
        return send_from_directory('.', filename)
    return '', 404

if __name__ == '__main__':
    port = int(os.environ.get('DASHBOARD_PORT', 8686))
    app.run(host='0.0.0.0', port=port)
