import os
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
import uuid
import time

logger = logging.getLogger(__name__)

class SceneSource:
    """Represents a media source in a scene"""
    
    def __init__(self, id: str, name: str, source_type: str, settings: Dict):
        self.id = id
        self.name = name
        self.type = source_type
        self.settings = settings
        self.is_visible = True
        self.is_muted = False
        self.volume = 1.0
        self.position = {"x": 0, "y": 0}
        self.size = {"width": 1920, "height": 1080}
        self.rotation = 0
        self.crop = {"top": 0, "left": 0, "bottom": 1080, "right": 1920}
        self.created_at = datetime.utcnow()
        
    def set_position(self, x: int, y: int):
        self.position["x"] = x
        self.position["y"] = y
    
    def set_size(self, width: int, height: int):
        self.size["width"] = width
        self.size["height"] = height
    
    def set_visibility(self, visible: bool):
        self.is_visible = visible
    
    def set_mute(self, muted: bool):
        self.is_muted = muted
    
    def set_volume(self, volume: float):
        self.volume = max(0.0, min(1.0, volume))

class BroadcastScene:
    """Represents a complete scene with multiple sources"""
    
    def __init__(self, id: str, name: str, scene_type: str = "custom"):
        self.id = id
        self.name = name
        self.description = ""
        self.scene_type = scene_type
        self.sources = {}
        self.is_active = False
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
        
    def add_source(self, source: SceneSource):
        """Add a source to this scene"""
        self.sources[source.id] = source
        self.updated_at = datetime.utcnow()
        logger.info(f"Added source {source.name} to scene {self.name}")
    
    def remove_source(self, source_id: str):
        """Remove a source from this scene"""
        if source_id in self.sources:
            source_name = self.sources[source_id].name
            del self.sources[source_id]
            self.updated_at = datetime.utcnow()
            logger.info(f"Removed source {source_name} from scene {self.name}")
            return True
        return False
    
    def get_source(self, source_id: str) -> Optional[SceneSource]:
        """Get a specific source"""
        return self.sources.get(source_id)
    
    def get_all_sources(self) -> List[SceneSource]:
        """Get all sources in this scene"""
        return list(self.sources.values())
    
    def set_active(self, active: bool):
        """Set this scene as active"""
        self.is_active = active
        if active:
            logger.info(f"Activated scene: {self.name}")
    
    def to_dict(self) -> Dict:
        """Convert scene to dictionary"""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "scene_type": self.scene_type,
            "is_active": self.is_active,
            "sources": {sid: self._source_to_dict(source) for sid, source in self.sources.items()},
            "source_count": len(self.sources),
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }
    
    def _source_to_dict(self, source: SceneSource) -> Dict:
        """Convert source to dictionary"""
        return {
            "id": source.id,
            "name": source.name,
            "type": source.type,
            "is_visible": source.is_visible,
            "is_muted": source.is_muted,
            "volume": source.volume,
            "position": source.position,
            "size": source.size,
            "rotation": source.rotation,
            "crop": source.crop,
            "settings": source.settings,
            "created_at": source.created_at.isoformat()
        }

