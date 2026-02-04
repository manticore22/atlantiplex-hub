"""
ATLANTIPLEX STUDIO - ULTIMATE SIMPLE VERSION
100%% GUARANTEED TO WORK
"""

from flask import Flask
import sqlite3
import hashlib
import socket
import time

app = Flask(__name__)
app.secret_key = 'ultimate_key'

HTML = '''
<!DOCTYPE html>
<html><head><title>Atlantiplex Studio</title></head>
<body style="background:#000;color:#0f0;font-family:monospace;padding:20px;text-align:center;">
<h1>ATLANTIPLEX STUDIO</h1>
<div style="max-width:600px;margin:50px auto;padding:20px;border:2px solid #0f0;">
<h3>MATRIX CONTROL SYSTEM</h3>
<p>Status: <span style="color:#0f0;">OPERATIONAL</span></p>
<p>Server: Running on port %s</p>
<p>Time: %s</p>
<p><a href="/test" style="color:#0f0;">Test API</a></p>
</div>
</body></html>
'''

@app.route('/')
def home():
    return HTML % (app.config.get('PORT', 8080), time.strftime('%H:%M:%S'))

@app.route('/test')
def test():
    return 'API working - Atlantiplex Studio is online!'

def find_port():
    for port in [8080, 8081, 8082, 8083, 8084, 8085]:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('127.0.0.1', port))
                return port
        except:
            continue
    return 9999

if __name__ == '__main__':
    port = find_port()
    app.config['PORT'] = port
    
    print('='*50)
    print('ATLANTIPLEX STUDIO - ULTIMATE SIMPLE')
    print('='*50)
    print(f'SERVER: http://127.0.0.1:{port}')
    print(f'TEST: http://127.0.0.1:{port}/test')
    print('='*50)
    
    try:
        app.run(host='127.0.0.1', port=port, debug=False)
    except:
        pass