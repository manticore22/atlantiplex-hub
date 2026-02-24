from flask import Flask, jsonify
from datetime import datetime
import os

app = Flask(__name__)

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat()
    }), 200

@app.route('/api/status', methods=['GET'])
def status():
    return jsonify({
        'service': 'flask-backend',
        'status': 'running',
        'environment': os.getenv('FLASK_ENV'),
        'timestamp': datetime.utcnow().isoformat()
    }), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
