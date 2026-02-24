import asyncio
import websockets
import json
import logging
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime
import threading
import time
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class OBSScene:
    """OBS Scene data structure"""
    name: str
    sources: List[Dict] = None
    is_active: bool = False
    
    def __post_init__(self):
        if self.sources is None:
            self.sources = []

@dataclass
class OBSSource:
    """OBS Source data structure"""
    name: str
    type: str
    settings: Dict = None
    visible: bool = True
    muted: bool = False
    
    def __post_init__(self):
        if self.settings is None:
            self.settings = {}

class OBSWebSocketManager:
    """OBS WebSocket client for controlling OBS Studio"""
    
    def __init__(self, host: str = "localhost", port: int = 4455, password: str = None):
        self.host = host
        self.port = port
        self.password = password
        self.websocket = None
        self.is_connected = False
        self.message_id = 1
        self.response_handlers = {}
        self.event_handlers = {}
        self.scenes = {}
        self.current_scene = None
        self.sources = {}
        
        # WebSocket URL
        self.ws_url = f"ws://{host}:{port}"
        
    async def connect(self) -> bool:
        """Connect to OBS WebSocket server"""
        try:
            self.websocket = await websockets.connect(self.ws_url)
            self.is_connected = True
            
            # Start listening for messages
            asyncio.create_task(self._message_listener())
            
            # Authenticate if password is provided
            if self.password:
                await self._authenticate()
            
            # Get current scenes and sources
            await self._get_scenes()
            await self._get_sources()
            
            logger.info(f"Connected to OBS WebSocket at {self.ws_url}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect to OBS WebSocket: {e}")
            self.is_connected = False
            return False
    
    async def disconnect(self):
        """Disconnect from OBS WebSocket server"""
        if self.websocket:
            await self.websocket.close()
            self.is_connected = False
            logger.info("Disconnected from OBS WebSocket")
    
    async def _authenticate(self):
        """Authenticate with OBS WebSocket"""
        try:
            auth_req = await self._send_request("GetAuthRequired")
            if auth_req.get('authRequired'):
                auth_response = await self._send_request(
                    "Authenticate",
                    {"auth": self._generate_auth_hash(auth_req['challenge'], auth_req['salt'])}
                )
                
                if not auth_response.get('authenticated'):
                    raise Exception("Authentication failed")
                    
        except Exception as e:
            logger.error(f"OBS authentication failed: {e}")
            raise
    
    def _generate_auth_hash(self, challenge: str, salt: str) -> str:
        """Generate authentication hash"""
        import hashlib
        import base64
        
        # Concatenate password with salt
        password_salt = self.password + salt
        password_hash = hashlib.sha256(password_salt.encode('utf-8')).hexdigest()
        
        # Concatenate hash with challenge
        auth_string = password_hash + challenge
        auth_hash = hashlib.sha256(auth_string.encode('utf-8')).hexdigest()
        
        return base64.b64encode(auth_hash.encode('utf-8')).decode('utf-8')
    
    async def _send_request(self, request_type: str, request_data: Dict = None) -> Dict:
        """Send a request to OBS WebSocket"""
        if not self.is_connected or not self.websocket:
            raise Exception("Not connected to OBS WebSocket")
        
        message_id = str(self.message_id)
        self.message_id += 1
        
        request = {
            "request-type": request_type,
            "message-id": message_id
        }
        
        if request_data:
            request.update(request_data)
        
        # Send request
        await self.websocket.send(json.dumps(request))
        
        # Wait for response
        future = asyncio.Future()
        self.response_handlers[message_id] = future
        
        try:
            response = await asyncio.wait_for(future, timeout=10.0)
            return response
        except asyncio.TimeoutError:
            del self.response_handlers[message_id]
            raise Exception(f"Request timeout for {request_type}")
    
    async def _message_listener(self):
        """Listen for WebSocket messages"""
        try:
            async for message in self.websocket:
                data = json.loads(message)
                
                # Handle responses
                if 'message-id' in data:
                    message_id = data['message-id']
                    if message_id in self.response_handlers:
                        future = self.response_handlers.pop(message_id)
                        future.set_result(data)
                
                # Handle events
                elif 'update-type' in data:
                    await self._handle_event(data)
                    
        except websockets.exceptions.ConnectionClosed:
            logger.warning("OBS WebSocket connection closed")
            self.is_connected = False
        except Exception as e:
            logger.error(f"Error in WebSocket message listener: {e}")
    
    async def _handle_event(self, event: Dict):
        """Handle OBS WebSocket events"""
        event_type = event.get('update-type')
        
        if event_type == 'ScenesChanged':
            await self._get_scenes()
        elif event_type == 'SwitchScenes':
            scene_name = event.get('scene-name')
            self._update_current_scene(scene_name)
        elif event_type == 'SourceMuteStateChanged':
            source_name = event.get('sourceName')
            is_muted = event.get('sourceMuted', False)
            self._update_source_mute_state(source_name, is_muted)
        elif event_type == 'SourceVisibilityChanged':
            source_name = event.get('itemName')
            is_visible = event.get('itemVisible', False)
            self._update_source_visibility(source_name, is_visible)
        
        # Call registered event handlers
        if event_type in self.event_handlers:
            for handler in self.event_handlers[event_type]:
                try:
                    await handler(event)
                except Exception as e:
                    logger.error(f"Error in event handler for {event_type}: {e}")
    
    def register_event_handler(self, event_type: str, handler: Callable):
        """Register an event handler"""
        if event_type not in self.event_handlers:
            self.event_handlers[event_type] = []
        self.event_handlers[event_type].append(handler)
    
    async def _get_scenes(self):
        """Get all scenes from OBS"""
        try:
            response = await self._send_request("GetSceneList")
            scenes_data = response.get('scenes', [])
            
            self.scenes = {}
            for scene_data in scenes_data:
                scene = OBSScene(
                    name=scene_data['name'],
                    is_active=scene_data.get('current', False)
                )
                
                # Get scene sources
                scene_sources = await self._send_request(
                    "GetSceneItemList",
                    {"sceneName": scene.name}
                )
                
                if 'sceneItems' in scene_sources:
                    scene.sources = scene_sources['sceneItems']
                
                self.scenes[scene.name] = scene
                
                if scene.is_active:
                    self.current_scene = scene.name
                    
        except Exception as e:
            logger.error(f"Failed to get scenes: {e}")
    
    async def _get_sources(self):
        """Get all sources from OBS"""
        try:
            response = await self._send_request("GetSourcesList")
            sources_data = response.get('sources', [])
            
            self.sources = {}
            for source_data in sources_data:
                source = OBSSource(
                    name=source_data['name'],
                    type=source_data['type'],
                    settings=source_data.get('settings', {}),
                    visible=source_data.get('render', True),
                    muted=source_data.get('muted', False)
                )
                self.sources[source.name] = source
                
        except Exception as e:
            logger.error(f"Failed to get sources: {e}")
    
    def _update_current_scene(self, scene_name: str):
        """Update current scene"""
        if scene_name in self.scenes:
            # Set all scenes as inactive
            for scene in self.scenes.values():
                scene.is_active = False
            
            # Set current scene as active
            self.scenes[scene_name].is_active = True
            self.current_scene = scene_name
    
    def _update_source_visibility(self, source_name: str, is_visible: bool):
        """Update source visibility"""
        if source_name in self.sources:
            self.sources[source_name].visible = is_visible
    
    def _update_source_mute_state(self, source_name: str, is_muted: bool):
        """Update source mute state"""
        if source_name in self.sources:
            self.sources[source_name].muted = is_muted
    
    # Scene Management Methods
    async def create_scene(self, scene_name: str) -> bool:
        """Create a new scene"""
        try:
            await self._send_request("CreateScene", {"sceneName": scene_name})
            await self._get_scenes()  # Refresh scenes
            return True
        except Exception as e:
            logger.error(f"Failed to create scene {scene_name}: {e}")
            return False
    
    async def delete_scene(self, scene_name: str) -> bool:
        """Delete a scene"""
        try:
            await self._send_request("DeleteScene", {"sceneName": scene_name})
            await self._get_scenes()  # Refresh scenes
            return True
        except Exception as e:
            logger.error(f"Failed to delete scene {scene_name}: {e}")
            return False
    
    async def switch_scene(self, scene_name: str) -> bool:
        """Switch to a specific scene"""
        try:
            await self._send_request("SetCurrentScene", {"scene-name": scene_name})
            self._update_current_scene(scene_name)
            return True
        except Exception as e:
            logger.error(f"Failed to switch to scene {scene_name}: {e}")
            return False
    
    async def get_current_scene(self) -> str:
        """Get the current scene name"""
        return self.current_scene
    
    # Source Management Methods
    async def create_source(self, source_name: str, source_type: str, settings: Dict = None) -> bool:
        """Create a new source"""
        try:
            source_data = {
                "sourceName": source_name,
                "sourceType": source_type
            }
            
            if settings:
                source_data["sourceSettings"] = settings
            
            await self._send_request("CreateSource", source_data)
            await self._get_sources()  # Refresh sources
            return True
        except Exception as e:
            logger.error(f"Failed to create source {source_name}: {e}")
            return False
    
    async def delete_source(self, source_name: str) -> bool:
        """Delete a source"""
        try:
            await self._send_request("DeleteSource", {"sourceName": source_name})
            await self._get_sources()  # Refresh sources
            return True
        except Exception as e:
            logger.error(f"Failed to delete source {source_name}: {e}")
            return False
    
    async def set_source_visibility(self, source_name: str, visible: bool, scene_name: str = None) -> bool:
        """Set source visibility"""
        try:
            await self._send_request(
                "SetSceneItemRender",
                {
                    "source": source_name,
                    "render": visible,
                    "scene-name": scene_name or self.current_scene
                }
            )
            self._update_source_visibility(source_name, visible)
            return True
        except Exception as e:
            logger.error(f"Failed to set visibility for source {source_name}: {e}")
            return False
    
    async def set_source_mute(self, source_name: str, muted: bool) -> bool:
        """Set source mute state"""
        try:
            await self._send_request(
                "SetMute",
                {
                    "source": source_name,
                    "mute": muted
                }
            )
            self._update_source_mute_state(source_name, muted)
            return True
        except Exception as e:
            logger.error(f"Failed to set mute state for source {source_name}: {e}")
            return False
    
    # Streaming Control Methods
    async def start_streaming(self) -> bool:
        """Start streaming"""
        try:
            await self._send_request("StartStreaming")
            logger.info("OBS streaming started")
            return True
        except Exception as e:
            logger.error(f"Failed to start streaming: {e}")
            return False
    
    async def stop_streaming(self) -> bool:
        """Stop streaming"""
        try:
            await self._send_request("StopStreaming")
            logger.info("OBS streaming stopped")
            return True
        except Exception as e:
            logger.error(f"Failed to stop streaming: {e}")
            return False
    
    async def start_recording(self) -> bool:
        """Start recording"""
        try:
            await self._send_request("StartRecording")
            logger.info("OBS recording started")
            return True
        except Exception as e:
            logger.error(f"Failed to start recording: {e}")
            return False
    
    async def stop_recording(self) -> bool:
        """Stop recording"""
        try:
            await self._send_request("StopRecording")
            logger.info("OBS recording stopped")
            return True
        except Exception as e:
            logger.error(f"Failed to stop recording: {e}")
            return False
    
    # Audio Methods
    async def get_audio_levels(self) -> Dict:
        """Get audio levels for all sources"""
        try:
            response = await self._send_request("GetAudioLevels")
            return response.get('levels', {})
        except Exception as e:
            logger.error(f"Failed to get audio levels: {e}")
            return {}
    
    async def set_source_volume(self, source_name: str, volume: float) -> bool:
        """Set source volume (0.0 - 1.0)"""
        try:
            volume_db = -60 + (volume * 60)  # Convert to decibels
            await self._send_request(
                "SetVolume",
                {
                    "source": source_name,
                    "volume": volume_db
                }
            )
            return True
        except Exception as e:
            logger.error(f"Failed to set volume for source {source_name}: {e}")
            return False
    
    # Scene Item Methods
    async def add_source_to_scene(self, scene_name: str, source_name: str, x: int = 0, y: int = 0) -> bool:
        """Add source to scene"""
        try:
            await self._send_request(
                "AddSceneItem",
                {
                    "sceneName": scene_name,
                    "sourceName": source_name,
                    "x": x,
                    "y": y
                }
            )
            await self._get_scenes()  # Refresh scenes
            return True
        except Exception as e:
            logger.error(f"Failed to add source {source_name} to scene {scene_name}: {e}")
            return False
    
    async def remove_source_from_scene(self, scene_name: str, item_id: int) -> bool:
        """Remove source from scene"""
        try:
            await self._send_request(
                "DeleteSceneItem",
                {
                    "scene-name": scene_name,
                    "item": item_id
                }
            )
            await self._get_scenes()  # Refresh scenes
            return True
        except Exception as e:
            logger.error(f"Failed to remove item {item_id} from scene {scene_name}: {e}")
            return False
    
    # Preset Methods
    async def create_transition_preset(self, preset_name: str, scene_data: Dict) -> bool:
        """Create a transition preset"""
        try:
            # This would store preset data in local storage
            # For now, we'll simulate it
            logger.info(f"Created transition preset: {preset_name}")
            return True
        except Exception as e:
            logger.error(f"Failed to create preset {preset_name}: {e}")
            return False
    
    async def apply_transition_preset(self, preset_name: str) -> bool:
        """Apply a transition preset"""
        try:
            # This would retrieve and apply preset data
            logger.info(f"Applied transition preset: {preset_name}")
            return True
        except Exception as e:
            logger.error(f"Failed to apply preset {preset_name}: {e}")
            return False