class SceneFactory:
    """Factory for creating predefined scene types"""
    
    @staticmethod
    def create_interview_scene(name: str, host_camera: str = "Main Camera", guest_camera: str = "Guest Camera") -> BroadcastScene:
        """Create an interview scene with split-screen layout"""
        scene = BroadcastScene(f"interview_{uuid.uuid4()}", name, "interview")
        scene.description = "Split-screen interview layout with two cameras and overlay"
        
        # Main camera (left side)
        main_cam = SceneSource(
            f"main_{uuid.uuid4()}",
            host_camera,
            "camera",
            {
                "device": "main",
                "resolution": "1280x720",
                "framerate": 30,
                "format": "YUV422"
            }
        )
        main_cam.set_position(0, 180)
        main_cam.set_size(960, 540)
        
        # Guest camera (right side)
        guest_cam = SceneSource(
            f"guest_{uuid.uuid4()}",
            guest_camera,
            "camera", 
            {
                "device": "guest",
                "resolution": "1280x720",
                "framerate": 30,
                "format": "YUV422"
            }
        )
        guest_cam.set_position(960, 180)
        guest_cam.set_size(960, 540)
        
        # Interview title overlay
        title_overlay = SceneSource(
            f"title_{uuid.uuid4()}",
            "Interview Title",
            "text",
            {
                "text": "LIVE INTERVIEW",
                "font_size": 48,
                "font_family": "Arial",
                "color": "#00ff41",
                "bold": True,
                "background_color": "rgba(0,0,0,0.7)"
            }
        )
        title_overlay.set_position(50, 50)
        
        # Scene info overlay
        info_overlay = SceneSource(
            f"info_{uuid.uuid4()}",
            "Scene Info",
            "text",
            {
                "text": "Matrix Broadcast Studio",
                "font_size": 24,
                "font_family": "Arial",
                "color": "#ffffff",
                "background_color": "rgba(0,255,65,0.3)"
            }
        )
        info_overlay.set_position(50, 100)
        
        # Add all sources to scene
        scene.add_source(main_cam)
        scene.add_source(guest_cam)
        scene.add_source(title_overlay)
        scene.add_source(info_overlay)
        
        return scene
    
    @staticmethod
    def create_gaming_scene(name: str, game_source: str = "Game Capture", webcam_source: str = "Webcam") -> BroadcastScene:
        """Create a gaming scene with game capture and webcam overlay"""
        scene = BroadcastScene(f"gaming_{uuid.uuid4()}", name, "gaming")
        scene.description = "Gaming layout with full game capture and webcam overlay"
        
        # Game capture (full screen)
        game_capture = SceneSource(
            f"game_{uuid.uuid4()}",
            game_source,
            "display",
            {
                "display": "primary",
                "capture_mode": "game",
                "resolution": "1920x1080",
                "fps": 60,
                "hdr": False
            }
        )
        game_capture.set_position(0, 0)
        game_capture.set_size(1920, 1080)
        
        # Webcam overlay (bottom right)
        webcam = SceneSource(
            f"webcam_{uuid.uuid4()}",
            webcam_source,
            "camera",
            {
                "device": "webcam",
                "resolution": "640x480",
                "framerate": 30,
                "mirror": True
            }
        )
        webcam.set_position(1280, 20)
        webcam.set_size(640, 480)
        
        # Stream overlay
        stream_overlay = SceneSource(
            f"overlay_{uuid.uuid4()}",
            "Stream Overlay",
            "text",
            {
                "text": "🎮 LIVE GAMING",
                "font_size": 36,
                "font_family": "Arial",
                "color": "#ff4444",
                "bold": True,
                "background_color": "rgba(0,0,0,0.7)"
            }
        )
        stream_overlay.set_position(20, 980)
        
        # Chat integration source
        chat_source = SceneSource(
            f"chat_{uuid.uuid4()}",
            "Chat Integration",
            "browser",
            {
                "url": "https://twitch.tv/chat/channel",
                "width": 400,
                "height": 600,
                "css": "background: rgba(0,0,0,0.8);"
            }
        )
        chat_source.set_position(20, 380)
        
        scene.add_source(game_capture)
        scene.add_source(webcam)
        scene.add_source(stream_overlay)
        scene.add_source(chat_source)
        
        return scene
    
    @staticmethod
    def create_presentation_scene(name: str, slides_source: str = "Slides", speaker_source: str = "Speaker") -> BroadcastScene:
        """Create a presentation scene with slides and speaker"""
        scene = BroadcastScene(f"presentation_{uuid.uuid4()}", name, "presentation")
        scene.description = "Presentation layout with slides and speaker picture-in-picture"
        
        # Slides (main content)
        slides = SceneSource(
            f"slides_{uuid.uuid4()}",
            slides_source,
            "display",
            {
                "display": "secondary",
                "capture_mode": "window",
                "window_name": "PowerPoint",
                "resolution": "1920x1080",
                "fps": 30
            }
        )
        slides.set_position(0, 0)
        slides.set_size(1920, 1080)
        
        # Speaker picture-in-picture (top right)
        speaker = SceneSource(
            f"speaker_{uuid.uuid4()}",
            speaker_source,
            "camera",
            {
                "device": "speaker_cam",
                "resolution": "640x480",
                "framerate": 30,
                "green_screen": False
            }
        )
        speaker.set_position(20, 20)
        speaker.set_size(320, 240)
        
        # Presentation title
        pres_title = SceneSource(
            f"title_{uuid.uuid4()}",
            "Presentation Title",
            "text",
            {
                "text": "PRESENTATION MODE",
                "font_size": 42,
                "font_family": "Arial",
                "color": "#00ff41",
                "bold": True,
                "background_color": "rgba(0,0,0,0.7)"
            }
        )
        pres_title.set_position(350, 20)
        
        # Progress bar
        progress_bar = SceneSource(
            f"progress_{uuid.uuid4()}",
            "Progress Bar",
            "image",
            {
                "image_path": "progress_bar.png",
                "width": 1280,
                "height": 20
            }
        )
        progress_bar.set_position(320, 1060)
        
        scene.add_source(slides)
        scene.add_source(speaker)
        scene.add_source(pres_title)
        scene.add_source(progress_bar)
        
        return scene
    
    @staticmethod
    def create_talking_head_scene(name: str, speaker_source: str = "Speaker") -> BroadcastScene:
        """Create a talking head scene"""
        scene = BroadcastScene(f"talking_head_{uuid.uuid4()}", name, "talking_head")
        scene.description = "Simple talking head layout centered"
        
        # Main speaker (centered)
        speaker = SceneSource(
            f"speaker_{uuid.uuid4()}",
            speaker_source,
            "camera",
            {
                "device": "main",
                "resolution": "1920x1080",
                "framerate": 30,
                "blur_background": False
            }
        )
        speaker.set_position(0, 0)
        speaker.set_size(1920, 1080)
        
        # Name title
        name_title = SceneSource(
            f"name_{uuid.uuid4()}",
            "Name Title",
            "text",
            {
                "text": speaker_source,
                "font_size": 64,
                "font_family": "Arial",
                "color": "#ffffff",
                "bold": True,
                "outline_color": "#000000",
                "outline_width": 3
            }
        )
        name_title.set_position(100, 900)
        
        # Live indicator
        live_indicator = SceneSource(
            f"live_{uuid.uuid4()}",
            "Live Indicator",
            "text",
            {
                "text": "🔴 LIVE",
                "font_size": 36,
                "font_family": "Arial",
                "color": "#ff0000",
                "bold": True,
                "blink": True
            }
        )
        live_indicator.set_position(1600, 50)
        
        scene.add_source(speaker)
        scene.add_source(name_title)
        scene.add_source(live_indicator)
        
        return scene
    
    @staticmethod
    def create_green_screen_scene(name: str, talent_source: str = "Talent") -> BroadcastScene:
        """Create a green screen scene"""
        scene = BroadcastScene(f"green_screen_{uuid.uuid4()}", name, "green_screen")
        scene.description = "Green screen layout for chroma keying"
        
        # Green screen background
        green_bg = SceneSource(
            f"green_{uuid.uuid4()}",
            "Green Background",
            "color",
            {
                "color": "#00ff00",
                "width": 1920,
                "height": 1080
            }
        )
        green_bg.set_position(0, 0)
        green_bg.set_size(1920, 1080)
        
        # Talent (will be chroma keyed)
        talent = SceneSource(
            f"talent_{uuid.uuid4()}",
            talent_source,
            "camera",
            {
                "device": "main",
                "resolution": "1920x1080",
                "framerate": 30,
                "chroma_key": "#00ff00",
                "chroma_smoothing": 5
            }
        )
        talent.set_position(0, 0)
        talent.set_size(1920, 1080)
        
        # Green screen indicator
        gs_indicator = SceneSource(
            f"gs_{uuid.uuid4()}",
            "Green Screen Active",
            "text",
            {
                "text": "🟢 GREEN SCREEN",
                "font_size": 28,
                "font_family": "Arial",
                "color": "#00ff00",
                "bold": True
            }
        )
        gs_indicator.set_position(1600, 20)
        
        scene.add_source(green_bg)
        scene.add_source(talent)
        scene.add_source(gs_indicator)
        
        return scene

