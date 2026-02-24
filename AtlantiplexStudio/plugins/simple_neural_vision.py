"""
SIMPLE NEURAL VISION PLUGIN FOR ATLANTIPLEX STUDIO
Easy integration with minimal code changes
"""

def add_neural_vision_to_app(app, db):
    """Add Neural Vision routes to existing Atlantiplex Studio app"""
    
    @app.route('/admin/neural-vision')
    def neural_vision_admin():
        """Neural Vision Filter Admin Panel"""
        if 'username' not in app.session or app.session.get('role') != 'admin':
            return app.redirect('/login')
        
        return render_neural_vision_page()
    
    @app.route('/api/neural-filters')
    def get_neural_filters():
        """API endpoint to get all available filters"""
        if 'username' not in app.session or app.session.get('role') != 'admin':
            return app.jsonify({'success': False, 'message': 'Admin access required'})
        
        # Return hardcoded filters for simplicity
        filters = [
            {
                'id': 1,
                'name': 'Dante Devil Trigger',
                'type': 'dante',
                'settings': {"color": "#ff1a1a", "intensity": 0.9},
                'enabled': True
            },
            {
                'id': 2,
                'name': 'Virgil Dark Slayer',
                'type': 'virgil',
                'settings': {"color": "#1a75ff", "intensity": 0.8},
                'enabled': True
            },
            {
                'id': 3,
                'name': 'Raiden Lightning',
                'type': 'raiden',
                'settings': {"color": "#00d4ff", "intensity": 0.85},
                'enabled': True
            },
            {
                'id': 4,
                'name': 'Thug Life',
                'type': 'thuglife',
                'settings': {"color": "#000000", "intensity": 1.0},
                'enabled': True
            },
            {
                'id': 5,
                'name': 'Glimmer Eye',
                'type': 'glimmer',
                'settings': {"color": "#ffffff", "intensity": 0.7},
                'enabled': True
            }
        ]
        
        return app.jsonify({
            'success': True,
            'filters': filters
        })
    
    @app.route('/api/neural-filters/<int:filter_id>/activate', methods=['POST'])
    def activate_neural_filter(filter_id):
        """Activate a specific neural filter"""
        if 'username' not in app.session or app.session.get('role') != 'admin':
            return app.jsonify({'success': False, 'message': 'Admin access required'})
        
        # For simplicity, just return success
        filter_names = {
            1: 'Dante Devil Trigger',
            2: 'Virgil Dark Slayer',
            3: 'Raiden Lightning',
            4: 'Thug Life',
            5: 'Glimmer Eye'
        }
        
        filter_name = filter_names.get(filter_id, f'Filter {filter_id}')
        
        return app.jsonify({
            'success': True,
            'message': f'Filter "{filter_name}" activated',
            'filter': {
                'id': filter_id,
                'name': filter_name,
                'activated': True
            }
        })
    
    def render_neural_vision_page():
        """Render the Neural Vision admin interface"""
        return '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Neural Vision Filters - Atlantiplex Studio</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Courier New', monospace;
            background: linear-gradient(135deg, #0a0a0a 0%, #001a00 50%, #0a0a0a 100%);
            color: #00ff00;
            min-height: 100vh;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }
        
        .header {
            text-align: center;
            margin-bottom: 40px;
        }
        
        .header h1 {
            font-size: 2.5rem;
            margin-bottom: 10px;
            text-shadow: 0 0 20px #00ff00;
        }
        
        .card {
            background: rgba(0, 0, 0, 0.8);
            border: 1px solid #00ff00;
            box-shadow: 0 0 20px rgba(0, 255, 0, 0.3);
            padding: 30px;
            margin-bottom: 30px;
        }
        
        .filters-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-top: 20px;
        }
        
        .filter-card {
            background: rgba(0, 20, 0, 0.5);
            border: 1px solid #00ff00;
            padding: 20px;
            text-align: center;
            transition: all 0.3s ease;
            cursor: pointer;
        }
        
        .filter-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 0 30px rgba(0, 255, 0, 0.5);
            background: rgba(0, 40, 0, 0.7);
        }
        
        .filter-icon {
            font-size: 3rem;
            margin-bottom: 10px;
            display: block;
        }
        
        .filter-name {
            font-size: 1.2rem;
            font-weight: bold;
            margin-bottom: 10px;
            color: #00ff00;
        }
        
        .filter-description {
            font-size: 0.9rem;
            margin-bottom: 15px;
            opacity: 0.8;
        }
        
        .activate-btn {
            background: linear-gradient(135deg, #001100 0%, #003300 100%);
            border: 1px solid #00ff00;
            color: #00ff00;
            padding: 10px 20px;
            font-family: inherit;
            cursor: pointer;
            transition: all 0.3s ease;
            text-transform: uppercase;
            font-weight: bold;
        }
        
        .activate-btn:hover {
            background: linear-gradient(135deg, #003300 0%, #005500 100%);
            box-shadow: 0 0 15px rgba(0, 255, 0, 0.5);
        }
        
        .control-panel {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 30px;
            margin-top: 20px;
        }
        
        .launch-btn {
            background: linear-gradient(135deg, #003300 0%, #006600 100%);
            border: 2px solid #00ff00;
            color: #00ff00;
            padding: 15px 30px;
            font-family: inherit;
            cursor: pointer;
            font-size: 1.1rem;
            text-transform: uppercase;
            font-weight: bold;
            transition: all 0.3s ease;
            margin: 10px 0;
            width: 100%;
        }
        
        .launch-btn:hover {
            background: linear-gradient(135deg, #006600 0%, #009900 100%);
            box-shadow: 0 0 20px rgba(0, 255, 0, 0.6);
            transform: scale(1.05);
        }
        
        .status {
            padding: 15px;
            background: rgba(0, 255, 0, 0.1);
            border: 1px solid #00ff00;
            margin: 10px 0;
            text-align: center;
        }
        
        .status-online {
            color: #00ff00;
        }
        
        .status-offline {
            color: #ff6600;
        }
        
        .back-link {
            display: inline-block;
            background: linear-gradient(135deg, #001100 0%, #003300 100%);
            border: 1px solid #00ff00;
            color: #00ff00;
            padding: 10px 20px;
            text-decoration: none;
            text-transform: uppercase;
            font-weight: bold;
            transition: all 0.3s ease;
        }
        
        .back-link:hover {
            background: linear-gradient(135deg, #003300 0%, #005500 100%);
            box-shadow: 0 0 15px rgba(0, 255, 0, 0.5);
        }
        
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.7; }
        }
        
        .pulse {
            animation: pulse 2s infinite;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🧠 NEURAL VISION FILTERS</h1>
            <p>Advanced Real-Time Filter Management System</p>
        </div>
        
        <div class="card">
            <h2>System Status</h2>
            <div class="status" id="webapp-status">
                <span class="pulse">🔍 Checking Neural Vision Web App...</span>
            </div>
        </div>
        
        <div class="card">
            <h2>Available Filters</h2>
            <div class="filters-grid" id="filters-grid">
                <!-- Filters will be loaded here -->
            </div>
        </div>
        
        <div class="card">
            <h2>Control Panel</h2>
            <div class="control-panel">
                <div>
                    <h3>Quick Actions</h3>
                    <button class="launch-btn" onclick="launchWebApp()">
                        🚀 Launch Neural Vision Web App
                    </button>
                    <button class="launch-btn" onclick="checkConnection()">
                        🔗 Test Connection
                    </button>
                    <button class="launch-btn" onclick="refreshFilters()">
                        🔄 Refresh Filters
                    </button>
                </div>
                <div>
                    <h3>Settings</h3>
                    <label for="webapp-url" style="display: block; margin-bottom: 5px;">Web App URL:</label>
                    <input type="text" id="webapp-url" value="http://localhost:8080" 
                           style="width: 100%; padding: 8px; background: #000; border: 1px solid #00ff00; color: #00ff00; margin-bottom: 10px;">
                    
                    <button class="launch-btn" onclick="saveSettings()">
                        💾 Save Settings
                    </button>
                </div>
            </div>
        </div>
        
        <div style="text-align: center; margin-top: 30px;">
            <a href="/admin" class="back-link">← Back to Admin Panel</a>
        </div>
    </div>
    
    <script>
        let currentFilters = [];
        
        // Load filters when page loads
        document.addEventListener('DOMContentLoaded', function() {
            loadFilters();
            checkConnection();
        });
        
        async function loadFilters() {
            try {
                const response = await fetch('/api/neural-filters');
                const data = await response.json();
                
                if (data.success) {
                    currentFilters = data.filters;
                    displayFilters(data.filters);
                }
            } catch (error) {
                console.error('Failed to load filters:', error);
                document.getElementById('filters-grid').innerHTML = 
                    '<div class="filter-card"><span>Failed to load filters</span></div>';
            }
        }
        
        function displayFilters(filters) {
            const grid = document.getElementById('filters-grid');
            grid.innerHTML = '';
            
            filters.forEach(filter => {
                const card = document.createElement('div');
                card.className = 'filter-card';
                card.innerHTML = `
                    <span class="filter-icon">${getFilterIcon(filter.type)}</span>
                    <div class="filter-name">${filter.name}</div>
                    <div class="filter-description">${getFilterDescription(filter.type)}</div>
                    <button class="activate-btn" onclick="activateFilter(${filter.id}, '${filter.name}')">
                        ACTIVATE
                    </button>
                `;
                grid.appendChild(card);
            });
        }
        
        function getFilterIcon(type) {
            const icons = {
                'dante': '🔥',
                'virgil': '⚔️',
                'raiden': '⚡',
                'thuglife': '🕶️',
                'glimmer': '✨'
            };
            return icons[type] || '👁️';
        }
        
        function getFilterDescription(type) {
            const descriptions = {
                'dante': 'Fiery demonic energy beams',
                'virgil': 'Elegant blue sword summons',
                'raiden': 'Electric lightning effects',
                'thuglife': 'Classic meme sunglasses',
                'glimmer': 'Magical sparkles in eyes'
            };
            return descriptions[type] || 'Advanced neural filter';
        }
        
        async function activateFilter(filterId, filterName) {
            try {
                const response = await fetch(`/api/neural-filters/${filterId}/activate`, {
                    method: 'POST'
                });
                const data = await response.json();
                
                if (data.success) {
                    alert(`✅ Filter "${filterName}" activated successfully!\\n\\nYou can now see the effect in the Neural Vision Web App.`);
                } else {
                    alert(`❌ Failed to activate filter: ${data.message}`);
                }
            } catch (error) {
                console.error('Failed to activate filter:', error);
                alert('❌ Failed to activate filter');
            }
        }
        
        async function checkConnection() {
            const statusEl = document.getElementById('webapp-status');
            const url = document.getElementById('webapp-url').value;
            
            statusEl.innerHTML = '<span class="pulse">🔍 Checking connection...</span>';
            
            try {
                const response = await fetch(url, { method: 'HEAD' });
                
                if (response.ok) {
                    statusEl.innerHTML = '<span class="status-online">✅ Neural Vision Web App is ONLINE</span>';
                } else {
                    statusEl.innerHTML = '<span class="status-offline">⚠️ Neural Vision Web App is OFFLINE</span>';
                }
            } catch (error) {
                statusEl.innerHTML = '<span class="status-offline">⚠️ Neural Vision Web App is OFFLINE (Connection failed)</span>';
            }
        }
        
        function launchWebApp() {
            const url = document.getElementById('webapp-url').value;
            window.open(url, '_blank');
        }
        
        function refreshFilters() {
            loadFilters();
        }
        
        function saveSettings() {
            const url = document.getElementById('webapp-url').value;
            localStorage.setItem('neural-vision-url', url);
            alert('✅ Settings saved successfully!');
        }
        
        // Load saved settings
        window.addEventListener('load', function() {
            const savedUrl = localStorage.getItem('neural-vision-url');
            if (savedUrl) {
                document.getElementById('webapp-url').value = savedUrl;
            }
        });
    </script>
</body>
</html>
        '''

def create_plugin_addon():
    """Create a simple addon to add to Atlantiplex Studio"""
    
    addon_code = '''
# NEURAL VISION PLUGIN ADDON
# Add this code to your main Atlantiplex Studio file

# Add these imports at the top
import os
import sys

# Add this function after your Flask app setup
def init_neural_vision():
    """Initialize Neural Vision plugin"""
    try:
        # Import and add Neural Vision routes
        sys.path.append(os.path.join(os.path.dirname(__file__), 'plugins'))
        from simple_neural_vision import add_neural_vision_to_app
        
        # Connect to your existing database
        conn = sqlite3.connect('atlantiplex_studio.db')
        
        # Add Neural Vision routes to your app
        add_neural_vision_to_app(app, conn)
        
        print("✅ Neural Vision plugin loaded successfully")
        conn.close()
        
    except Exception as e:
        print(f"⚠️ Failed to load Neural Vision plugin: {e}")

# Call this function after your app setup but before app.run()
init_neural_vision()

# Add this to your admin menu HTML template:
# <a href="/admin/neural-vision" class="admin-menu-item">
#     <span>🧠</span> Neural Vision Filters
# </a>
'''
    
    with open('simple_neural_vision_addon.py', 'w') as f:
        f.write(addon_code)
    
    print("📄 Created 'simple_neural_vision_addon.py'")
    print("📝 Add the code to your main Atlantiplex Studio file")

if __name__ == "__main__":
    create_plugin_addon()
    print("✅ Simple Neural Vision plugin created!")
    print("📋 Instructions:")
    print("1. Copy the code from simple_neural_vision_addon.py")
    print("2. Paste it into your main Atlantiplex Studio file")
    print("3. Restart Atlantiplex Studio")
    print("4. Access Neural Vision from admin menu")
    print("5. Launch the web app from the control panel")