class OBSSceneManager:
    """High-level OBS scene and source manager"""
    
    def __init__(self, obs_manager: OBSWebSocketManager):
        self.obs = obs_manager
        
    async def create_interview_scene(self, scene_name: str, camera_sources: List[str]) -> bool:
        """Create an interview scene with multiple cameras"""
        try:
            # Create scene
            await self.obs.create_scene(scene_name)
            
            # Add camera sources in layout
            for i, source_name in enumerate(camera_sources):
                x_pos = i * 320  # Position cameras side by side
                await self.obs.add_source_to_scene(scene_name, source_name, x_pos, 0)
            
            # Add overlay text
            await self.obs.create_source(
                f"{scene_name}_title",
                "text_source_v2",
                {"text": "INTERVIEW - LIVE", "font_size": 48}
            )
            await self.obs.add_source_to_scene(scene_name, f"{scene_name}_title", 10, 10)
            
            return True
        except Exception as e:
            logger.error(f"Failed to create interview scene {scene_name}: {e}")
            return False
    
    async def create_gaming_scene(self, scene_name: str, game_capture: str, webcam: str = None) -> bool:
        """Create a gaming scene with game capture and optional webcam"""
        try:
            # Create scene
            await self.obs.create_scene(scene_name)
            
            # Add game capture as main source
            await self.obs.add_source_to_scene(scene_name, game_capture, 0, 0)
            
            # Add webcam overlay if provided
            if webcam:
                await self.obs.add_source_to_scene(scene_name, webcam, 1100, 600)
                
                # Scale down webcam
                await self.obs._send_request(
                    "SetSceneItemTransform",
                    {
                        "scene-name": scene_name,
                        "item": webcam,
                        "scale": {"x": 0.3, "y": 0.3}
                    }
                )
            
            return True
        except Exception as e:
            logger.error(f"Failed to create gaming scene {scene_name}: {e}")
            return False
    
    async def create_presentation_scene(self, scene_name: str, display_source: str, speaker_source: str = None) -> bool:
        """Create a presentation scene with slides and speaker"""
        try:
            # Create scene
            await self.obs.create_scene(scene_name)
            
            # Add display capture for slides
            await self.obs.add_source_to_scene(scene_name, display_source, 0, 0)
            
            # Add speaker picture-in-picture if provided
            if speaker_source:
                await self.obs.add_source_to_scene(scene_name, speaker_source, 1200, 50)
                
                # Scale down speaker video
                await self.obs._send_request(
                    "SetSceneItemTransform",
                    {
                        "scene-name": scene_name,
                        "item": speaker_source,
                        "scale": {"x": 0.25, "y": 0.25}
                    }
                )
            
            return True
        except Exception as e:
            logger.error(f"Failed to create presentation scene {scene_name}: {e}")
            return False

# Utility function for running OBS operations in background
def run_obs_coroutine(coro):
    """Run an OBS coroutine in a background thread"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()