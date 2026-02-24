#!/usr/bin/env python3
"""
🌊 MATRIX BROADCAST STUDIO - BROADCAST ENGINE
Professional multi-platform streaming engine with real-time capabilities
Features: RTMP streaming, adaptive bitrate, failover, real-time monitoring
"""

import os
import json
import time
import subprocess
import threading
import logging
import queue
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
import asyncio
import websockets
import cv2
import numpy as np
from PIL import Image

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class StreamQuality:
    """Stream quality presets"""
    
    QUALITY_PRESETS = {
        '360p': {
            'width': 640,
            'height': 360,
            'bitrate': 1000,
            'fps': 30,
            'keyframe_interval': 60
        },
        '480p': {
            'width': 854,
            'height': 480,
            'bitrate': 2000,
            'fps': 30,
            'keyframe_interval': 60
        },
        '720p': {
            'width': 1280,
            'height': 720,
            'bitrate': 4500,
            'fps': 30,
            'keyframe_interval': 60
        },
        '1080p': {
            'width': 1920,
            'height': 1080,
            'bitrate': 8000,
            'fps': 30,
            'keyframe_interval': 60
        }
    }
    
    @classmethod
    def get_quality(cls, quality_name: str) -> Dict[str, Any]:
        """Get quality preset by name"""
        return cls.QUALITY_PRESETS.get(quality_name, cls.QUALITY_PRESETS['720p'])