class SceneManager:
    """Manages all scenes and sources"""
    
    def __init__(self):
        self.scenes = {}
        self.active_scene_id = None
        self.current_stream = None
        
        # Create default scenes
        self._create_default_scenes()
        
    def _create_default_scenes(self):
        """Create default scenes"""
        # Interview scene
        interview = SceneFactory.create_interview_scene("Interview Setup")
        self.scenes[interview.id] = interview
        
        # Gaming scene
        gaming = SceneFactory.create_gaming_scene("Gaming Stream")
        self.scenes[gaming.id] = gaming
        
        # Presentation scene
        presentation = SceneFactory.create_presentation_scene("Presentation Mode")
        self.scenes[presentation.id] = presentation
        
        # Talking head scene
        talking_head = SceneFactory.create_talking_head_scene("Talking Head")
        self.scenes[talking_head.id] = talking_head
        
        # Green screen scene
        green_screen = SceneFactory.create_green_screen_scene("Green Screen")
        self.scenes[green_screen.id] = green_screen
        
        # Set default active scene
        interview.set_active(True)
        self.active_scene_id = interview.id
        
        logger.info("Created default scenes")
    
    def create_scene(self, name: str, scene_type: str, description: str = "") -> BroadcastScene:
        """Create a new scene"""
        scene_id = str(uuid.uuid4())
        scene = BroadcastScene(scene_id, name, scene_type)
        scene.description = description
        self.scenes[scene_id] = scene
        
        logger.info(f"Created new scene: {name}")
        return scene
    
    def delete_scene(self, scene_id: str) -> bool:
        """Delete a scene"""
        if scene_id in self.scenes:
            # Don't allow deletion of active scene
            if scene_id == self.active_scene_id:
                logger.error("Cannot delete active scene")
                return False
            
            scene_name = self.scenes[scene_id].name
            del self.scenes[scene_id]
            logger.info(f"Deleted scene: {scene_name}")
            return True
        
        return False
    
    def switch_scene(self, scene_id: str) -> bool:
        """Switch to a different scene"""
        if scene_id not in self.scenes:
            logger.error(f"Scene not found: {scene_id}")
            return False
        
        # Deactivate current scene
        if self.active_scene_id:
            self.scenes[self.active_scene_id].set_active(False)
        
        # Activate new scene
        self.scenes[scene_id].set_active(True)
        self.active_scene_id = scene_id
        
        logger.info(f"Switched to scene: {self.scenes[scene_id].name}")
        return True
    
    def add_source_to_scene(self, scene_id: str, source_type: str, name: str, settings: Dict) -> Optional[SceneSource]:
        """Add a new source to a scene"""
        if scene_id not in self.scenes:
            logger.error(f"Scene not found: {scene_id}")
            return None
        
        scene = self.scenes[scene_id]
        
        # Create new source
        source_id = str(uuid.uuid4())
        source = SceneSource(source_id, name, source_type, settings)
        
        # Add source based on type
        if source_type == "camera":
            source.set_position(100, 100)
            source.set_size(640, 480)
        elif source_type == "microphone":
            source.settings.update({
                "device": "default",
                "sample_rate": 44100,
                "channels": 2,
                "bitrate": 128
            })
        elif source_type == "display":
            source.set_position(0, 0)
            source.set_size(1920, 1080)
        elif source_type == "image":
            source.settings.update({
                "image_path": "",
                "scale_mode": "fit",
                "opacity": 1.0
            })
        elif source_type == "video":
            source.settings.update({
                "video_path": "",
                "loop": True,
                "audio": True
            })
        elif source_type == "text":
            source.settings.update({
                "text": name,
                "font_size": 48,
                "font_family": "Arial",
                "color": "#00ff41",
                "background_color": "transparent"
            })
        elif source_type == "browser":
            source.settings.update({
                "url": "https://example.com",
                "width": 800,
                "height": 600,
                "css": ""
            })
        elif source_type == "color":
            source.set_position(0, 0)
            source.set_size(1920, 1080)
            source.settings.update({
                "color": "#000000"
            })
        
        scene.add_source(source)
        return source
    
    def remove_source_from_scene(self, scene_id: str, source_id: str) -> bool:
        """Remove a source from a scene"""
        if scene_id not in self.scenes:
            return False
        
        return self.scenes[scene_id].remove_source(source_id)
    
    def get_scene(self, scene_id: str) -> Optional[BroadcastScene]:
        """Get a specific scene"""
        return self.scenes.get(scene_id)
    
    def get_all_scenes(self) -> List[BroadcastScene]:
        """Get all scenes"""
        return list(self.scenes.values())
    
    def get_active_scene(self) -> Optional[BroadcastScene]:
        """Get the currently active scene"""
        if self.active_scene_id:
            return self.scenes.get(self.active_scene_id)
        return None
    
    def update_source_properties(self, scene_id: str, source_id: str, properties: Dict) -> bool:
        """Update source properties"""
        scene = self.get_scene(scene_id)
        if not scene:
            return False
        
        source = scene.get_source(source_id)
        if not source:
            return False
        
        # Update properties
        for key, value in properties.items():
            if hasattr(source, key):
                setattr(source, key, value)
            elif key in source.settings:
                source.settings[key] = value
        
        logger.info(f"Updated properties for source {source.name}")
        return True
    
    def duplicate_scene(self, scene_id: str, new_name: str) -> Optional[BroadcastScene]:
        """Duplicate an existing scene"""
        original_scene = self.get_scene(scene_id)
        if not original_scene:
            return None
        
        # Create new scene with same properties
        new_scene = BroadcastScene(str(uuid.uuid4()), new_name, original_scene.scene_type)
        new_scene.description = f"Copy of {original_scene.name}"
        
        # Copy all sources
        for source in original_scene.get_all_sources():
            new_source = SceneSource(
                str(uuid.uuid4()),
                f"Copy of {source.name}",
                source.type,
                source.settings.copy()
            )
            new_source.position = source.position.copy()
            new_source.size = source.size.copy()
            new_source.is_visible = source.is_visible
            new_source.is_muted = source.is_muted
            new_source.volume = source.volume
            
            new_scene.add_source(new_source)
        
        self.scenes[new_scene.id] = new_scene
        logger.info(f"Duplicated scene: {original_scene.name} -> {new_name}")
        return new_scene
    
    def __getitem__(self, scene_id: str):
        """Get scene by ID (for compatibility)"""
        return self.get_scene(scene_id)
    
    def __setitem__(self, scene_id: str, value):
        """Set scene (for compatibility)"""
        self.scenes[scene_id] = value
    
    def get_scene_list_for_ui(self) -> Dict:
        """Get scene data formatted for UI"""
        scenes = []
        
        for scene in self.get_all_scenes():
            scenes.append({
                'id': scene.id,
                'name': scene.name,
                'description': scene.description,
                'scene_type': scene.scene_type,
                'is_active': scene.is_active,
                'sources': [self._source_to_dict(source) for source in scene.get_all_sources()],
                'created_at': scene.created_at.isoformat(),
                'updated_at': scene.updated_at.isoformat()
            })
        
        return {
            'scenes': scenes,
            'active_scene_id': self.active_scene_id,
            'total_scenes': len(scenes)
        }
    
    def get_all_sources_in_scene(self, scene_id: str) -> List[Dict]:
        """Get all sources in a specific scene"""
        scene = self.get_scene(scene_id)
        if scene:
            return [self._source_to_dict(source) for source in scene.get_all_sources()]
        return []
    
    def update_source_in_scene(self, scene_id: str, source_id: str, updates: Dict) -> bool:
        """Update a specific source in a scene"""
        scene = self.get_scene(scene_id)
        if not scene:
            return False
        
        source = scene.get_source(source_id)
        if not source:
            return False
        
        # Update source properties
        for key, value in updates.items():
            if key == 'position':
                source.set_position(value.get('x', 0), value.get('y', 0))
            elif key == 'size':
                source.set_size(value.get('width', 1920), value.get('height', 1080))
            elif key == 'is_visible':
                source.set_visibility(value)
            elif key == 'is_muted':
                source.set_mute(value)
            elif key == 'volume':
                source.set_volume(value)
            elif key == 'settings':
                source.settings.update(value)
        
        scene.updated_at = datetime.utcnow()
        logger.info(f"Updated source {source.name} in scene {scene.name}")
        return True
    
    def get_stream_status(self) -> Dict:
        """Get current streaming status"""
        active_scene = self.get_active_scene()
        
        status = {
            'is_streaming': self.current_stream is not None,
            'active_scene_id': self.active_scene_id,
            'active_scene_name': active_scene.name if active_scene else None,
            'active_scene_type': active_scene.scene_type if active_scene else None,
            'total_scenes': len(self.scenes),
            'total_sources': sum(len(scene.sources) for scene in self.scenes.values()),
            'timestamp': datetime.utcnow().isoformat()
        }
        
        if self.current_stream:
            status.update({
                'stream_id': self.current_stream.get('id'),
                'stream_title': self.current_stream.get('title'),
                'stream_platforms': self.current_stream.get('platforms', []),
                'viewer_count': self.current_stream.get('viewer_count', 0),
                'started_at': self.current_stream.get('started_at'),
                'duration': self._calculate_stream_duration()
            })
        
        return status
    
    def _calculate_stream_duration(self) -> str:
        """Calculate streaming duration"""
        if not self.current_stream or 'started_at' not in self.current_stream:
            return "00:00:00"
        
        started = datetime.fromisoformat(self.current_stream['started_at'])
        duration = datetime.utcnow() - started
        
        hours = int(duration.total_seconds() // 3600)
        minutes = int((duration.total_seconds() % 3600) // 60)
        seconds = int(duration.total_seconds() % 60)
        
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    
    def export_scene_config(self, scene_id: str) -> Optional[Dict]:
        """Export scene configuration"""
        scene = self.get_scene(scene_id)
        if not scene:
            return None
        
        return {
            'scene': scene.to_dict(),
            'exported_at': datetime.utcnow().isoformat(),
            'version': '1.0'
        }
    
    def import_scene_config(self, config: Dict) -> Optional[BroadcastScene]:
        """Import scene configuration"""
        try:
            scene_data = config.get('scene', {})
            
            # Create new scene
            scene = BroadcastScene(
                str(uuid.uuid4()),
                scene_data.get('name', 'Imported Scene'),
                scene_data.get('scene_type', 'custom')
            )
            scene.description = scene_data.get('description', '')
            
            # Import sources
            for source_data in scene_data.get('sources', {}).values():
                source = SceneSource(
                    str(uuid.uuid4()),
                    source_data.get('name', 'Imported Source'),
                    source_data.get('type', 'camera'),
                    source_data.get('settings', {})
                )
                
                # Apply properties
                if 'position' in source_data:
                    source.position = source_data['position']
                if 'size' in source_data:
                    source.size = source_data['size']
                if 'is_visible' in source_data:
                    source.is_visible = source_data['is_visible']
                if 'is_muted' in source_data:
                    source.is_muted = source_data['is_muted']
                if 'volume' in source_data:
                    source.volume = source_data['volume']
                
                scene.add_source(source)
            
            self.scenes[scene.id] = scene
            logger.info(f"Imported scene: {scene.name}")
            
            return scene
            
        except Exception as e:
            logger.error(f"Failed to import scene: {e}")
            return None

# Global scene manager instance
scene_manager = SceneManager()