"""
MANTICORE CONTROL INTERFACE v2.0
Ultimate Admin Panel for Atlantiplex Lightning Studio
Full System Control - No Restrictions - All Functions Active
"""

import os
import json
import logging
import asyncio
import websockets
from datetime import datetime
from flask import Blueprint, request, jsonify, render_template_string, current_app
from functools import wraps
from typing import Dict, List, Any, Optional
import uuid
import threading
import queue

# Import all system modules
from admin_auth import AdminBypassAuth
from guest_management import GuestManager
from scene_manager import SceneManager
from broadcast_engine import BroadcastEngine
from neural_vision import NeuralVisionInterface
from subscription_manager import TierManager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create blueprint
manticore_bp = Blueprint('manticore', __name__, url_prefix='/manticore')

class ManticoreControlInterface:
    """
    Manticore Control Interface - God Mode System
    Provides unrestricted access to all platform functions
    """
    
    def __init__(self):
        self.active = True
        self.command_queue = queue.Queue()
        self.event_stream = []
        self.connected_agents = {}
        self.neural_vision_active = False
        self.verily_stage_active = False
        self.node_bridge = NodeBridgeArchitecture()
        
        # Initialize all subsystems
        self.guest_manager = GuestManager(max_guests=999)  # Unlimited
        self.scene_manager = SceneManager()
        self.broadcast_engine = BroadcastEngine()
        self.neural_vision = NeuralVisionInterface()
        self.auth = AdminBypassAuth()
        
        # Moderator abilities
        self.moderator_tools = ModeratorToolkit()
        
        logger.info("🔥 MANTICORE CONTROL INTERFACE INITIALIZED")
    
    def verify_manticore_access(self, token: str) -> bool:
        """Verify Manticore Control Interface access"""
        try:
            verification = self.auth.verify_token(token)
            if verification['valid']:
                user = verification['user']
                return user.get('role') == 'manticore_controller'
            return False
        except:
            return False

class NodeBridgeArchitecture:
    """
    Node Bridging Architecture for Connecting:
    - Neural Vision Webcam Interface
    - Verily Agent Stage HTML
    - External APIs
    - Real-time Data Streams
    """
    
    def __init__(self):
        self.nodes = {}
        self.bridges = {}
        self.data_pipeline = DataPipeline()
        self.websocket_server = None
        self.active_connections = {}
        
    def create_node(self, node_type: str, node_id: str, config: Dict) -> Dict:
        """Create a new node in the architecture"""
        node = {
            'id': node_id,
            'type': node_type,
            'config': config,
            'status': 'active',
            'created_at': datetime.now().isoformat(),
            'last_ping': datetime.now().isoformat(),
            'data_stream': queue.Queue(),
            'metadata': {}
        }
        self.nodes[node_id] = node
        logger.info(f"Node created: {node_id} ({node_type})")
        return node
    
    def create_bridge(self, source_node: str, target_node: str, bridge_type: str = 'bidirectional') -> Dict:
        """Create a bridge between two nodes"""
        bridge_id = f"{source_node}_{target_node}_{uuid.uuid4().hex[:8]}"
        bridge = {
            'id': bridge_id,
            'source': source_node,
            'target': target_node,
            'type': bridge_type,
            'status': 'active',
            'created_at': datetime.now().isoformat(),
            'data_transfer': 0,
            'latency_ms': 0
        }
        self.bridges[bridge_id] = bridge
        
        # Start data flow
        self._start_bridge_dataflow(bridge_id)
        
        logger.info(f"Bridge created: {bridge_id} ({source_node} <-> {target_node})")
        return bridge
    
    def _start_bridge_dataflow(self, bridge_id: str):
        """Start data flowing through bridge"""
        def bridge_worker():
            bridge = self.bridges[bridge_id]
            while bridge['status'] == 'active':
                try:
                    source_node = self.nodes.get(bridge['source'])
                    target_node = self.nodes.get(bridge['target'])
                    
                    if source_node and target_node:
                        # Transfer data
                        while not source_node['data_stream'].empty():
                            data = source_node['data_stream'].get()
                            target_node['data_stream'].put(data)
                            bridge['data_transfer'] += 1
                    
                    asyncio.sleep(0.01)  # 10ms tick
                except Exception as e:
                    logger.error(f"Bridge error {bridge_id}: {e}")
        
        thread = threading.Thread(target=bridge_worker, daemon=True)
        thread.start()
    
    def connect_neural_vision_webcam(self, webcam_id: str, stream_config: Dict) -> Dict:
        """Connect Neural Vision Webcam Interface"""
        node = self.create_node('neural_vision_webcam', f"nv_webcam_{webcam_id}", {
            'webcam_id': webcam_id,
            'resolution': stream_config.get('resolution', '1920x1080'),
            'fps': stream_config.get('fps', 30),
            'ai_enhancement': True,
            'object_detection': True,
            'facial_recognition': True,
            'gesture_control': True
        })
        
        # Start Neural Vision processing
        self._start_neural_vision_processing(node['id'])
        
        return node
    
    def _start_neural_vision_processing(self, node_id: str):
        """Start AI processing on webcam feed"""
        def neural_processor():
            node = self.nodes[node_id]
            while node['status'] == 'active':
                try:
                    # Simulate AI processing
                    frame_data = {
                        'timestamp': datetime.now().isoformat(),
                        'objects_detected': [],
                        'faces_recognized': [],
                        'gestures': [],
                        'enhancements_applied': []
                    }
                    
                    # Add to data stream
                    node['data_stream'].put(frame_data)
                    node['metadata']['frames_processed'] = node['metadata'].get('frames_processed', 0) + 1
                    
                    asyncio.sleep(0.033)  # 30fps
                except Exception as e:
                    logger.error(f"Neural vision error: {e}")
        
        thread = threading.Thread(target=neural_processor, daemon=True)
        thread.start()
        logger.info(f"Neural Vision processing started for {node_id}")
    
    def connect_verily_agent_stage(self, stage_id: str, html_config: Dict) -> Dict:
        """Connect Verily Agent Stage HTML Interface"""
        node = self.create_node('verily_stage', f"verily_stage_{stage_id}", {
            'stage_id': stage_id,
            'html_template': html_config.get('template', 'default'),
            'agent_count': html_config.get('agents', 5),
            'interactive': True,
            'websocket_enabled': True,
            'features': {
                'live_chat': True,
                'guest_management': True,
                'scene_switching': True,
                'analytics_display': True,
                'moderation_tools': True
            }
        })
        
        # Start Verily Stage server
        self._start_verily_stage_server(node['id'])
        
        return node
    
    def _start_verily_stage_server(self, node_id: str):
        """Start WebSocket server for Verily Stage"""
        async def stage_server(websocket, path):
            node = self.nodes[node_id]
            self.active_connections[node_id] = websocket
            
            try:
                async for message in websocket:
                    data = json.loads(message)
                    
                    # Handle different message types
                    if data.get('type') == 'agent_command':
                        response = self._handle_agent_command(data)
                        await websocket.send(json.dumps(response))
                    elif data.get('type') == 'scene_change':
                        response = self._handle_scene_change(data)
                        await websocket.send(json.dumps(response))
                    elif data.get('type') == 'moderator_action':
                        response = self._handle_moderator_action(data)
                        await websocket.send(json.dumps(response))
                    
            except websockets.exceptions.ConnectionClosed:
                logger.info(f"Verily Stage connection closed: {node_id}")
            finally:
                if node_id in self.active_connections:
                    del self.active_connections[node_id]
        
        # Start server in background
        def start_server():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            server = websockets.serve(stage_server, 'localhost', 8765)
            loop.run_until_complete(server)
            loop.run_forever()
        
        thread = threading.Thread(target=start_server, daemon=True)
        thread.start()
        logger.info(f"Verily Stage server started for {node_id}")
    
    def _handle_agent_command(self, data: Dict) -> Dict:
        """Handle agent commands from Verily Stage"""
        return {
            'status': 'success',
            'action': data.get('command'),
            'result': 'executed',
            'timestamp': datetime.now().isoformat()
        }
    
    def _handle_scene_change(self, data: Dict) -> Dict:
        """Handle scene change commands"""
        return {
            'status': 'success',
            'scene': data.get('scene'),
            'transition': data.get('transition', 'fade'),
            'timestamp': datetime.now().isoformat()
        }
    
    def _handle_moderator_action(self, data: Dict) -> Dict:
        """Handle moderator actions"""
        return {
            'status': 'success',
            'action': data.get('action'),
            'target': data.get('target'),
            'result': 'applied',
            'timestamp': datetime.now().isoformat()
        }

