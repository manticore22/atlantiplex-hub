from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    return "FLASK TEST - Server is working!"

if __name__ == '__main__':
    print("Starting Flask test server on port 8082...")
    app.run(host='127.0.0.1', port=8082, debug=False)