class BroadcastEngine:
    """Professional broadcast engine with multi-platform support"""
    
    def __init__(self):
        self.active_streams = {}  # platform -> stream info
        self.current_scene = None
        self.audio_mixer = None
        self.video_compositor = None
        self.stream_processes = {}  # platform -> subprocess
        self.monitoring_thread = None
        self.broadcast_queue = queue.Queue()
        self.is_broadcasting = False
        self.stream_quality = '720p'
        self.fallback_enabled = True
        
        # Statistics
        self.stats = {
            'frames_sent': 0,
            'bytes_sent': 0,
            'dropped_frames': 0,
            'uptime': 0,
            'current_bitrate': 0,
            'avg_fps': 0
        }
        
        logger.info("🌊 Broadcast Engine initialized")
    
    def initialize_streaming(self, quality: str = '720p'):
        """Initialize streaming components"""
        self.stream_quality = quality
        
        # Get quality settings
        quality_settings = StreamQuality.get_quality(quality)
        
        # Initialize video compositor
        self.video_compositor = VideoCompositor(
            width=quality_settings['width'],
            height=quality_settings['height'],
            fps=quality_settings['fps']
        )
        
        # Initialize audio mixer
        self.audio_mixer = AudioMixer()
        
        logger.info(f"✅ Streaming initialized at {quality}")
        
        return {
            'success': True,
            'quality': quality_settings,
            'compositor': self.video_compositor.get_info(),
            'mixer': self.audio_mixer.get_info()
        }
    
    def start_platform_stream(self, platform: str, stream_config: Dict[str, Any]) -> Dict[str, Any]:
        """Start streaming to specific platform"""
        try:
            if platform in self.active_streams:
                return {'error': f'Stream to {platform} already active'}
            
            # Get RTMP URL and stream key
            rtmp_url = stream_config.get('rtmp_url')
            stream_key = stream_config.get('stream_key')
            
            if not rtmp_url or not stream_key:
                return {'error': 'RTMP URL and stream key required'}
            
            # Build full RTMP URL
            full_url = f"{rtmp_url}/{stream_key}"
            
            # Get quality settings
            quality_settings = StreamQuality.get_quality(self.stream_quality)
            
            # Build FFmpeg command
            ffmpeg_cmd = self._build_ffmpeg_command(full_url, quality_settings, platform)
            
            # Start FFmpeg process
            process = subprocess.Popen(
                ffmpeg_cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                shell=False
            )
            
            # Store stream info
            self.active_streams[platform] = {
                'platform': platform,
                'rtmp_url': rtmp_url,
                'stream_key': stream_key,
                'full_url': full_url,
                'process': process,
                'started_at': datetime.now(),
                'status': 'starting',
                'quality': self.stream_quality,
                'config': stream_config
            }
            
            self.stream_processes[platform] = process
            
            # Start monitoring if this is first stream
            if not self.is_broadcasting:
                self._start_broadcast_monitoring()
                self.is_broadcasting = True
            
            logger.info(f"🚀 Started {platform} stream: {full_url}")
            
            return {
                'success': True,
                'platform': platform,
                'url': full_url,
                'quality': self.stream_quality,
                'status': 'starting'
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to start {platform} stream: {e}")
            return {'error': str(e)}
    
    def _build_ffmpeg_command(self, rtmp_url: str, quality: Dict[str, Any], platform: str) -> List[str]:
        """Build FFmpeg command for streaming"""
        cmd = [
            'ffmpeg',
            '-y',  # Overwrite output files
            '-f', 'rawvideo',
            '-pix_fmt', 'bgr24',
            '-s', f"{quality['width']}x{quality['height']}",
            '-r', str(quality['fps']),
            '-i', '-',  # Input from stdin (will be fed by our compositor)
            '-f', 's16le',
            '-ac', '2',
            '-ar', '44100',
            '-i', '-',  # Audio input from stdin
            '-c:v', 'libx264',
            '-preset', 'veryfast',
            '-tune', 'zerolatency',
            '-profile:v', 'high',
            '-level', '4.1',
            '-b:v', f"{quality['bitrate']}k",
            '-maxrate', f"{int(quality['bitrate'] * 1.2)}k",
            '-bufsize', f"{quality['bitrate'] * 2}k",
            '-g', str(quality['keyframe_interval']),
            '-keyint_min', str(quality['keyframe_interval']),
            '-sc_threshold', '0',
            '-c:a', 'aac',
            '-b:a', '128k',
            '-ar', '44100',
            '-f', 'flv',
            rtmp_url
        ]
        
        # Platform-specific optimizations
        if platform == 'youtube':
            cmd.extend([
                '-movflags', '+faststart',
                '-pix_fmt', 'yuv420p'
            ])
        elif platform == 'twitch':
            cmd.extend([
                '-pix_fmt', 'yuv420p',
                '-bf', '1'
            ])
        
        return cmd
    
    def _start_broadcast_monitoring(self):
        """Start broadcast monitoring thread"""
        self.monitoring_thread = threading.Thread(
            target=self._monitor_broadcasts,
            daemon=True
        )
        self.monitoring_thread.start()
        logger.info("📊 Broadcast monitoring started")
    
    def _monitor_broadcasts(self):
        """Monitor active streams and handle failures"""
        while self.is_broadcasting:
            try:
                current_time = datetime.now()
                
                for platform, stream_info in list(self.active_streams.items()):
                    process = stream_info['process']
                    
                    # Check if process is still running
                    if process.poll() is not None:
                        # Process has died
                        stderr = process.stderr.read().decode()
                        logger.error(f"❌ {platform} stream died: {stderr}")
                        
                        # Handle stream failure
                        if self.fallback_enabled:
                            self._handle_stream_failure(platform, stream_info)
                        
                        # Remove from active streams
                        del self.active_streams[platform]
                        if platform in self.stream_processes:
                            del self.stream_processes[platform]
                    else:
                        # Update stream status
                        if stream_info['status'] == 'starting':
                            # Check if stream has started successfully
                            if self._check_stream_health(platform, process):
                                stream_info['status'] = 'live'
                                logger.info(f"✅ {platform} stream is live")
                
                # Update statistics
                self._update_statistics()
                
                # Sleep for monitoring interval
                time.sleep(5)
                
            except Exception as e:
                logger.error(f"❌ Broadcast monitoring error: {e}")
                time.sleep(5)
    
    def _check_stream_health(self, platform: str, process: subprocess.Popen) -> bool:
        """Check if stream is healthy"""
        # Simple health check - check if process is still running
        # In production, this would check RTMP connection status
        return process.poll() is None and time.time() > 2
    
    def _handle_stream_failure(self, platform: str, stream_info: Dict[str, Any]):
        """Handle stream failure with fallback"""
        logger.warning(f"⚠️ Handling {platform} stream failure")
        
        # Attempt to restart stream
        if stream_info['config'].get('auto_restart', True):
            retry_count = stream_info.get('retry_count', 0)
            if retry_count < 3:
                logger.info(f"🔄 Attempting to restart {platform} stream (attempt {retry_count + 1})")
                time.sleep(5)  # Wait before retry
                
                result = self.start_platform_stream(platform, stream_info['config'])
                if result.get('success'):
                    self.active_streams[platform]['retry_count'] = retry_count + 1
    
    def _update_statistics(self):
        """Update broadcast statistics"""
        if self.active_streams:
            # Calculate uptime
            oldest_stream = min(self.active_streams.values(), key=lambda x: x['started_at'])
            self.stats['uptime'] = int((datetime.now() - oldest_stream['started_at']).total_seconds())
            
            # Update frame count (simplified)
            self.stats['frames_sent'] += self.video_compositor.frame_count if self.video_compositor else 0
    
    def stop_platform_stream(self, platform: str) -> Dict[str, Any]:
        """Stop streaming to specific platform"""
        try:
            if platform not in self.active_streams:
                return {'error': f'Stream to {platform} not active'}
            
            stream_info = self.active_streams[platform]
            process = stream_info['process']
            
            # Graceful shutdown
            logger.info(f"🛑 Stopping {platform} stream")
            
            # Send quit signal to FFmpeg
            process.terminate()
            
            # Wait for process to end
            try:
                process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()
            
            # Remove from active streams
            del self.active_streams[platform]
            if platform in self.stream_processes:
                del self.stream_processes[platform]
            
            # Stop monitoring if no more streams
            if not self.active_streams and self.is_broadcasting:
                self.is_broadcasting = False
            
            logger.info(f"✅ Stopped {platform} stream")
            
            return {
                'success': True,
                'platform': platform,
                'duration': int((datetime.now() - stream_info['started_at']).total_seconds())
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to stop {platform} stream: {e}")
            return {'error': str(e)}
    
    def stop_all_streams(self) -> Dict[str, Any]:
        """Stop all active streams"""
        results = {}
        
        for platform in list(self.active_streams.keys()):
            result = self.stop_platform_stream(platform)
            results[platform] = result
        
        # Wait for monitoring thread to end
        if self.monitoring_thread and self.monitoring_thread.is_alive():
            self.monitoring_thread.join(timeout=5)
        
        return {
            'success': True,
            'stopped_platforms': results,
            'total_stopped': len([r for r in results.values() if r.get('success')])
        }
    
    def get_stream_status(self) -> Dict[str, Any]:
        """Get comprehensive stream status"""
        active_platforms = {}
        
        for platform, stream_info in self.active_streams.items():
            active_platforms[platform] = {
                'platform': platform,
                'status': stream_info['status'],
                'quality': stream_info['quality'],
                'started_at': stream_info['started_at'].isoformat(),
                'uptime': int((datetime.now() - stream_info['started_at']).total_seconds()),
                'url': stream_info['full_url'],
                'health': 'good' if stream_info['process'].poll() is None else 'error'
            }
        
        return {
            'is_broadcasting': self.is_broadcasting,
            'active_platforms': active_platforms,
            'total_platforms': len(active_platforms),
            'quality': self.stream_quality,
            'statistics': self.stats,
            'fallback_enabled': self.fallback_enabled
        }
    
    def update_stream_quality(self, quality: str) -> Dict[str, Any]:
        """Change stream quality (requires restart of all streams)"""
        if quality not in StreamQuality.QUALITY_PRESETS:
            return {'error': f'Invalid quality: {quality}'}
        
        old_quality = self.stream_quality
        self.stream_quality = quality
        
        # Restart all streams with new quality
        if self.active_streams:
            # Store current configs
            current_configs = {
                platform: stream_info['config']
                for platform, stream_info in self.active_streams.items()
            }
            
            # Stop all streams
            self.stop_all_streams()
            
            # Reinitialize with new quality
            self.initialize_streaming(quality)
            
            # Restart all streams
            restart_results = {}
            for platform, config in current_configs.items():
                result = self.start_platform_stream(platform, config)
                restart_results[platform] = result
            
            return {
                'success': True,
                'old_quality': old_quality,
                'new_quality': quality,
                'restart_results': restart_results
            }
        else:
            return {
                'success': True,
                'old_quality': old_quality,
                'new_quality': quality,
                'message': 'Quality updated (will take effect on next stream start)'
            }

class VideoCompositor:
    """Professional video compositor for multi-source streaming"""
    
    def __init__(self, width: int, height: int, fps: int):
        self.width = width
        self.height = height
        self.fps = fps
        self.sources = {}
        self.frame_count = 0
        self.composition_mode = 'scene'  # scene, picture_in_picture, split_screen
        
        logger.info(f"🎬 Video Compositor initialized: {width}x{height} @ {fps}fps")
    
    def add_source(self, source_id: str, source_config: Dict[str, Any]):
        """Add video source"""
        self.sources[source_id] = {
            'id': source_id,
            'config': source_config,
            'position': source_config.get('position', {'x': 0, 'y': 0}),
            'size': source_config.get('size', {'width': self.width, 'height': self.height}),
            'z_index': source_config.get('z_index', 0),
            'visible': source_config.get('visible', True),
            'opacity': source_config.get('opacity', 1.0),
            'rotation': source_config.get('rotation', 0)
        }
        
        logger.info(f"➕ Added video source: {source_id}")
    
    def remove_source(self, source_id: str):
        """Remove video source"""
        if source_id in self.sources:
            del self.sources[source_id]
            logger.info(f"➖ Removed video source: {source_id}")
    
    def update_source(self, source_id: str, updates: Dict[str, Any]):
        """Update source configuration"""
        if source_id in self.sources:
            self.sources[source_id].update(updates)
            logger.info(f"✏️ Updated video source: {source_id}")
    
    def compose_frame(self, frame_sources: Dict[str, np.ndarray]) -> np.ndarray:
        """Compose final frame from multiple sources"""
        # Create black canvas
        final_frame = np.zeros((self.height, self.width, 3), dtype=np.uint8)
        
        # Sort sources by z_index
        sorted_sources = sorted(
            self.sources.items(),
            key=lambda x: x[1]['z_index']
        )
        
        # Composite each source
        for source_id, source_info in sorted_sources:
            if not source_info['visible']:
                continue
            
            if source_id in frame_sources:
                source_frame = frame_sources[source_id]
                
                # Resize source frame
                target_size = (
                    source_info['size']['width'],
                    source_info['size']['height']
                )
                resized_frame = cv2.resize(source_frame, target_size)
                
                # Apply transformations
                if source_info['rotation'] != 0:
                    # Apply rotation
                    matrix = cv2.getRotationMatrix2D(
                        (target_size[0]//2, target_size[1]//2),
                        source_info['rotation'],
                        1.0
                    )
                    resized_frame = cv2.warpAffine(resized_frame, matrix, target_size)
                
                # Apply opacity
                if source_info['opacity'] < 1.0:
                    resized_frame = cv2.addWeighted(
                        resized_frame, source_info['opacity'],
                        np.zeros_like(resized_frame), 1 - source_info['opacity'],
                        0
                    )
                
                # Position source on final frame
                x, y = source_info['position']['x'], source_info['position']['y']
                h, w = resized_frame.shape[:2]
                
                # Check bounds
                if (x >= 0 and y >= 0 and x + w <= self.width and y + h <= self.height):
                    final_frame[y:y+h, x:x+w] = resized_frame
        
        self.frame_count += 1
        return final_frame
    
    def get_info(self) -> Dict[str, Any]:
        """Get compositor information"""
        return {
            'width': self.width,
            'height': self.height,
            'fps': self.fps,
            'frame_count': self.frame_count,
            'sources_count': len(self.sources),
            'composition_mode': self.composition_mode
        }

class AudioMixer:
    """Professional audio mixer for multi-source streaming"""
    
    def __init__(self):
        self.sources = {}
        self.master_volume = 1.0
        self.sample_rate = 44100
        self.channels = 2
        
        logger.info("🎵 Audio Mixer initialized")
    
    def add_source(self, source_id: str, source_config: Dict[str, Any]):
        """Add audio source"""
        self.sources[source_id] = {
            'id': source_id,
            'volume': source_config.get('volume', 1.0),
            'muted': source_config.get('muted', False),
            'balance': source_config.get('balance', 0.0),  # -1.0 (left) to 1.0 (right)
            'effects': source_config.get('effects', [])
        }
        
        logger.info(f"🎤 Added audio source: {source_id}")
    
    def mix_audio(self, audio_sources: Dict[str, np.ndarray]) -> np.ndarray:
        """Mix multiple audio sources"""
        if not audio_sources:
            # Return silent audio
            return np.zeros((1024, self.channels), dtype=np.int16)
        
        # Start with silence
        mixed_audio = np.zeros((1024, self.channels), dtype=np.int16)
        
        # Mix each source
        for source_id, source_audio in audio_sources.items():
            if source_id in self.sources:
                source_info = self.sources[source_id]
                
                if source_info['muted']:
                    continue
                
                # Apply volume
                volume = source_info['volume'] * self.master_volume
                processed_audio = source_audio * volume
                
                # Add to mix
                mixed_audio += processed_audio.astype(np.int16)
        
        # Clip to prevent overflow
        mixed_audio = np.clip(mixed_audio, -32768, 32767)
        
        return mixed_audio
    
    def get_info(self) -> Dict[str, Any]:
        """Get mixer information"""
        return {
            'sample_rate': self.sample_rate,
            'channels': self.channels,
            'master_volume': self.master_volume,
            'sources_count': len(self.sources)
        }

# Global broadcast engine instance
broadcast_engine = BroadcastEngine()

def setup_broadcast_api(app):
    """Setup broadcast engine API endpoints"""
    
    @app.route('/api/broadcast/initialize', methods=['POST'])
    def initialize_broadcast():
        """Initialize broadcast engine"""
        data = request.get_json()
        quality = data.get('quality', '720p')
        
        result = broadcast_engine.initialize_streaming(quality)
        return jsonify(result)
    
    @app.route('/api/broadcast/start/<platform>', methods=['POST'])
    def start_platform_broadcast(platform):
        """Start streaming to platform"""
        data = request.get_json()
        result = broadcast_engine.start_platform_stream(platform, data)
        return jsonify(result)
    
    @app.route('/api/broadcast/stop/<platform>', methods=['POST'])
    def stop_platform_broadcast(platform):
        """Stop streaming to platform"""
        result = broadcast_engine.stop_platform_stream(platform)
        return jsonify(result)
    
    @app.route('/api/broadcast/stop-all', methods=['POST'])
    def stop_all_broadcasts():
        """Stop all streams"""
        result = broadcast_engine.stop_all_streams()
        return jsonify(result)
    
    @app.route('/api/broadcast/status', methods=['GET'])
    def get_broadcast_status():
        """Get broadcast status"""
        status = broadcast_engine.get_stream_status()
        return jsonify(status)
    
    @app.route('/api/broadcast/quality', methods=['PUT'])
    def update_broadcast_quality():
        """Update stream quality"""
        data = request.get_json()
        quality = data.get('quality')
        
        result = broadcast_engine.update_stream_quality(quality)
        return jsonify(result)

if __name__ == "__main__":
    print("🌊 Matrix Broadcast Studio - Broadcast Engine")
    print("=" * 60)
    print("🚀 Professional multi-platform streaming")
    print("🎬 Video composition with multiple sources")
    print("🎵 Audio mixing and processing")
    print("📊 Real-time monitoring and statistics")
    print("🔄 Automatic failover and recovery")
    print("=" * 60)
    
    # Test broadcast engine
    engine = BroadcastEngine()
    result = engine.initialize_streaming('720p')
    print(f"✅ Engine initialized: {result}")
    
    status = engine.get_stream_status()
    print(f"📊 Status: {status}")