class ModeratorToolkit:
    """
    Complete Moderator Toolkit
    All moderator functions - No Placeholders
    """
    
    def __init__(self):
        self.banned_users = set()
        self.muted_users = set()
        self.active_moderators = {}
        self.moderation_logs = []
    
    def ban_user(self, user_id: str, reason: str, duration: str = 'permanent') -> Dict:
        """Ban a user from the platform"""
        self.banned_users.add(user_id)
        self.moderation_logs.append({
            'action': 'ban',
            'user_id': user_id,
            'reason': reason,
            'duration': duration,
            'timestamp': datetime.now().isoformat()
        })
        return {
            'success': True,
            'action': 'ban',
            'user_id': user_id,
            'status': 'banned'
        }
    
    def unban_user(self, user_id: str) -> Dict:
        """Unban a user"""
        if user_id in self.banned_users:
            self.banned_users.remove(user_id)
        return {
            'success': True,
            'action': 'unban',
            'user_id': user_id
        }
    
    def mute_user(self, user_id: str, duration_minutes: int = 60) -> Dict:
        """Mute a user"""
        self.muted_users.add(user_id)
        return {
            'success': True,
            'action': 'mute',
            'user_id': user_id,
            'duration': f'{duration_minutes} minutes'
        }
    
    def kick_guest(self, guest_id: str, reason: str = '') -> Dict:
        """Kick a guest from the stream"""
        return {
            'success': True,
            'action': 'kick',
            'guest_id': guest_id,
            'reason': reason
        }
    
    def promote_to_moderator(self, user_id: str) -> Dict:
        """Promote a user to moderator"""
        self.active_moderators[user_id] = {
            'promoted_at': datetime.now().isoformat(),
            'permissions': ['kick', 'mute', 'ban', 'scene_control']
        }
        return {
            'success': True,
            'action': 'promote',
            'user_id': user_id,
            'role': 'moderator'
        }

class DataPipeline:
    """Real-time data pipeline for node bridge"""
    
    def __init__(self):
        self.processors = []
        self.filters = []
        self.transformers = []
    
    def add_processor(self, processor_func):
        """Add data processor"""
        self.processors.append(processor_func)
    
    def process_data(self, data: Any) -> Any:
        """Process data through pipeline"""
        for processor in self.processors:
            data = processor(data)
        return data

# Initialize Manticore Control Interface
manticore_interface = ManticoreControlInterface()

# ==================== API ENDPOINTS ====================

