"""
ATLANTIPLEX MATRIX STUDIO - DEBUG LOGIN VERSION
"""

from flask import Flask, request, session, redirect, url_for
import sqlite3
import hashlib

app = Flask(__name__)
app.secret_key = 'debug_key_123'

def get_db():
    conn = sqlite3.connect('matrix_studio.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def home():
    return "DEBUG HOME - <a href='/login'>Login</a> | <a href='/check_db'>Check Database</a>"

@app.route('/check_db')
def check_db():
    conn = get_db()
    users = conn.execute('SELECT username, password_hash FROM users').fetchall()
    conn.close()
    
    result = "Users in database:<br>"
    for user in users:
        expected = hashlib.sha256('patriot8812'.encode()).hexdigest()
        match = "✓ MATCH" if user['password_hash'] == expected else "✗ NO MATCH"
        result += f"Username: {user['username']}, Hash: {user['password_hash']} {match}<br>"
    
    return result

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return '''
        <form method="post">
            Username: <input name="username" value="manticore"><br>
            Password: <input name="password" type="password" value="patriot8812"><br>
            <input type="submit" value="Login">
        </form>
        '''
    
    username = request.form.get('username')
    password = request.form.get('password')
    
    if not username or not password:
        return f"Missing username or password. Got: username='{username}', password='{password}'"
    
    conn = get_db()
    user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
    conn.close()
    
    if not user:
        return f"No user found with username: {username}"
    
    input_hash = hashlib.sha256(password.encode()).hexdigest()
    stored_hash = user['password_hash']
    
    debug_info = f"""
    DEBUG INFO:<br>
    Username: {username}<br>
    Input Password: {password}<br>
    Input Hash: {input_hash}<br>
    Stored Hash: {stored_hash}<br>
    Hashes Match: {input_hash == stored_hash}<br>
    """
    
    if input_hash == stored_hash:
        session['user_id'] = user['id']
        session['username'] = user['username']
        return "LOGIN SUCCESSFUL! " + debug_info + "<br><a href='/'>Home</a>"
    else:
        return "LOGIN FAILED! " + debug_info + "<br><a href='/login'>Try Again</a>"

if __name__ == '__main__':
    print("DEBUG LOGIN SERVER - http://localhost:8081")
    app.run(host='0.0.0.0', port=8081, debug=True)