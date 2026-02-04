#!/usr/bin/env python3
"""
Simple test to check if templates are working
"""

import os
from flask import Flask, render_template

# Get the absolute path to templates
template_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'web', 'templates'))
print(f"Template directory: {template_dir}")
print(f"Template directory exists: {os.path.exists(template_dir)}")
print(f"Templates in directory: {os.listdir(template_dir) if os.path.exists(template_dir) else 'Directory not found'}")

# Create test app
app = Flask(__name__, template_folder=template_dir)

@app.route('/test')
def test_template():
    try:
        return render_template('unified_studio.html')
    except Exception as e:
        return f"Template error: {e}"

@app.route('/test-list')
def test_list():
    try:
        templates = os.listdir(template_dir)
        return f"Available templates: {templates}"
    except Exception as e:
        return f"Directory error: {e}"

if __name__ == '__main__':
    print("Test server on http://localhost:8081")
    print("Test routes:")
    print("  http://localhost:8081/test - Test template rendering")
    print("  http://localhost:8081/test-list - List templates")
    app.run(port=8081, debug=True)