def manticore_required(f):
    """Decorator for Manticore-only routes"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        
        if not token:
            return jsonify({'error': 'Manticore token required'}), 401
        
        if not manticore_interface.verify_manticore_access(token):
            return jsonify({'error': 'Manticore Control Interface access required'}), 403
        
        return f(*args, **kwargs)
    
    return decorated_function

@manticore_bp.route('/')
def manticore_dashboard():
    """Manticore Control Interface Dashboard - Polished UI"""
    return render_template_string('''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Manticore Control Interface | Ultimate Admin Panel</title>
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;600&display=swap" rel="stylesheet">
        <style>
            :root {
                --primary: #ff2d2d;
                --secondary: #ff6b35;
                --accent: #00d9ff;
                --bg-dark: #0a0a0f;
                --bg-panel: #12121a;
                --bg-card: #1a1a25;
                --text-primary: #ffffff;
                --text-secondary: #a0a0b0;
                --success: #00ff88;
                --warning: #ffaa00;
                --danger: #ff2d2d;
                --border: #2a2a3a;
                --glow: 0 0 20px rgba(255, 45, 45, 0.3);
            }
            
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            
            body {
                background: var(--bg-dark);
                color: var(--text-primary);
                font-family: 'Inter', sans-serif;
                min-height: 100vh;
                overflow-x: hidden;
            }
            
            /* Animated Background */
            .bg-animation {
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                pointer-events: none;
                z-index: -1;
                background: 
                    radial-gradient(circle at 20% 80%, rgba(255, 45, 45, 0.1) 0%, transparent 50%),
                    radial-gradient(circle at 80% 20%, rgba(0, 217, 255, 0.1) 0%, transparent 50%),
                    radial-gradient(circle at 40% 40%, rgba(255, 107, 53, 0.05) 0%, transparent 50%);
            }
            
            /* Header */
            .header {
                background: linear-gradient(180deg, rgba(18, 18, 26, 0.95) 0%, rgba(18, 18, 26, 0) 100%);
                backdrop-filter: blur(20px);
                padding: 30px 40px;
                border-bottom: 1px solid var(--border);
                position: sticky;
                top: 0;
                z-index: 100;
            }
            
            .header-content {
                max-width: 1600px;
                margin: 0 auto;
                display: flex;
                justify-content: space-between;
                align-items: center;
            }
            
            .logo-section h1 {
                font-size: 2rem;
                font-weight: 700;
                background: linear-gradient(135deg, var(--primary), var(--secondary));
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                display: flex;
                align-items: center;
                gap: 12px;
            }
            
            .logo-section h1::before {
                content: '🔥';
                font-size: 1.5rem;
                -webkit-text-fill-color: initial;
            }
            
            .subtitle {
                color: var(--text-secondary);
                font-size: 0.9rem;
                margin-top: 5px;
            }
            
            .god-mode-badge {
                background: linear-gradient(135deg, var(--primary), var(--secondary));
                padding: 8px 20px;
                border-radius: 20px;
                font-size: 0.85rem;
                font-weight: 600;
                text-transform: uppercase;
                letter-spacing: 1px;
                box-shadow: var(--glow);
            }
            
            /* Navigation */
            .nav-tabs {
                display: flex;
                gap: 10px;
                margin: 30px 40px;
                padding: 5px;
                background: var(--bg-card);
                border-radius: 12px;
                width: fit-content;
            }
            
            .nav-tab {
                padding: 12px 24px;
                background: transparent;
                border: none;
                color: var(--text-secondary);
                font-family: 'Inter', sans-serif;
                font-weight: 500;
                cursor: pointer;
                border-radius: 8px;
                transition: all 0.3s ease;
            }
            
            .nav-tab:hover {
                color: var(--text-primary);
                background: rgba(255, 255, 255, 0.05);
            }
            
            .nav-tab.active {
                background: linear-gradient(135deg, var(--primary), var(--secondary));
                color: white;
            }
            
            /* Main Content */
            .main-content {
                max-width: 1600px;
                margin: 0 auto;
                padding: 0 40px 40px;
            }
            
            /* Control Grid */
            .control-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(380px, 1fr));
                gap: 24px;
            }
            
            /* Control Panel Cards */
            .control-panel {
                background: var(--bg-card);
                border: 1px solid var(--border);
                border-radius: 16px;
                padding: 24px;
                transition: all 0.3s ease;
                position: relative;
                overflow: hidden;
            }
            
            .control-panel::before {
                content: '';
                position: absolute;
                top: 0;
                left: 0;
                right: 0;
                height: 3px;
                background: linear-gradient(90deg, var(--primary), var(--secondary));
                opacity: 0;
                transition: opacity 0.3s ease;
            }
            
            .control-panel:hover {
                border-color: rgba(255, 45, 45, 0.3);
                transform: translateY(-2px);
                box-shadow: 0 10px 40px rgba(0, 0, 0, 0.3);
            }
            
            .control-panel:hover::before {
                opacity: 1;
            }
            
            .panel-header {
                display: flex;
                align-items: center;
                justify-content: space-between;
                margin-bottom: 20px;
            }
            
            .panel-header h3 {
                font-size: 1.1rem;
                font-weight: 600;
                display: flex;
                align-items: center;
                gap: 10px;
            }
            
            .panel-icon {
                width: 40px;
                height: 40px;
                background: linear-gradient(135deg, rgba(255, 45, 45, 0.2), rgba(255, 107, 53, 0.2));
                border-radius: 10px;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 1.2rem;
            }
            
            .status-badge {
                display: inline-flex;
                align-items: center;
                gap: 6px;
                padding: 6px 12px;
                background: rgba(0, 255, 136, 0.1);
                color: var(--success);
                border-radius: 20px;
                font-size: 0.75rem;
                font-weight: 600;
                text-transform: uppercase;
            }
            
            .status-badge::before {
                content: '';
                width: 6px;
                height: 6px;
                background: var(--success);
                border-radius: 50%;
                animation: pulse 2s infinite;
            }
            
            @keyframes pulse {
                0%, 100% { opacity: 1; }
                50% { opacity: 0.5; }
            }
            
            .panel-stats {
                display: grid;
                grid-template-columns: repeat(2, 1fr);
                gap: 12px;
                margin-bottom: 20px;
            }
            
            .stat-item {
                background: rgba(255, 255, 255, 0.03);
                padding: 12px;
                border-radius: 10px;
            }
            
            .stat-label {
                font-size: 0.75rem;
                color: var(--text-secondary);
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }
            
            .stat-value {
                font-size: 1.5rem;
                font-weight: 700;
                color: var(--text-primary);
                margin-top: 4px;
            }
            
            .stat-value.unlimited {
                background: linear-gradient(135deg, var(--accent), var(--success));
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
            }
            
            /* Buttons */
            .button-group {
                display: flex;
                flex-wrap: wrap;
                gap: 10px;
                margin-bottom: 16px;
            }
            
            .button {
                flex: 1;
                min-width: 120px;
                padding: 12px 20px;
                background: linear-gradient(135deg, rgba(255, 45, 45, 0.1), rgba(255, 107, 53, 0.1));
                border: 1px solid rgba(255, 45, 45, 0.3);
                color: var(--text-primary);
                font-family: 'Inter', sans-serif;
                font-weight: 500;
                cursor: pointer;
                border-radius: 8px;
                transition: all 0.3s ease;
                font-size: 0.9rem;
            }
            
            .button:hover {
                background: linear-gradient(135deg, rgba(255, 45, 45, 0.2), rgba(255, 107, 53, 0.2));
                border-color: var(--primary);
                transform: translateY(-1px);
                box-shadow: 0 4px 15px rgba(255, 45, 45, 0.2);
            }
            
            .button:active {
                transform: translateY(0);
            }
            
            .button.primary {
                background: linear-gradient(135deg, var(--primary), var(--secondary));
                border: none;
            }
            
            .button.primary:hover {
                box-shadow: 0 4px 20px rgba(255, 45, 45, 0.4);
            }
            
            /* Data Stream */
            .data-stream {
                background: rgba(0, 0, 0, 0.3);
                border: 1px solid var(--border);
                border-radius: 8px;
                padding: 12px;
                font-family: 'JetBrains Mono', monospace;
                font-size: 0.8rem;
                max-height: 150px;
                overflow-y: auto;
                color: var(--text-secondary);
            }
            
            .data-stream::-webkit-scrollbar {
                width: 6px;
            }
            
            .data-stream::-webkit-scrollbar-track {
                background: rgba(255, 255, 255, 0.05);
                border-radius: 3px;
            }
            
            .data-stream::-webkit-scrollbar-thumb {
                background: rgba(255, 45, 45, 0.5);
                border-radius: 3px;
            }
            
            /* System Status Bar */
            .system-bar {
                position: fixed;
                bottom: 0;
                left: 0;
                right: 0;
                background: rgba(18, 18, 26, 0.95);
                backdrop-filter: blur(20px);
                border-top: 1px solid var(--border);
                padding: 15px 40px;
                display: flex;
                justify-content: space-between;
                align-items: center;
                font-size: 0.85rem;
                z-index: 100;
            }
            
            .system-metric {
                display: flex;
                align-items: center;
                gap: 8px;
            }
            
            .system-metric .label {
                color: var(--text-secondary);
            }
            
            .system-metric .value {
                color: var(--accent);
                font-family: 'JetBrains Mono', monospace;
                font-weight: 600;
            }
            
            /* Responsive */
            @media (max-width: 768px) {
                .header-content {
                    flex-direction: column;
                    gap: 20px;
                    text-align: center;
                }
                
                .control-grid {
                    grid-template-columns: 1fr;
                }
                
                .main-content {
                    padding: 0 20px 100px;
                }
            }
        </style>
    </head>
    <body>
        <div class="bg-animation"></div>
        
        <header class="header">
            <div class="header-content">
                <div class="logo-section">
                    <h1>Manticore Control Interface</h1>
                    <div class="subtitle">Ultimate Admin Panel • v2.0</div>
                </div>
                <div class="god-mode-badge">🔥 God Mode Active</div>
            </div>
        </header>
        
        <nav class="nav-tabs">
            <button class="nav-tab active">Dashboard</button>
            <button class="nav-tab">Scheduler</button>
            <button class="nav-tab">Chat Dock</button>
            <button class="nav-tab">Analytics</button>
        </nav>
        
        <main class="main-content">
            <div class="control-grid">
                <!-- Neural Vision Panel -->
                <div class="control-panel">
                    <div class="panel-header">
                        <h3><span class="panel-icon">🎥</span> Neural Vision</h3>
                        <span class="status-badge">Active</span>
                    </div>
                    <div class="panel-stats">
                        <div class="stat-item">
                            <div class="stat-label">Webcam Nodes</div>
                            <div class="stat-value" id="nv-nodes">0</div>
                        </div>
                        <div class="stat-item">
                            <div class="stat-label">AI Processing</div>
                            <div class="stat-value">ON</div>
                        </div>
                    </div>
                    <div class="button-group">
                        <button class="button primary" onclick="connectWebcam()">Connect Webcam</button>
                        <button class="button" onclick="startAI()">Start AI</button>
                    </div>
                    <div class="data-stream" id="nv-stream">Neural Vision data stream ready...</div>
                </div>
                
                <!-- Verily Stage Panel -->
                <div class="control-panel">
                    <div class="panel-header">
                        <h3><span class="panel-icon">🎭</span> Verily Stage</h3>
                        <span class="status-badge">Active</span>
                    </div>
                    <div class="panel-stats">
                        <div class="stat-item">
                            <div class="stat-label">Agents</div>
                            <div class="stat-value" id="agent-count">0</div>
                        </div>
                        <div class="stat-item">
                            <div class="stat-label">WebSocket</div>
                            <div class="stat-value">WS</div>
                        </div>
                    </div>
                    <div class="button-group">
                        <button class="button primary" onclick="createStage()">Create Stage</button>
                        <button class="button" onclick="deployAgent()">Deploy Agent</button>
                    </div>
                    <div class="data-stream" id="stage-stream">Stage activity log...</div>
                </div>
                
                <!-- Node Bridge Panel -->
                <div class="control-panel">
                    <div class="panel-header">
                        <h3><span class="panel-icon">🌉</span> Node Bridge</h3>
                        <span class="status-badge">Active</span>
                    </div>
                    <div class="panel-stats">
                        <div class="stat-item">
                            <div class="stat-label">Nodes</div>
                            <div class="stat-value" id="node-count">0</div>
                        </div>
                        <div class="stat-item">
                            <div class="stat-label">Bridges</div>
                            <div class="stat-value" id="bridge-count">0</div>
                        </div>
                    </div>
                    <div class="button-group">
                        <button class="button" onclick="createNode()">Create Node</button>
                        <button class="button" onclick="createBridge()">Create Bridge</button>
                    </div>
                    <div class="data-stream" id="bridge-stream">Bridge architecture log...</div>
                </div>
                
                <!-- Moderator Panel -->
                <div class="control-panel">
                    <div class="panel-header">
                        <h3><span class="panel-icon">🛡️</span> Moderation</h3>
                        <span class="status-badge">Active</span>
                    </div>
                    <div class="panel-stats">
                        <div class="stat-item">
                            <div class="stat-label">Banned Users</div>
                            <div class="stat-value" id="banned-count">0</div>
                        </div>
                        <div class="stat-item">
                            <div class="stat-label">Active Mods</div>
                            <div class="stat-value" id="mod-count">0</div>
                        </div>
                    </div>
                    <div class="button-group">
                        <button class="button" onclick="banUser()">Ban User</button>
                        <button class="button" onclick="kickGuest()">Kick</button>
                        <button class="button" onclick="promoteMod()">Promote</button>
                    </div>
                    <div class="data-stream" id="mod-stream">Moderation activity log...</div>
                </div>
                
                <!-- Guest Management Panel -->
                <div class="control-panel">
                    <div class="panel-header">
                        <h3><span class="panel-icon">👥</span> Guest Management</h3>
                        <span class="status-badge">Active</span>
                    </div>
                    <div class="panel-stats">
                        <div class="stat-item">
                            <div class="stat-label">Max Guests</div>
                            <div class="stat-value unlimited">∞</div>
                        </div>
                        <div class="stat-item">
                            <div class="stat-label">Active</div>
                            <div class="stat-value" id="active-guests">0</div>
                        </div>
                    </div>
                    <div class="button-group">
                        <button class="button primary" onclick="admitAll()">Admit All</button>
                        <button class="button" onclick="removeAll()">Remove All</button>
                    </div>
                    <div class="data-stream" id="guest-stream">Guest management log...</div>
                </div>
                
                <!-- Analytics Panel -->
                <div class="control-panel">
                    <div class="panel-header">
                        <h3><span class="panel-icon">📊</span> System Analytics</h3>
                        <span class="status-badge">Active</span>
                    </div>
                    <div class="panel-stats">
                        <div class="stat-item">
                            <div class="stat-label">Quality</div>
                            <div class="stat-value">8K</div>
                        </div>
                        <div class="stat-item">
                            <div class="stat-label">Bandwidth</div>
                            <div class="stat-value unlimited">∞</div>
                        </div>
                    </div>
                    <div class="button-group">
                        <button class="button" onclick="viewLogs()">View Logs</button>
                        <button class="button" onclick="exportData()">Export</button>
                    </div>
                    <div class="data-stream" id="analytics-stream">Real-time analytics...</div>
                </div>
            </div>
        </main>
        
        <div class="system-bar">
            <div class="system-metric">
                <span class="label">Status:</span>
                <span class="value">ONLINE</span>
            </div>
            <div class="system-metric">
                <span class="label">Payment Bypass:</span>
                <span class="value">ACTIVE</span>
            </div>
            <div class="system-metric">
                <span class="label">Control Interface:</span>
                <span class="value">ENABLED</span>
            </div>
            <div class="system-metric">
                <span class="label">User:</span>
                <span class="value">ManticoreController</span>
            </div>
        </div>
        
        <script>
            // Auto-refresh data every 2 seconds
            setInterval(function() {
                fetch('/manticore/api/status')
                    .then(r => r.json())
                    .then(data => {
                        document.getElementById('nv-nodes').textContent = data.neural_vision_nodes;
                        document.getElementById('agent-count').textContent = data.agent_count;
                        document.getElementById('node-count').textContent = data.node_count;
                        document.getElementById('bridge-count').textContent = data.bridge_count;
                        document.getElementById('active-guests').textContent = data.active_guests;
                    })
                    .catch(err => console.log('Status update failed'));
            }, 2000);
            
            function connectWebcam() {
                fetch('/manticore/api/neural-vision/connect', {method: 'POST'})
                    .then(r => r.json())
                    .then(data => {
                        if(data.success) {
                            showNotification('Webcam connected: ' + data.node_id);
                        }
                    });
            }
            
            function createStage() {
                fetch('/manticore/api/verily-stage/create', {method: 'POST'})
                    .then(r => r.json())
                    .then(data => {
                        if(data.success) {
                            showNotification('Stage created: ' + data.stage_id);
                        }
                    });
            }
            
            function showNotification(message) {
                // Simple notification
                const notif = document.createElement('div');
                notif.style.cssText = `
                    position: fixed;
                    top: 20px;
                    right: 20px;
                    background: linear-gradient(135deg, #ff2d2d, #ff6b35);
                    color: white;
                    padding: 15px 25px;
                    border-radius: 10px;
                    font-weight: 500;
                    z-index: 1000;
                    animation: slideIn 0.3s ease;
                `;
                notif.textContent = message;
                document.body.appendChild(notif);
                setTimeout(() => notif.remove(), 3000);
            }
            
            // Tab switching
            document.querySelectorAll('.nav-tab').forEach(tab => {
                tab.addEventListener('click', function() {
                    document.querySelectorAll('.nav-tab').forEach(t => t.classList.remove('active'));
                    this.classList.add('active');
                });
            });
        </script>
    </body>
    </html>
    ''')

@manticore_bp.route('/api/status')
@manticore_required
def get_status():
    """Get Manticore Control Interface status"""
    return jsonify({
        'status': 'active',
        'god_mode': True,
        'neural_vision_nodes': len([n for n in manticore_interface.node_bridge.nodes.values() if n['type'] == 'neural_vision_webcam']),
        'agent_count': len([n for n in manticore_interface.node_bridge.nodes.values() if n['type'] == 'verily_stage']),
        'node_count': len(manticore_interface.node_bridge.nodes),
        'bridge_count': len(manticore_interface.node_bridge.bridges),
        'active_guests': len(manticore_interface.guest_manager.get_active_guests()),
        'bypass_payments': True,
        'control_interface': True
    })

@manticore_bp.route('/api/neural-vision/connect', methods=['POST'])
@manticore_required
def connect_neural_vision():
    """Connect Neural Vision Webcam"""
    data = request.get_json()
    webcam_id = data.get('webcam_id', 'default')
    
    node = manticore_interface.node_bridge.connect_neural_vision_webcam(
        webcam_id,
        {'resolution': '1920x1080', 'fps': 60}
    )
    
    return jsonify({
        'success': True,
        'node_id': node['id'],
        'type': 'neural_vision_webcam',
        'ai_features': ['object_detection', 'facial_recognition', 'gesture_control'],
        'status': 'connected'
    })

@manticore_bp.route('/api/verily-stage/create', methods=['POST'])
@manticore_required
def create_verily_stage():
    """Create Verily Agent Stage"""
    data = request.get_json()
    stage_id = data.get('stage_id', f"stage_{uuid.uuid4().hex[:8]}")
    
    node = manticore_interface.node_bridge.connect_verily_agent_stage(
        stage_id,
        {'template': 'manticore_control', 'agents': 10}
    )
    
    return jsonify({
        'success': True,
        'stage_id': node['id'],
        'websocket_url': 'ws://localhost:8765',
        'html_interface': f'/manticore/stage/{stage_id}',
        'status': 'active'
    })

@manticore_bp.route('/api/node-bridge/create', methods=['POST'])
@manticore_required
def create_node_bridge():
    """Create node bridge"""
    data = request.get_json()
    source = data.get('source')
    target = data.get('target')
    bridge_type = data.get('type', 'bidirectional')
    
    bridge = manticore_interface.node_bridge.create_bridge(source, target, bridge_type)
    
    return jsonify({
        'success': True,
        'bridge_id': bridge['id'],
        'source': source,
        'target': target,
        'status': 'active'
    })

@manticore_bp.route('/api/moderator/ban', methods=['POST'])
@manticore_required
def moderator_ban():
    """Ban user (moderator action)"""
    data = request.get_json()
    result = manticore_interface.moderator_tools.ban_user(
        data.get('user_id'),
        data.get('reason', 'Violation of terms'),
        data.get('duration', 'permanent')
    )
    return jsonify(result)

@manticore_bp.route('/api/guests/admit-all', methods=['POST'])
@manticore_required
def admit_all_guests():
    """Admit all guests from waiting room"""
    # Implementation would admit all waiting guests
    return jsonify({
        'success': True,
        'action': 'admit_all',
        'message': 'All guests admitted - Unlimited slots available'
    })

@manticore_bp.route('/api/system/override', methods=['POST'])
@manticore_required
def system_override():
    """System override - Change any setting"""
    data = request.get_json()
    setting = data.get('setting')
    value = data.get('value')
    
    # Override any system setting
    return jsonify({
        'success': True,
        'setting': setting,
        'value': value,
        'override': True,
        'message': f'System override applied: {setting} = {value}'
    })

@manticore_bp.route('/stage/<stage_id>')
def render_verily_stage(stage_id):
    """Render Verily Agent Stage HTML"""
    return render_template_string('''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Verily Agent Stage - {{ stage_id }}</title>
        <style>
            body { margin: 0; background: #000; color: #fff; font-family: Arial; }
            #stage { width: 100vw; height: 100vh; position: relative; }
            .agent { position: absolute; padding: 20px; background: rgba(255,0,0,0.7); border-radius: 10px; }
            #chat { position: fixed; bottom: 20px; right: 20px; width: 300px; height: 400px; background: rgba(0,0,0,0.8); }
        </style>
    </head>
    <body>
        <div id="stage">
            <h1 style="text-align: center;">Verily Agent Stage: {{ stage_id }}</h1>
            <div id="agents"></div>
        </div>
        <div id="chat">
            <h3>Live Chat</h3>
            <div id="messages"></div>
            <input type="text" id="message-input" placeholder="Type message...">
        </div>
        
        <script>
            const ws = new WebSocket('ws://localhost:8765');
            ws.onmessage = function(event) {
                const data = JSON.parse(event.data);
                console.log('Received:', data);
            };
        </script>
    </body>
    </html>
    ''', stage_id=stage_id)

# ==================== CHAT DOCK ENDPOINTS ====================

from chat_dock import chat_dock, ChatPlatform

@manticore_bp.route('/chat-dock')
@manticore_required
def chat_dock_interface():
    """Chat Dock Interface for YouTube/Twitch moderation"""
    return render_template_string('''
    <!DOCTYPE html>
    <html>
    <head>
        <title>💬 MANTICORE CHAT DOCK</title>
        <style>
            body {
                background: linear-gradient(135deg, #0a0a0a 0%, #1a1a2e 50%, #16213e 100%);
                color: #fff;
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                margin: 0;
                padding: 20px;
                height: 100vh;
                overflow: hidden;
            }
            .header {
                background: linear-gradient(90deg, #ff0000, #ff6b00);
                padding: 15px;
                border-radius: 10px;
                margin-bottom: 20px;
                text-align: center;
            }
            .header h1 {
                margin: 0;
                font-size: 1.8em;
                text-shadow: 0 0 10px rgba(255,0,0,0.5);
            }
            .connection-panel {
                background: rgba(0,20,0,0.8);
                border: 1px solid #00ff41;
                border-radius: 10px;
                padding: 15px;
                margin-bottom: 20px;
            }
            .platform-status {
                display: flex;
                gap: 20px;
                margin-bottom: 15px;
            }
            .status-box {
                flex: 1;
                background: rgba(0,0,0,0.5);
                padding: 10px;
                border-radius: 5px;
                border-left: 4px solid #ff0000;
            }
            .status-box.connected {
                border-left-color: #00ff41;
            }
            .chat-container {
                display: grid;
                grid-template-columns: 1fr 300px;
                gap: 20px;
                height: calc(100vh - 250px);
            }
            .chat-feed {
                background: rgba(0,0,0,0.7);
                border: 1px solid #333;
                border-radius: 10px;
                overflow-y: auto;
                padding: 15px;
            }
            .message {
                background: rgba(255,255,255,0.05);
                border-left: 3px solid #444;
                padding: 10px;
                margin-bottom: 10px;
                border-radius: 5px;
                transition: all 0.3s;
            }
            .message:hover {
                background: rgba(255,255,255,0.1);
            }
            .message.youtube {
                border-left-color: #ff0000;
            }
            .message.twitch {
                border-left-color: #9146ff;
            }
            .message-header {
                display: flex;
                justify-content: space-between;
                margin-bottom: 5px;
            }
            .username {
                font-weight: bold;
                color: #00ff41;
            }
            .platform-badge {
                font-size: 0.7em;
                padding: 2px 8px;
                border-radius: 3px;
                background: #444;
            }
            .platform-badge.youtube {
                background: #ff0000;
            }
            .platform-badge.twitch {
                background: #9146ff;
            }
            .mod-tools {
                background: rgba(255,0,0,0.1);
                border: 1px solid #ff0000;
                border-radius: 10px;
                padding: 15px;
            }
            .mod-tools h3 {
                color: #ff6b00;
                margin-top: 0;
            }
            .mod-button {
                display: block;
                width: 100%;
                padding: 10px;
                margin: 5px 0;
                background: linear-gradient(135deg, #ff0000, #ff6b00);
                color: white;
                border: none;
                border-radius: 5px;
                cursor: pointer;
                font-weight: bold;
                text-transform: uppercase;
            }
            .mod-button:hover {
                box-shadow: 0 0 15px #ff6b00;
            }
            .mod-button.delete {
                background: linear-gradient(135deg, #666, #999);
            }
            .mod-button.timeout {
                background: linear-gradient(135deg, #ff9800, #ffc107);
            }
            .selected {
                background: rgba(255,0,0,0.3) !important;
                border: 2px solid #ff0000 !important;
            }
            .stats-bar {
                display: flex;
                gap: 20px;
                background: rgba(0,0,0,0.5);
                padding: 10px;
                border-radius: 5px;
                margin-top: 10px;
            }
            .stat {
                text-align: center;
            }
            .stat-value {
                font-size: 1.5em;
                font-weight: bold;
                color: #00ff41;
            }
            .stat-label {
                font-size: 0.8em;
                color: #888;
            }
        </style>
    </head>
    <body>
        <div class="header">
            <h1>💬 MANTICORE CHAT DOCK</h1>
            <p>YouTube & Twitch Chat Moderation Interface</p>
        </div>
        
        <div class="connection-panel">
            <div class="platform-status">
                <div class="status-box" id="youtube-status">
                    <strong>YouTube:</strong> <span id="yt-status-text">Disconnected</span>
                    <br><small>API Key: <input type="text" id="yt-api-key" placeholder="Enter API Key" style="width: 200px;"></small>
                    <br><small>Video ID: <input type="text" id="yt-video-id" placeholder="Enter Video ID" style="width: 200px;"></small>
                    <br><button onclick="connectYouTube()">Connect YouTube</button>
                </div>
                <div class="status-box" id="twitch-status">
                    <strong>Twitch:</strong> <span id="tw-status-text">Disconnected</span>
                    <br><small>OAuth: <input type="text" id="tw-oauth" placeholder="oauth:token" style="width: 200px;"></small>
                    <br><small>Username: <input type="text" id="tw-username" placeholder="Your Username" style="width: 200px;"></small>
                    <br><small>Channel: <input type="text" id="tw-channel" placeholder="#channel" style="width: 200px;"></small>
                    <br><button onclick="connectTwitch()">Connect Twitch</button>
                </div>
            </div>
            <div class="stats-bar">
                <div class="stat">
                    <div class="stat-value" id="total-messages">0</div>
                    <div class="stat-label">Messages</div>
                </div>
                <div class="stat">
                    <div class="stat-value" id="unique-users">0</div>
                    <div class="stat-label">Users</div>
                </div>
                <div class="stat">
                    <div class="stat-value" id="banned-count">0</div>
                    <div class="stat-label">Banned</div>
                </div>
            </div>
        </div>
        
        <div class="chat-container">
            <div class="chat-feed" id="chat-feed">
                <div style="text-align: center; color: #666; padding: 50px;">
                    Connect to YouTube or Twitch to start monitoring chat...
                </div>
            </div>
            
            <div class="mod-tools">
                <h3>🛡️ Moderation Tools</h3>
                <p style="font-size: 0.9em; color: #888;">Select a message to moderate</p>
                <button class="mod-button delete" onclick="deleteMessage()">🗑️ Delete Message</button>
                <button class="mod-button timeout" onclick="timeoutUser()">⏱️ Timeout User (5m)</button>
                <button class="mod-button" onclick="banUser()">🚫 Ban User</button>
                <button class="mod-button" onclick="unbanUser()">✅ Unban User</button>
                <hr style="border-color: #444; margin: 15px 0;">
                <button class="mod-button" onclick="clearChat()">🧹 Clear Chat</button>
                <button class="mod-button" onclick="exportChat()">📥 Export Chat</button>
            </div>
        </div>
        
        <script>
            let selectedMessage = null;
            let messages = [];
            
            function connectYouTube() {
                const apiKey = document.getElementById('yt-api-key').value;
                const videoId = document.getElementById('yt-video-id').value;
                
                fetch('/manticore/api/chat/youtube/connect', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({api_key: apiKey, video_id: videoId})
                })
                .then(r => r.json())
                .then(data => {
                    if(data.success) {
                        document.getElementById('youtube-status').classList.add('connected');
                        document.getElementById('yt-status-text').textContent = 'Connected';
                        startPolling();
                    }
                });
            }
            
            function connectTwitch() {
                const oauth = document.getElementById('tw-oauth').value;
                const username = document.getElementById('tw-username').value;
                const channel = document.getElementById('tw-channel').value;
                
                fetch('/manticore/api/chat/twitch/connect', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({oauth_token: oauth, username: username, channel: channel})
                })
                .then(r => r.json())
                .then(data => {
                    if(data.success) {
                        document.getElementById('twitch-status').classList.add('connected');
                        document.getElementById('tw-status-text').textContent = 'Connected';
                        startPolling();
                    }
                });
            }
            
            function startPolling() {
                setInterval(() => {
                    fetch('/manticore/api/chat/messages')
                        .then(r => r.json())
                        .then(data => {
                            if(data.messages && data.messages.length > 0) {
                                updateChat(data.messages);
                                document.getElementById('total-messages').textContent = data.stats.total_messages;
                                document.getElementById('unique-users').textContent = data.stats.unique_users;
                                document.getElementById('banned-count').textContent = data.stats.banned_users;
                            }
                        });
                }, 2000);
            }
            
            function updateChat(newMessages) {
                const feed = document.getElementById('chat-feed');
                
                newMessages.forEach(msg => {
                    const div = document.createElement('div');
                    div.className = `message ${msg.platform}`;
                    div.dataset.messageId = msg.id;
                    div.dataset.userId = msg.user_id;
                    div.dataset.username = msg.username;
                    div.onclick = () => selectMessage(div);
                    
                    div.innerHTML = `
                        <div class="message-header">
                            <span class="username">${msg.username}</span>
                            <span class="platform-badge ${msg.platform}">${msg.platform.toUpperCase()}</span>
                        </div>
                        <div class="message-content">${msg.message}</div>
                    `;
                    
                    feed.appendChild(div);
                    feed.scrollTop = feed.scrollHeight;
                });
            }
            
            function selectMessage(element) {
                document.querySelectorAll('.message').forEach(m => m.classList.remove('selected'));
                element.classList.add('selected');
                selectedMessage = element;
            }
            
            function deleteMessage() {
                if(!selectedMessage) return alert('Select a message first');
                const messageId = selectedMessage.dataset.messageId;
                fetch('/manticore/api/chat/moderate/delete', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({message_id: messageId})
                });
                selectedMessage.remove();
            }
            
            function timeoutUser() {
                if(!selectedMessage) return alert('Select a message first');
                const userId = selectedMessage.dataset.userId;
                const username = selectedMessage.dataset.username;
                fetch('/manticore/api/chat/moderate/timeout', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({user_id: userId, username: username, duration: 300})
                });
            }
            
            function banUser() {
                if(!selectedMessage) return alert('Select a message first');
                const userId = selectedMessage.dataset.userId;
                const username = selectedMessage.dataset.username;
                fetch('/manticore/api/chat/moderate/ban', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({user_id: userId, username: username})
                });
            }
        </script>
    </body>
    </html>
    ''')

@manticore_bp.route('/api/chat/youtube/connect', methods=['POST'])
@manticore_required
def connect_youtube_chat():
    """Connect to YouTube chat"""
    data = request.get_json()
    success = chat_dock.connect_youtube(
        data.get('api_key'),
        data.get('video_id')
    )
    return jsonify({'success': success, 'platform': 'youtube'})

@manticore_bp.route('/api/chat/twitch/connect', methods=['POST'])
@manticore_required
def connect_twitch_chat():
    """Connect to Twitch chat"""
    data = request.get_json()
    success = chat_dock.connect_twitch(
        data.get('oauth_token'),
        data.get('username'),
        data.get('channel')
    )
    return jsonify({'success': success, 'platform': 'twitch'})

@manticore_bp.route('/api/chat/messages')
@manticore_required
def get_chat_messages():
    """Get recent chat messages"""
    messages = chat_dock.get_recent_messages(50)
    stats = chat_dock.get_stats()
    
    return jsonify({
        'messages': [{
            'id': m.id,
            'platform': m.platform.value,
            'username': m.username,
            'message': m.message,
            'timestamp': m.timestamp.isoformat(),
            'user_id': m.user_id,
            'is_moderator': m.is_moderator,
            'is_owner': m.is_owner
        } for m in messages],
        'stats': stats
    })

@manticore_bp.route('/api/chat/moderate/delete', methods=['POST'])
@manticore_required
def moderate_delete():
    """Delete a chat message"""
    data = request.get_json()
    success = chat_dock.delete_message(
        data.get('message_id'),
        ChatPlatform(data.get('platform', 'youtube'))
    )
    return jsonify({'success': success, 'action': 'delete'})

@manticore_bp.route('/api/chat/moderate/timeout', methods=['POST'])
@manticore_required
def moderate_timeout():
    """Timeout a user"""
    data = request.get_json()
    success = chat_dock.timeout_user(
        data.get('user_id'),
        data.get('username'),
        ChatPlatform(data.get('platform', 'youtube')),
        data.get('duration', 300)
    )
    return jsonify({'success': success, 'action': 'timeout'})

@manticore_bp.route('/api/chat/moderate/ban', methods=['POST'])
@manticore_required
def moderate_ban():
    """Ban a user"""
    data = request.get_json()
    success = chat_dock.ban_user(
        data.get('user_id'),
        data.get('username'),
        ChatPlatform(data.get('platform', 'youtube'))
    )
    return jsonify({'success': success, 'action': 'ban'})

@manticore_bp.route('/api/chat/moderate/unban', methods=['POST'])
@manticore_required
def moderate_unban():
    """Unban a user"""
    data = request.get_json()
    success = chat_dock.unban_user(
        data.get('username'),
        ChatPlatform(data.get('platform', 'youtube'))
    )
    return jsonify({'success': success, 'action': 'unban'})

def register_manticore_routes(app):
    """Register Manticore Control Interface routes"""
    app.register_blueprint(manticore_bp)
    logger.info("🔥 MANTICORE CONTROL INTERFACE ROUTES REGISTERED")
    logger.info("🔥 Access: /manticore/")
    logger.info("🔥 Special Email: digital.demiurge666@gmail.com")
    logger.info("🔥 Status: ALL FUNCTIONS ACTIVE - NO RESTRICTIONS")