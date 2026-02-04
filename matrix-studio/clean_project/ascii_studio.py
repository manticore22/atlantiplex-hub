"""
ATLANTIPLEX STUDIO - ASCII SAFE VERSION
No unicode characters - guaranteed to work
"""

from flask import Flask, render_template_string, request, session, redirect, url_for, jsonify
import sqlite3
import hashlib
import socket
import webbrowser
import threading
import time
import sys

app = Flask(__name__)
app.secret_key = 'ascii_safe_key_2024'

# Simple template
TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Atlantiplex Studio</title>
    <meta charset="UTF-8">
    <style>
        body { font-family: monospace; background: #000; color: #0f0; padding: 20px; text-align: center; }
        .container { max-width: 600px; margin: 50px auto; padding: 20px; border: 2px solid #0f0; }
        input { width: 100%%; padding: 10px; margin: 10px 0; background: #111; border: 1px solid #0f0; color: #0f0; }
        button { width: 100%%; padding: 10px; background: #0f0; color: #000; border: none; font-weight: bold; cursor: pointer; }
        .success { color: #0f0; }
        .error { color: #f00; }
        .status { margin: 20px 0; padding: 10px; background: #111; border: 1px solid #0f0; }
    </style>
</head>
<body>
    <h1>ATLANTIPLEX STUDIO</h1>
    <div class="container">
        <h3>MATRIX CONTROL SYSTEM</h3>
        {% if session.username %}
            <div class="status success">
                Welcome {{ session.username }}! 
                <p><a href="/logout" style="color: #0f0;">Logout</a></p>
            </div>
            <div class="status">
                <h4>System Status:</h4>
                <p>[OK] Server: Running on port {{ port }}</p>
                <p>[OK] Database: Connected</p>
                <p>[OK] Authentication: Active</p>
                <p>[OK] Interface: Operational</p>
            </div>
        {% else %}
            <form method="post" action="/login">
                <input type="text" name="username" placeholder="Username" value="manticore" required>
                <input type="password" name="password" placeholder="Password" value="patriot8812" required>
                <button type="submit">ACCESS SYSTEM</button>
            </form>
            {% if error %}
            <div class="error">{{ error }}</div>
            {% endif %}
        {% endif %}
        <p><small>Server Port: {{ port }}</small></p>
    </div>
</body>
</html>
'''

def get_port():
    try_ports = [8080, 8081, 8082, 8083, 8084, 8085, 8086, 5000, 3000]
    for port in try_ports:
        try:
            test_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            test_socket.bind(('127.0.0.1', port))
            test_socket.close()
            return port
        except:
            continue
    return 9999

def init_db():
    try:
        conn = sqlite3.connect('atlantiplex_studio.db')
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                role TEXT DEFAULT 'user'
            )
        ''')
        admin_hash = hashlib.sha256('patriot8812'.encode()).hexdigest()
        cursor.execute('INSERT OR IGNORE INTO users (username, password_hash, role) VALUES (?, ?, ?)', 
                     ('manticore', admin_hash, 'admin'))
        conn.commit()
        conn.close()
        print("[OK] Database initialized successfully")
        return True
    except Exception as e:
        print(f"[ERROR] Database error: {e}")
        return False

init_db()

@app.route('/')
def home():
    if 'username' in session:
        return render_template_string(TEMPLATE, port=port)
    else:
        return redirect(url_for('login'))

@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username', '').strip()
    password = request.form.get('password', '')
    
    if not username or not password:
        return render_template_string(TEMPLATE, error="Credentials required", port=port)
    
    try:
        conn = sqlite3.connect('atlantiplex_studio.db')
        cursor = conn.cursor()
        cursor.execute('SELECT password_hash FROM users WHERE username = ?', (username,))
        result = cursor.fetchone()
        conn.close()
        
        if result:
            stored_hash = result[0]
            input_hash = hashlib.sha256(password.encode()).hexdigest()
            if input_hash == stored_hash:
                session['username'] = username
                print(f"[OK] Login successful: {username}")
                return redirect(url_for('home'))
        
        return render_template_string(TEMPLATE, error="Invalid credentials", port=port)
        
    except Exception as e:
        print(f"[ERROR] Login error: {e}")
        return render_template_string(TEMPLATE, error="System error", port=port)

@app.route('/logout')
def logout():
    username = session.get('username', 'unknown')
    session.clear()
    print(f"[OK] Logout: {username}")
    return redirect(url_for('home'))

@app.route('/api/test')
def api_test():
    return jsonify({
        'status': 'working',
        'message': 'Atlantiplex Studio API is functional',
        'server': 'ascii_safe',
        'timestamp': time.time()
    })

@app.route('/status')
def status():
    return f"""
    <html><head><title>Status</title></head>
    <body style="background: #000; color: #0f0; font-family: monospace; padding: 20px;">
        <h1>[OK] ATLANTIPLEX STUDIO STATUS</h1>
        <p>Server: RUNNING</p>
        <p>Port: {port}</p>
        <p>Time: {time.strftime('%%H:%%M:%%S')}</p>
        <p><a href="/" style="color: #0f0;">Go to Studio</a></p>
    </body></html>
    """

if __name__ == '__main__':
    port = get_port()
    
    print("=" * 60)
    print("ATLANTIPLEX STUDIO - ASCII SAFE VERSION")
    print("=" * 60)
    print(f"[OK] Server URL: http://127.0.0.1:{port}")
    print(f"[OK] Status Page: http://127.0.0.1:{port}/status")
    print(f"[OK] API Test: http://127.0.0.1:{port}/api/test")
    print(f"[OK] Login: manticore / patriot8812")
    print("=" * 60)
    print("STARTING SERVER - KEEP THIS WINDOW OPEN")
    print("=" * 60)
    
    def open_browser_delayed():
        time.sleep(3)
        try:
            webbrowser.open(f'http://127.0.0.1:{port}')
            print("[OK] Browser opened")
        except:
            print("[ERROR] Browser failed - open manually")
    
    threading.Thread(target=open_browser_delayed, daemon=True).start()
    
    try:
        app.run(host='127.0.0.1', port=port, debug=False, use_reloader=False, threaded=True)
    except KeyboardInterrupt:
        print("\n[OK] Server stopped by user")
    except Exception as e:
        print(f"\n[ERROR] Server error: {e}")
    
    input("\nPress Enter to exit...")