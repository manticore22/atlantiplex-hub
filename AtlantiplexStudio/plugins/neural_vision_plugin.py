"""
ATLANTIPLEX STUDIO - NEURAL VISION FILTER PLUGIN
Integrates laser eye filters into the moderator menu
"""

class NeuralVisionPlugin:
    """Plugin for laser eye filters integration"""
    
    def __init__(self, app, db_connection):
        self.app = app
        self.db = db_connection
        self.plugin_version = "1.0.0"
        self.setup_plugin()
    
    def setup_plugin(self):
        """Initialize plugin and add routes"""
        self.create_plugin_tables()
        self.add_plugin_routes()
        self.add_plugin_settings()
    
    def create_plugin_tables(self):
        """Create necessary database tables for the plugin"""
        cursor = self.db.cursor()
        
        # Create neural filters table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS neural_filters (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filter_name TEXT UNIQUE NOT NULL,
                filter_type TEXT NOT NULL,
                settings TEXT NOT NULL,
                enabled BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create filter presets table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS filter_presets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                preset_name TEXT UNIQUE NOT NULL,
                filter_settings TEXT NOT NULL,
                created_by TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Insert default filters
        default_filters = [
            ('Dante Devil Trigger', 'dante', '{"color": "#ff1a1a", "intensity": 0.9, "aura": true}'),
            ('Virgil Dark Slayer', 'virgil', '{"color": "#1a75ff", "intensity": 0.8, "swords": true}'),
            ('Raiden Lightning', 'raiden', '{"color": "#00d4ff", "intensity": 0.85, "electric": true}'),
            ('Thug Life', 'thuglife', '{"color": "#000000", "intensity": 1.0, "glasses": true}'),
            ('Glimmer Eye', 'glimmer', '{"color": "#ffffff", "intensity": 0.7, "sparkles": true}'),
            ('Neon Red', 'red', '{"color": "#ff0000", "intensity": 0.8}'),
            ('Electric Blue', 'blue', '{"color": "#00bfff", "intensity": 0.8}'),
            ('Toxic Green', 'green', '{"color": "#00ff00", "intensity": 0.8}')
        ]
        
        cursor.executemany('''
            INSERT OR IGNORE INTO neural_filters (filter_name, filter_type, settings)
            VALUES (?, ?, ?)
        ''', default_filters)
        
        self.db.commit()
    
    def add_plugin_routes(self):
        """Add plugin-specific routes to the Flask app"""
        
        @self.app.route('/admin/neural-vision')
        def neural_vision_admin():
            """Neural Vision Filter Admin Panel"""
            if 'username' not in self.app.session or self.app.session.get('role') != 'admin':
                return self.app.redirect('/login')
            
            return self.render_neural_vision_admin()
        
        @self.app.route('/api/neural-filters')
        def get_neural_filters():
            """API endpoint to get all available filters"""
            if 'username' not in self.app.session or self.app.session.get('role') != 'admin':
                return self.app.jsonify({'success': False, 'message': 'Admin access required'})
            
            try:
                cursor = self.db.cursor()
                filters = cursor.execute('SELECT * FROM neural_filters WHERE enabled = 1').fetchall()
                
                filter_list = []
                for filter_row in filters:
                    filter_list.append({
                        'id': filter_row['id'],
                        'name': filter_row['filter_name'],
                        'type': filter_row['filter_type'],
                        'settings': self.app.json.loads(filter_row['settings']),
                        'enabled': bool(filter_row['enabled'])
                    })
                
                return self.app.jsonify({
                    'success': True,
                    'filters': filter_list
                })
                
            except Exception as e:
                return self.app.jsonify({'success': False, 'message': str(e)})
        
        @self.app.route('/api/neural-filters/<int:filter_id>/activate')
        def activate_neural_filter(filter_id):
            """Activate a specific neural filter"""
            if 'username' not in self.app.session or self.app.session.get('role') != 'admin':
                return self.app.jsonify({'success': False, 'message': 'Admin access required'})
            
            try:
                cursor = self.db.cursor()
                filter_row = cursor.execute(
                    'SELECT * FROM neural_filters WHERE id = ?', (filter_id,)
                ).fetchone()
                
                if not filter_row:
                    return self.app.jsonify({'success': False, 'message': 'Filter not found'})
                
                # Update active filter setting
                cursor.execute('''
                    INSERT OR REPLACE INTO settings (key, value, description)
                    VALUES (?, ?, ?)
                ''', ('active_neural_filter', filter_row['filter_type'], f'Filter activated by {self.app.session["username"]}'))
                
                self.db.commit()
                
                return self.app.jsonify({
                    'success': True,
                    'message': f'Filter "{filter_row["filter_name"]}" activated',
                    'filter': {
                        'id': filter_row['id'],
                        'name': filter_row['filter_name'],
                        'type': filter_row['filter_type'],
                        'settings': self.app.json.loads(filter_row['settings'])
                    }
                })
                
            except Exception as e:
                return self.app.jsonify({'success': False, 'message': str(e)})
        
        @self.app.route('/api/neural-vision/webhook')
        def neural_vision_webhook():
            """Webhook to integrate with the neural vision web app"""
            try:
                data = self.app.request.json
                
                # Validate webhook data
                if not data or 'filter_type' not in data:
                    return self.app.jsonify({'success': False, 'message': 'Invalid data'})
                
                # Log the webhook call
                cursor = self.db.cursor()
                cursor.execute('''
                    INSERT INTO filter_presets (preset_name, filter_settings, created_by)
                    VALUES (?, ?, ?)
                ''', (f"Webhook_{data['filter_type']}", 
                     self.app.json.dumps(data), 
                     data.get('user', 'webhook')))
                
                self.db.commit()
                
                return self.app.jsonify({
                    'success': True,
                    'message': 'Webhook processed successfully'
                })
                
            except Exception as e:
                return self.app.jsonify({'success': False, 'message': str(e)})
    
    def add_plugin_settings(self):
        """Add plugin-specific settings"""
        cursor = self.db.cursor()
        
        plugin_settings = [
            ('neural_vision_enabled', 'true', 'Enable Neural Vision filters'),
            ('neural_vision_api_url', 'http://localhost:8080', 'Neural Vision web app URL'),
            ('neural_vision_webhook_key', 'neural_vision_2024', 'Webhook authentication key'),
            ('neural_vision_auto_start', 'false', 'Auto-start Neural Vision with studio'),
        ]
        
        cursor.executemany('''
            INSERT OR REPLACE INTO settings (key, value, description)
            VALUES (?, ?, ?)
        ''', plugin_settings)
        
        self.db.commit()
    
    def render_neural_vision_admin(self):
        """Render the Neural Vision admin interface"""
        template = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Neural Vision Filters - Atlantiplex Studio</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        .neural-bg {
            background: linear-gradient(135deg, #0a0a0a 0%, #001a00 50%, #0a0a0a 100%);
            min-height: 100vh;
        }
        .neural-card {
            background: rgba(0, 0, 0, 0.8);
            border: 1px solid #00ff00;
            box-shadow: 0 0 20px rgba(0, 255, 0, 0.3);
        }
        .neural-btn {
            background: linear-gradient(135deg, #001100 0%, #003300 100%);
            border: 1px solid #00ff00;
            transition: all 0.3s ease;
        }
        .neural-btn:hover {
            background: linear-gradient(135deg, #003300 0%, #005500 100%);
            box-shadow: 0 0 15px rgba(0, 255, 0, 0.5);
        }
        .filter-card {
            transition: all 0.3s ease;
            cursor: pointer;
        }
        .filter-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 0 25px rgba(0, 255, 0, 0.4);
        }
        .active-filter {
            border-color: #00ff00;
            box-shadow: 0 0 30px rgba(0, 255, 0, 0.6);
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
<body class="neural-bg">
    <div class="container mx-auto px-4 py-8">
        <!-- Header -->
        <div class="text-center mb-8">
            <h1 class="text-4xl font-bold text-green-400 mb-2">🧠 NEURAL VISION FILTERS</h1>
            <p class="text-green-300 opacity-80">Advanced Real-Time Filter Management</p>
        </div>

        <!-- Status Panel -->
        <div class="neural-card rounded p-6 mb-8">
            <h2 class="text-2xl font-bold text-green-400 mb-4">System Status</h2>
            <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div class="text-center">
                    <div id="filter-count" class="text-3xl font-bold text-green-400 pulse">-</div>
                    <p class="text-green-300">Available Filters</p>
                </div>
                <div class="text-center">
                    <div id="active-filter" class="text-2xl font-bold text-green-400">None</div>
                    <p class="text-green-300">Active Filter</p>
                </div>
                <div class="text-center">
                    <div id="webapp-status" class="text-2xl font-bold text-yellow-400">Checking...</div>
                    <p class="text-green-300">Web App Status</p>
                </div>
            </div>
        </div>

        <!-- Filter Grid -->
        <div class="neural-card rounded p-6 mb-8">
            <h2 class="text-2xl font-bold text-green-400 mb-4">Available Filters</h2>
            <div id="filter-grid" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                <!-- Filters will be loaded here -->
            </div>
        </div>

        <!-- Control Panel -->
        <div class="neural-card rounded p-6 mb-8">
            <h2 class="text-2xl font-bold text-green-400 mb-4">Control Panel</h2>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                    <h3 class="text-xl font-bold text-green-400 mb-3">Quick Actions</h3>
                    <div class="space-y-3">
                        <button onclick="launchWebApp()" class="neural-btn text-green-400 px-6 py-3 rounded font-bold w-full">
                            🚀 Launch Neural Vision Web App
                        </button>
                        <button onclick="testConnection()" class="neural-btn text-green-400 px-6 py-3 rounded font-bold w-full">
                            🔗 Test Connection
                        </button>
                        <button onclick="refreshFilters()" class="neural-btn text-green-400 px-6 py-3 rounded font-bold w-full">
                            🔄 Refresh Filters
                        </button>
                    </div>
                </div>
                <div>
                    <h3 class="text-xl font-bold text-green-400 mb-3">Settings</h3>
                    <div class="space-y-3">
                        <div>
                            <label class="text-green-300 block mb-2">Web App URL:</label>
                            <input type="text" id="webapp-url" class="w-full px-3 py-2 bg-black border border-green-500 rounded text-green-400" 
                                   value="http://localhost:8080" />
                        </div>
                        <div>
                            <label class="text-green-300 block mb-2">Auto-start Web App:</label>
                            <select id="auto-start" class="w-full px-3 py-2 bg-black border border-green-500 rounded text-green-400">
                                <option value="false">Disabled</option>
                                <option value="true">Enabled</option>
                            </select>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Integration Info -->
        <div class="neural-card rounded p-6">
            <h2 class="text-2xl font-bold text-green-400 mb-4">Integration Information</h2>
            <div class="text-green-300">
                <p class="mb-2"><strong>Webhook Endpoint:</strong> <code class="bg-black px-2 py-1 rounded">/api/neural-vision/webhook</code></p>
                <p class="mb-2"><strong>Current Session:</strong> <span id="session-info">Loading...</span></p>
                <p class="mb-2"><strong>Plugin Version:</strong> {{ plugin_version }}</p>
            </div>
        </div>

        <!-- Back to Studio -->
        <div class="text-center mt-8">
            <a href="/admin" class="neural-btn text-green-400 px-8 py-3 rounded font-bold inline-block">
                ← Back to Admin Panel
            </a>
        </div>
    </div>

    <script>
        let currentActiveFilter = null;

        // Load filters on page load
        document.addEventListener('DOMContentLoaded', function() {
            loadFilters();
            checkWebAppStatus();
            loadSessionInfo();
        });

        async function loadFilters() {
            try {
                const response = await fetch('/api/neural-filters');
                const data = await response.json();
                
                if (data.success) {
                    displayFilters(data.filters);
                    document.getElementById('filter-count').textContent = data.filters.length;
                }
            } catch (error) {
                console.error('Failed to load filters:', error);
            }
        }

        function displayFilters(filters) {
            const grid = document.getElementById('filter-grid');
            grid.innerHTML = '';
            
            filters.forEach(filter => {
                const card = document.createElement('div');
                card.className = 'filter-card neural-card rounded p-4';
                card.innerHTML = `
                    <div class="text-center">
                        <div class="text-2xl mb-2">${getFilterIcon(filter.type)}</div>
                        <h3 class="text-lg font-bold text-green-400 mb-2">${filter.name}</h3>
                        <p class="text-green-300 text-sm mb-4">${getFilterDescription(filter.type)}</p>
                        <button onclick="activateFilter(${filter.id}, '${filter.type}')" 
                                class="neural-btn text-green-400 px-4 py-2 rounded text-sm font-bold w-full">
                            Activate
                        </button>
                    </div>
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
                'glimmer': '✨',
                'red': '🔴',
                'blue': '🔵',
                'green': '🟢'
            };
            return icons[type] || '👁️';
        }

        function getFilterDescription(type) {
            const descriptions = {
                'dante': 'Fiery demonic energy beams',
                'virgil': 'Elegant blue sword summons',
                'raiden': 'Electric lightning effects',
                'thuglife': 'Classic meme sunglasses',
                'glimmer': 'Magical sparkles in eyes',
                'red': 'Classic red laser beams',
                'blue': 'Electric blue energy',
                'green': 'Toxic green lasers'
            };
            return descriptions[type] || 'Advanced neural filter';
        }

        async function activateFilter(filterId, filterType) {
            try {
                const response = await fetch(`/api/neural-filters/${filterId}/activate`, {
                    method: 'POST'
                });
                const data = await response.json();
                
                if (data.success) {
                    document.getElementById('active-filter').textContent = data.filter.name;
                    currentActiveFilter = data.filter;
                    
                    // Highlight active filter
                    document.querySelectorAll('.filter-card').forEach(card => {
                        card.classList.remove('active-filter');
                    });
                    event.target.closest('.filter-card').classList.add('active-filter');
                    
                    alert(`Filter "${data.filter.name}" activated successfully!`);
                } else {
                    alert('Failed to activate filter: ' + data.message);
                }
            } catch (error) {
                console.error('Failed to activate filter:', error);
                alert('Failed to activate filter');
            }
        }

        async function checkWebAppStatus() {
            try {
                const url = document.getElementById('webapp-url').value;
                const response = await fetch(url, { method: 'HEAD' });
                
                if (response.ok) {
                    document.getElementById('webapp-status').textContent = 'Online';
                    document.getElementById('webapp-status').className = 'text-2xl font-bold text-green-400';
                } else {
                    document.getElementById('webapp-status').textContent = 'Offline';
                    document.getElementById('webapp-status').className = 'text-2xl font-bold text-red-400';
                }
            } catch (error) {
                document.getElementById('webapp-status').textContent = 'Offline';
                document.getElementById('webapp-status').className = 'text-2xl font-bold text-red-400';
            }
        }

        function launchWebApp() {
            const url = document.getElementById('webapp-url').value;
            window.open(url, '_blank');
        }

        function testConnection() {
            checkWebAppStatus();
        }

        function refreshFilters() {
            loadFilters();
        }

        async function loadSessionInfo() {
            try {
                const response = await fetch('/api/session-info');
                const data = await response.json();
                if (data.success) {
                    document.getElementById('session-info').textContent = 
                        `${data.username} (${data.role}) - ${data.login_time}`;
                }
            } catch (error) {
                document.getElementById('session-info').textContent = 'Unknown';
            }
        }
    </script>
</body>
</html>
        '''
        
        return template.replace('{{ plugin_version }}', self.plugin_version)

def init_neural_vision_plugin(app, db_connection):
    """Initialize the Neural Vision plugin"""
    plugin = NeuralVisionPlugin(app, db_connection)
    return plugin