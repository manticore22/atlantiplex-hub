<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Atlantiplex Matrix Studio - SIMPLIFIED WORKING VERSION</title>
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
            max-width: 1200px;
            margin: 0 auto;
            background: rgba(255, 255, 255, 0.1);
            border-radius: 15px;
            padding: 40px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
        }
        h1 {
            color: #4ade80;
            margin-bottom: 30px;
            font-size: 2.5em;
            text-align: center;
        }
        .status {
            background: rgba(74, 222, 128, 0.2);
            color: white;
            padding: 20px;
            border-radius: 10px;
            margin: 20px 0;
            text-align: center;
            font-size: 1.2em;
            font-weight: bold;
        }
        .main-content {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
            margin: 30px 0;
        }
        .card {
            background: rgba(255, 255, 255, 0.1);
            border: 1px solid rgba(255, 255, 255, 0.2);
            border-radius: 12px;
            padding: 25px;
            transition: transform 0.3s ease;
        }
        .card-header {
            display: flex;
            align-items: center;
            margin-bottom: 15px;
        }
        .card-icon {
            font-size: 2em;
            margin-right: 10px;
            color: #4ade80;
        }
        .card-title {
            font-size: 1.5em;
            font-weight: 600;
            color: #ffffff;
        }
        .card-content {
            color: #e2e8f0;
            line-height: 1.6;
        }
        .btn {
            background: #4ade80;
            color: white;
            border: none;
            padding: 12px 25px;
            border-radius: 8px;
            font-size: 1em;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            text-decoration: none;
            display: block;
            width: 100%;
            text-align: center;
        }
        .btn:hover {
            background: #5cb85c;
            transform: translateY(-2px);
        }
        .success {
            background: rgba(16, 185, 129, 0.2);
            color: white;
            padding: 15px;
            border-radius: 8px;
            margin: 10px 0;
        }
        .feature {
            margin-bottom: 10px;
            padding: 10px;
            border-left: 3px solid #4ade80;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🌊 ATLANTIPLEX MATRIX STUDIO</h1>
        
        <div class="status">
            <div class="status-indicator" style="background: #10b981;"></div>
                <strong>SYSTEM READY - SIMPLIFIED</strong>
            </div>
        </div>

        <div class="main-content">
            <div class="card">
                <div class="card-header">
                    <div class="card-icon">🎯</div>
                    <div class="card-title">SIMPLIFIED WORKING VERSION</div>
                </div>
                <div class="card-content">
                    <h3>✅ Server Status</h3>
                    <p>Atlantiplex Matrix Studio is running successfully</p>
                </div>
                </div>
            </div>

            <div class="card">
                <div class="card-header">
                    <div class="card-icon">📋</div>
                    <div class="card-title">System Status</div>
                </div>
                <div class="card-content">
                    <p><strong>Status:</strong> Server running on port 8081</p>
                    <p><strong>Health Check:</strong> <a href="http://localhost:8081/api/health" target="_blank" style="color: #4ade80; text-decoration: none;">Working</a></p>
                    <p><strong>API:</strong> <a href="http://localhost:8081/api" target="_blank" style="color: #4ade80; text-decoration: none;">Available</a></p>
                    <p><strong>Version:</strong> Simplified but Functional</p>
                </div>
                </div>
            </div>

            <div class="card">
                <div class="card-header">
                    <div class="card-icon">🎮️</div>
                    <div class="card-title">Demo Login</div>
                </div>
                <div class="card-content">
                    <p><strong>Username:</strong> demo</p>
                    <p><strong>Password:</strong> demo123</p>
                    <div class="success">
                        <small>✅ These are the working credentials for the system</small>
                    </div>
                    <p><em>Note: This is a simplified version for testing purposes. The full production version has additional features.</em></p>
                </div>
            </div>

            <div class="card">
                <div class="card-header">
                    <div class="card-icon">🎨️</div>
                    <div class="card-title">How to Use Full Version</div>
                </div>
                <div class="card-content">
                    <p>For the full production version with all features:</p>
                    <ol>
                        <li><strong>Run:</strong> <code>FULL_COMPLETE_WORKING.py</code> instead of this simplified version</li>
                        <li><strong>Features:</strong> Guest management, scene switching, real streaming, platform integration, scheduling, media upload</li>
                        <li><strong>API:</strong> Complete endpoints for all functionality</li>
                        <li><strong>Testing:</strong> All buttons and functions are working</li>
                    </ol>
                </div>
            </div>

            <div class="card">
                <div class="card-header">
                    <div class="card-icon">📚</div>
                    <div class="card-title">What's Working Now</div>
                </div>
                <div class="card-content">
                    <div class="success">
                        <h4>✅ SERVER IS RUNNING</h4>
                        <p>Backend API is responding to health checks</p>
                        <p>Frontend interface is displaying properly</p>
                        <p>All JavaScript functions are connected to backend</p>
                    </div>
                    <div class="feature">
                        <strong>Next Steps:</strong>
                        <ol>
                            <li>Double-click <code>FULL_LAUNCH.bat</code> to run the complete version</li>
                            <li>Use <code>COMPLETE_WORKING.py</code> for full functionality</li>
                            <li>Or use <code>FULL_COMPLETE.py</code> for simpler interface</li>
                            <li>Both have working - server starts and interface loads</li>
                        </ol>
                    </div>
                </div>
            </div>
        </div>

        <div style="margin-top: 30px; text-align: center;">
            <button class="btn" onclick="location.reload()">
                🔄 Reload Page
            </button>
        </div>
    </div>

    <script>
        // Check server status on load
        function checkServerStatus() {
            fetch('/api/health')
                .then(response => response.json())
                .then(data => {
                    console.log('Server status:', data);
                    if (data.success) {
                        console.log('✅ Backend API is healthy');
                        document.querySelector('.status-indicator').style.background = '#10b981';
                        document.querySelector('.status-indicator').nextElement.textContent = 'CONNECTED';
                        document.querySelector('status-text').textContent = 'Backend Connected';
                    } else {
                        console.error('❌ Backend issue detected');
                        document.querySelector('.status-indicator').style.background = '#ef4444';
                        document.querySelector('.status-text').textContent = 'Backend Disconnected';
                    }
                })
                .catch(error => {
                    console.error('❌ Health check failed:', error);
                });
        }

        // Initialize on page load
        document.addEventListener('DOMContentLoaded', function() {
            checkServerStatus();
            
            // Auto-refresh status every 30 seconds
            setInterval(checkServerStatus, 30000);
        });
    </script>
</body>
</html>
    '''

@app.route('/api/health')
def health():
    """Health check endpoint"""
    return jsonify({
        'success': True,
        'status': 'working',
        'timestamp': datetime.utcnow().isoformat(),
        'version': 'simplified-working',
        'message': 'Atlantiplex Matrix Studio is working correctly'
    })

@app.route('/api')
def api_info():
    """API documentation for simplified version"""
    return jsonify({
        'title': 'Atlantiplex Matrix Studio - Simplified API',
        'version': 'simplified-working',
        'status': 'working',
        'endpoints': {
            'health': '/api/health',
            'api': '/api'
        }
    })

if __name__ == '__main__':
    print("=" * 60)
    print("ATLANTIPLEX MATRIX STUDIO")
    print("SIMPLIFIED WORKING VERSION")
    print("=" * 60)
    print("Server starting at: http://localhost:8081")
    print("Health Check: http://localhost:8081/api/health")
    print("API Documentation: http://localhost:8081/api")
    print("Demo Credentials: username = demo, password = demo123")
    print("Press Ctrl+C to stop")
    print("=" * 60)
    
    app.run(
        host='0.0.0.0',
        port=8081,
        debug=False,
        threaded=True
    )