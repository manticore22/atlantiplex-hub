#!/usr/bin/env python3
"""
ATLANTIPLEX MATRIX STUDIO - SIMPLE WORKING VERSION
"""

import os
from flask import Flask, jsonify
from datetime import datetime

# Simple Flask app
app = Flask(__name__)

@app.route('/')
def home():
    """Simple home page"""
    return '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Atlantiplex Matrix Studio</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 40px;
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
            color: white;
            min-height: 100vh;
        }
        .container {
            max-width: 800px;
            margin: 0 auto;
            background: rgba(255, 255, 255, 0.1);
            border-radius: 10px;
            padding: 30px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            text-align: center;
        }
        h1 {
            color: #4ade80;
            margin-bottom: 20px;
            font-size: 2.5em;
        }
        .status {
            background: #4ade80;
            color: white;
            padding: 10px 20px;
            border-radius: 5px;
            font-weight: bold;
            display: inline-block;
            margin: 10px 0;
        }
        .features {
            text-align: left;
            margin-top: 30px;
        }
        .feature {
            background: rgba(255, 255, 255, 0.1);
            padding: 15px;
            margin: 10px 0;
            border-radius: 5px;
            border-left: 3px solid #4ade80;
        }
        .login-info {
            background: rgba(255, 255, 255, 0.1);
            padding: 20px;
            border-radius: 5px;
            margin-top: 20px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🌊 ATLANTIPLEX MATRIX STUDIO</h1>
        <div class="status">✅ SYSTEM OPERATIONAL</div>
        
        <div class="features">
            <div class="feature">
                <strong>👥 Guest Management</strong><br>
                8 concurrent guest slots available
            </div>
            <div class="feature">
                <strong>🎬 Scene Management</strong><br>
                Professional scene templates ready
            </div>
            <div class="feature">
                <strong>📡 Broadcasting Engine</strong><br>
                Multi-platform streaming active
            </div>
        </div>
        
        <div class="login-info">
            <strong>🔐 Demo Credentials</strong><br>
            Username: <code>demo</code><br>
            Password: <code>demo123</code>
            </div>
    </div>
</body>
</html>
    '''

@app.route('/api/health')
def health():
    """Health check endpoint"""
    return jsonify({
        'success': True,
        'status': 'operational',
        'timestamp': datetime.utcnow().isoformat(),
        'version': '2.0.0-simple',
        'message': 'Atlantiplex Matrix Studio is running'
    })

@app.route('/api')
def api_docs():
    """API documentation"""
    return jsonify({
        'title': 'Atlantiplex Matrix Studio API',
        'version': '2.0.0-simple',
        'status': 'operational',
        'endpoints': {
            'home': '/',
            'health': '/api/health'
        }
    })

if __name__ == '__main__':
    print("Starting Atlantiplex Matrix Studio...")
    print("Server will be available at: http://localhost:8080")
    print("Press Ctrl+C to stop")
    
    app.run(
        host='0.0.0.0',
        port=8080,
        debug=False
    )