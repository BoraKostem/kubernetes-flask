#!/usr/bin/env python3
from flask import Flask

app = Flask(__name__)

@app.route('/')
def main_page():
    return 'An awesome Kubernetes app with Flask!'

@app.route('/api')
def api_page():
    return 'API Page'

@app.route('/health')
def health_page():
    return 'Healthy', 200

if __name__ == '__main__':
    app.run(debug=True)
