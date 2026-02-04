from flask import Flask, request
import sqlite3
import hashlib
import socket

app = Flask(__name__)

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
    import time
    return HTML % (8080, time.strftime('%H:%M:%S'))

@app.route('/login')
def login():
    return '''
    <!DOCTYPE html><head><title>Login</title></head>
    <body style="background:#000;color:#0f0;font-family:monospace;padding:20px;text-align:center;">
    <h1>ATLANTIPLEX STUDIO - LOGIN</h1>
    <form method="post" action="/login">
        <input type="text" name="username" placeholder="Username" value="manticore" style="width:200px;padding:10px;margin:5px;background:#111;border:1px solid #0f0;color:#0f0;"><br>
        <input type="password" name="password" placeholder="Password" value="patriot8812" style="width:200px;padding:10px;margin:5px;background:#111;border:1px solid #0f0;color:#0f0;"><br>
        <button type="submit" style="background:#0f0;color:#000;border:none;padding:10px 20px;font-weight:bold;cursor:pointer;">LOGIN</button>
    </form>
    <p><a href="/" style="color:#0f0;">Back to Home</a></p>
    </body></html>
    '''

@app.route('/login', methods=['POST'])
def do_login():
    username = request.form.get('username')
    password = request.form.get('password')
    if username == 'manticore' and password == 'patriot8812':
        return '''
        <!DOCTYPE html><head><title>Dashboard</title></head>
        <body style="background:#000;color:#0f0;font-family:monospace;padding:20px;text-align:center;">
        <h1>WELCOME TO ATLANTIPLEX STUDIO!</h1>
        <h2>Login Successful!</h2>
        <p>User: ''' + username + '''</p>
        <p>Status: <span style="color:#0f0;">OPERATIONAL</span></p>
        <p><a href="/logout" style="color:#0f0;">Logout</a></p>
        </body></html>
        '''
    else:
        return '''
        <!DOCTYPE html><head><title>Login Failed</title></head>
        <body style="background:#000;color:#f00;font-family:monospace;padding:20px;text-align:center;">
        <h1>LOGIN FAILED</h1>
        <p>Invalid credentials</p>
        <p><a href="/login" style="color:#f00;">Try Again</a></p>
        </body></html>
        '''

@app.route('/logout')
def logout():
    return '''
    <!DOCTYPE html><head><title>Logged Out</title></head>
    <body style="background:#000;color:#0f0;font-family:monospace;padding:20px;text-align:center;">
    <h1>LOGGED OUT</h1>
    <p><a href="/login" style="color:#0f0;">Login Again</a></p>
    </body></html>
    '''

@app.route('/test')
def test():
    return 'API working - Atlantiplex Studio is online!'

if __name__ == '__main__':
    print('ATLANTIPLEX STUDIO STARTING...')
    print('URL: http://127.0.0.1:8080')
    print('TEST: http://127.0.0.1:8080/test')
    app.run(host='127.0.0.1', port=8080, debug=False)