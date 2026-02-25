"""
ATLANTIPLEX STUDIO - NEURAL VISION INTEGRATION SCRIPT
Integrates the Neural Vision Plugin into the main Atlantiplex Studio
"""

import sqlite3
import sys
import os

def integrate_neural_vision():
    """Integrate Neural Vision plugin into Atlantiplex Studio"""
    
    # Database setup
    db_path = 'atlantiplex_studio.db'
    
    if not os.path.exists(db_path):
        print("❌ Atlantiplex Studio database not found!")
        print("Please run the main Atlantiplex Studio first to create the database.")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if plugins table exists, create if not
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS plugins (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                plugin_name TEXT UNIQUE NOT NULL,
                plugin_version TEXT NOT NULL,
                plugin_file TEXT NOT NULL,
                enabled BOOLEAN DEFAULT 1,
                settings TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Add Neural Vision plugin to database
        cursor.execute('''
            INSERT OR REPLACE INTO plugins (plugin_name, plugin_version, plugin_file, settings)
            VALUES (?, ?, ?, ?)
        ''', (
            'Neural Vision Filters',
            '1.0.0',
            'plugins/neural_vision_plugin.py',
            '{"webapp_url": "http://localhost:8080", "auto_start": false}'
        ))
        
        # Add plugin navigation to admin menu
        cursor.execute('''
            INSERT OR REPLACE INTO admin_menu (menu_item, route_path, icon, description, enabled)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            'Neural Vision Filters',
            '/admin/neural-vision',
            '🧠',
            'Advanced real-time laser eye filters with Matrix-style interface',
            1
        ))
        
        conn.commit()
        conn.close()
        
        print("✅ Neural Vision Plugin integrated successfully!")
        print("🚀 Features added:")
        print("   • Neural Vision Filters admin panel")
        print("   • 8 advanced filter types (Dante, Virgil, Raiden, Thug Life, Glimmer, etc.)")
        print("   • Real-time filter activation")
        print("   • Webhook integration")
        print("   • Matrix-style UI")
        print("   • Connection testing and monitoring")
        print()
        print("📋 Next steps:")
        print("1. Restart Atlantiplex Studio")
        print("2. Login as admin (username: manticore)")
        print("3. Access Neural Vision from admin menu")
        print("4. Launch the web app from the control panel")
        
        return True
        
    except Exception as e:
        print(f"❌ Integration failed: {str(e)}")
        return False

def create_integration_script():
    """Create a Python script to integrate the plugin into existing Atlantiplex Studio"""
    
    integration_code = '''
"""
NEURAL VISION PLUGIN INTEGRATION
Add this code to your existing Atlantiplex Studio main file
"""

# Add this import at the top of your Atlantiplex Studio file
import sys
import os

# Add the plugin path
sys.path.append(os.path.join(os.path.dirname(__file__), 'plugins'))

# After your database setup and before app.run(), add this:
def init_plugins():
    """Initialize all plugins"""
    try:
        # Initialize Neural Vision plugin
        from neural_vision_plugin import init_neural_vision_plugin
        
        # Connect to database
        conn = sqlite3.connect('atlantiplex_studio.db')
        
        # Initialize the plugin
        neural_vision_plugin = init_neural_vision_plugin(app, conn)
        
        print("✅ Neural Vision Plugin loaded successfully")
        conn.close()
        
    except ImportError as e:
        print("⚠️ Neural Vision Plugin not found:", str(e))
    except Exception as e:
        print("⚠️ Failed to load Neural Vision Plugin:", str(e))

# Call this function after your app configuration
init_plugins()

# Add this session info endpoint if it doesn't exist:
@app.route('/api/session-info')
def get_session_info():
    """Get current session information"""
    if 'username' not in session:
        return jsonify({'success': False, 'message': 'Not logged in'})
    
    return jsonify({
        'success': True,
        'username': session['username'],
        'role': session.get('role', 'user'),
        'login_time': session.get('login_time', 'Unknown')
    })
'''
    
    with open('neural_vision_integration.py', 'w') as f:
        f.write(integration_code)
    
    print("📄 Created 'neural_vision_integration.py' with integration code")
    print("📝 Add the contents to your main Atlantiplex Studio file")

def create_launcher_script():
    """Create a launcher script for the complete system"""
    
    launcher_code = '''
"""
ATLANTIPLEX STUDIO + NEURAL VISION LAUNCHER
Launch both systems together for complete integration
"""

import subprocess
import webbrowser
import time
import sys
import os

def launch_systems():
    """Launch Atlantiplex Studio and Neural Vision Web App"""
    
    print("🚀 Starting Atlantiplex Studio + Neural Vision System...")
    print("=" * 60)
    
    # Launch Neural Vision Web App first
    print("🧠 Launching Neural Vision Web App...")
    neural_vision_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', '..', 'index.html')
    
    if os.path.exists(neural_vision_path):
        try:
            # Start a simple HTTP server for the Neural Vision app
            import http.server
            import socketserver
            import threading
            
            PORT = 8080
            
            class NVHandler(http.server.SimpleHTTPRequestHandler):
                def __init__(self, *args, **kwargs):
                    super().__init__(*args, directory=os.path.dirname(neural_vision_path), **kwargs)
            
            def start_nv_server():
                with socketserver.TCPServer(("", PORT), NVHandler) as httpd:
                    print(f"✅ Neural Vision running at: http://localhost:{PORT}")
                    httpd.serve_forever()
            
            # Start Neural Vision server in a thread
            nv_thread = threading.Thread(target=start_nv_server, daemon=True)
            nv_thread.start()
            
            time.sleep(2)  # Give it time to start
            
        except Exception as e:
            print(f"⚠️ Failed to start Neural Vision server: {e}")
            print("💡 You can still open index.html manually in a browser")
    
    # Launch Atlantiplex Studio
    print("🎬 Launching Atlantiplex Studio...")
    studio_path = os.path.join(os.path.dirname(__file__), 'atlantiplex_studio.py')
    
    if os.path.exists(studio_path):
        try:
            # Run in the background
            subprocess.Popen([sys.executable, studio_path], 
                           cwd=os.path.dirname(studio_path))
            print("✅ Atlantiplex Studio starting...")
        except Exception as e:
            print(f"❌ Failed to launch Atlantiplex Studio: {e}")
            return
    
    # Open browser
    time.sleep(3)
    webbrowser.open('http://localhost:5000/login')
    
    print("=" * 60)
    print("🎯 SYSTEM ACTIVE!")
    print("📱 Atlantiplex Studio: http://localhost:5000")
    print("🧠 Neural Vision App: http://localhost:8080")
    print("👤 Admin Login: username=manticore, password=patriot8812")
    print("=" * 60)
    print("Press Ctrl+C to stop")

if __name__ == "__main__":
    try:
        launch_systems()
        
        # Keep the script running
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\\n🛑 Shutting down systems...")
        sys.exit(0)
'''
    
    with open('launch_complete_system.py', 'w') as f:
        f.write(launch_code)
    
    print("🚀 Created 'launch_complete_system.py' for launching both systems")

if __name__ == "__main__":
    print("🧠 ATLANTIPLEX STUDIO - NEURAL VISION INTEGRATION")
    print("=" * 60)
    
    choice = input("Choose integration method:\\n"
                   "1. Automatic integration (modifies database)\\n"
                   "2. Create integration code file\\n"
                   "3. Create launcher script\\n"
                   "4. All of the above\\n"
                   "Choice (1-4): ")
    
    if choice == '1':
        integrate_neural_vision()
    elif choice == '2':
        create_integration_script()
    elif choice == '3':
        create_launcher_script()
    elif choice == '4':
        integrate_neural_vision()
        print()
        create_integration_script()
        print()
        create_launcher_script()
    else:
        print("Invalid choice")
        sys.exit(1)
    
    print("\\n✨ Integration complete! Enjoy your Neural Vision Filters! 🎯")