#!/usr/bin/env python3
"""
🌊 MATRIX BROADCAST STUDIO - API ENDPOINTS
Comprehensive API endpoints for unified broadcasting server
"""

import os
import json
import logging
from datetime import datetime, timedelta
from flask import request, jsonify, send_from_directory
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_socketio import emit
from werkzeug.utils import secure_filename
from typing import Dict, List, Optional, Any

logger = logging.getLogger(__name__)

def setup_comprehensive_api(app, socketio, unified_system, db):
    """Setup comprehensive API endpoints"""

    # === STREAMING CONTROL API ===
    
    @app.route('/api/stream/preview', methods=['GET'])
    @jwt_required()
    def get_stream_preview():
        """Get current stream preview"""
        try:
            # Get current scene preview from OBS
            if unified_system.obs_controller.is_connected():
                preview_data = unified_system.obs_controller.get_preview_source()
                return jsonify({
                    'success': True,
                    'preview_url': preview_data.get('screenshot'),
                    'sources': preview_data.get('sources', [])
                })
            else:
                return jsonify({'error': 'OBS not connected'}), 503
                
        except Exception as e:
            logger.error(f"❌ Stream preview error: {e}")
            return jsonify({'error': str(e)}), 500

    @app.route('/api/stream/audio/mix', methods=['POST'])
    @jwt_required()
    def update_audio_mix():
        """Update audio mix settings"""
        try:
            data = request.get_json()
            
            # Update audio mixer settings
            result = unified_system.broadcast_engine.audio_mixer.update_mix(data)
            
            # Emit to connected clients
            socketio.emit('audio_mix_updated', data)
            
            return jsonify({
                'success': True,
                'mix_settings': result
            })
            
        except Exception as e:
            logger.error(f"❌ Audio mix error: {e}")
            return jsonify({'error': str(e)}), 500

    @app.route('/api/stream/video/composition', methods=['POST'])
    @jwt_required()
    def update_video_composition():
        """Update video composition settings"""
        try:
            data = request.get_json()
            
            # Update video compositor
            compositor = unified_system.broadcast_engine.video_compositor
            
            # Update sources
            if 'sources' in data:
                for source_update in data['sources']:
                    source_id = source_update['id']
                    if 'position' in source_update:
                        compositor.update_source_position(
                            source_id, 
                            source_update['position']['x'], 
                            source_update['position']['y']
                        )
                    if 'size' in source_update:
                        compositor.update_source_size(
                            source_id, 
                            source_update['size']['width'], 
                            source_update['size']['height']
                        )
                    if 'visibility' in source_update:
                        compositor.update_source_visibility(
                            source_id, 
                            source_update['visibility']
                        )
            
            return jsonify({
                'success': True,
                'composition': compositor.get_composition_info()
            })
            
        except Exception as e:
            logger.error(f"❌ Video composition error: {e}")
            return jsonify({'error': str(e)}), 500

    # === GUEST MANAGEMENT API ===
    
    @app.route('/api/guests/<guest_id>/invite', methods=['POST'])
    @jwt_required()
    def invite_guest(guest_id):
        """Send invite to guest"""
        try:
            data = request.get_json()
            guest_data = {
                'name': data.get('name'),
                'email': data.get('email'),
                'role': data.get('role', 'guest'),
                'permissions': data.get('permissions', {})
            }
            
            result = unified_system.guest_manager.invite_guest(guest_id, guest_data)
            
            # Send invite via email/webhook (implementation needed)
            
            return jsonify({
                'success': True,
                'invite_code': result.get('invite_code'),
                'guest_url': f"https://studio.matrix.local/guest-view/{guest_id}"
            })
            
        except Exception as e:
            logger.error(f"❌ Guest invite error: {e}")
            return jsonify({'error': str(e)}), 500

    @app.route('/api/guests/<guest_id>/kick', methods=['POST'])
    @jwt_required()
    def kick_guest(guest_id):
        """Kick guest from studio"""
        try:
            result = unified_system.guest_manager.kick_guest(guest_id)
            
            # Notify guest
            socketio.emit('kicked', {'reason': 'Kicked by host'}, room=f'guest_{guest_id}')
            
            # Update UI
            socketio.emit('guest_kicked', {'guest_id': guest_id}, room='studio')
            
            return jsonify({
                'success': True,
                'guest_id': guest_id
            })
            
        except Exception as e:
            logger.error(f"❌ Guest kick error: {e}")
            return jsonify({'error': str(e)}), 500

    @app.route('/api/guests/<guest_id>/media', methods=['PUT'])
    @jwt_required()
    def toggle_guest_media(guest_id):
        """Toggle guest camera/microphone"""
        try:
            data = request.get_json()
            action = data.get('action')  # 'camera', 'microphone', 'both'
            state = data.get('state', 'toggle')  # 'on', 'off', 'toggle'
            
            result = unified_system.guest_manager.toggle_guest_media(guest_id, action, state)
            
            # Notify guest
            socketio.emit('media_toggled', {
                'action': action,
                'state': result.get('new_state')
            }, room=f'guest_{guest_id}')
            
            return jsonify({
                'success': True,
                'new_state': result.get('new_state')
            })
            
        except Exception as e:
            logger.error(f"❌ Guest media toggle error: {e}")
            return jsonify({'error': str(e)}), 500

    # === SCENE MANAGEMENT API ===
    
    @app.route('/api/scenes/custom', methods=['POST'])
    @jwt_required()
    def create_custom_scene():
        """Create custom scene"""
        try:
            data = request.get_json()
            
            scene = {
                'name': data['name'],
                'description': data.get('description', ''),
                'sources': data.get('sources', []),
                'layout': data.get('layout', 'custom'),
                'transitions': data.get('transitions', {})
            }
            
            result = unified_system.scene_manager.create_custom_scene(scene)
            
            return jsonify({
                'success': True,
                'scene_id': result.get('scene_id'),
                'scene': result.get('scene')
            })
            
        except Exception as e:
            logger.error(f"❌ Scene creation error: {e}")
            return jsonify({'error': str(e)}), 500

    @app.route('/api/scenes/<scene_id>/sources', methods=['POST'])
    @jwt_required()
    def add_scene_source(scene_id):
        """Add source to scene"""
        try:
            data = request.get_json()
            
            source_config = {
                'id': data['id'],
                'name': data['name'],
                'type': data['type'],
                'settings': data.get('settings', {}),
                'position': data.get('position', {'x': 0, 'y': 0}),
                'size': data.get('size', {'width': 1920, 'height': 1080})
            }
            
            result = unified_system.scene_manager.add_source_to_scene(scene_id, source_config)
            
            return jsonify({
                'success': True,
                'source_id': source_config['id'],
                'scene_id': scene_id
            })
            
        except Exception as e:
            logger.error(f"❌ Add scene source error: {e}")
            return jsonify({'error': str(e)}), 500

    @app.route('/api/scenes/transition', methods=['POST'])
    @jwt_required()
    def scene_transition():
        """Execute scene transition"""
        try:
            data = request.get_json()
            
            from_scene = data.get('from_scene')
            to_scene = data.get('to_scene')
            transition_type = data.get('type', 'cut')  # cut, fade, slide, zoom
            duration = data.get('duration', 1000)  # milliseconds
            
            result = unified_system.scene_manager.execute_transition(
                from_scene, to_scene, transition_type, duration
            )
            
            # Notify clients
            socketio.emit('scene_transition', {
                'from_scene': from_scene,
                'to_scene': to_scene,
                'transition_type': transition_type,
                'duration': duration
            }, room='studio')
            
            return jsonify({
                'success': True,
                'transition': result
            })
            
        except Exception as e:
            logger.error(f"❌ Scene transition error: {e}")
            return jsonify({'error': str(e)}), 500

    # === PLATFORM MANAGEMENT API ===
    
    @app.route('/api/platforms/test-connection', methods=['POST'])
    @jwt_required()
    def test_platform_connection():
        """Test connection to streaming platform"""
        try:
            data = request.get_json()
            platform = data.get('platform')
            credentials = data.get('credentials', {})
            
            result = unified_system.platform_streamer.test_connection(platform, credentials)
            
            return jsonify({
                'success': result.get('success', False),
                'platform': platform,
                'test_result': result
            })
            
        except Exception as e:
            logger.error(f"❌ Platform test error: {e}")
            return jsonify({'error': str(e)}), 500

    @app.route('/api/platforms/<platform>/stream-key', methods=['POST'])
    @jwt_required()
    def regenerate_stream_key(platform):
        """Regenerate stream key for platform"""
        try:
            result = unified_system.platform_streamer.regenerate_stream_key(platform)
            
            return jsonify({
                'success': True,
                'platform': platform,
                'new_stream_key': result.get('stream_key')
            })
            
        except Exception as e:
            logger.error(f"❌ Stream key regeneration error: {e}")
            return jsonify({'error': str(e)}), 500

    # === RECORDING API ===
    
    @app.route('/api/recording/start', methods=['POST'])
    @jwt_required()
    def start_recording():
        """Start recording stream"""
        try:
            data = request.get_json()
            format_type = data.get('format', 'mp4')  # mp4, flv, mov
            quality = data.get('quality', 'high')
            
            result = unified_system.obs_controller.start_recording(format_type, quality)
            
            return jsonify({
                'success': True,
                'recording_path': result.get('recording_path'),
                'format': format_type,
                'quality': quality
            })
            
        except Exception as e:
            logger.error(f"❌ Recording start error: {e}")
            return jsonify({'error': str(e)}), 500

    @app.route('/api/recording/stop', methods=['POST'])
    @jwt_required()
    def stop_recording():
        """Stop recording stream"""
        try:
            result = unified_system.obs_controller.stop_recording()
            
            return jsonify({
                'success': True,
                'recording_path': result.get('recording_path'),
                'duration': result.get('duration'),
                'file_size': result.get('file_size')
            })
            
        except Exception as e:
            logger.error(f"❌ Recording stop error: {e}")
            return jsonify({'error': str(e)}), 500

    @app.route('/api/recordings', methods=['GET'])
    @jwt_required()
    def get_recordings():
        """Get list of recordings"""
        try:
            recordings = unified_system.obs_controller.get_recordings_list()
            
            return jsonify({
                'success': True,
                'recordings': recordings
            })
            
        except Exception as e:
            logger.error(f"❌ Get recordings error: {e}")
            return jsonify({'error': str(e)}), 500

    # === ANALYTICS API ===
    
    @app.route('/api/analytics/stream/<stream_id>', methods=['GET'])
    @jwt_required()
    def get_stream_analytics(stream_id):
        """Get detailed analytics for specific stream"""
        try:
            analytics = unified_system.analytics_engine.get_stream_analytics(stream_id)
            
            return jsonify({
                'success': True,
                'stream_id': stream_id,
                'analytics': analytics
            })
            
        except Exception as e:
            logger.error(f"❌ Stream analytics error: {e}")
            return jsonify({'error': str(e)}), 500

    @app.route('/api/analytics/realtime', methods=['GET'])
    @jwt_required()
    def get_realtime_analytics():
        """Get real-time analytics"""
        try:
            analytics = unified_system.analytics_engine.get_realtime_stats()
            
            return jsonify({
                'success': True,
                'timestamp': datetime.utcnow().isoformat(),
                'analytics': analytics
            })
            
        except Exception as e:
            logger.error(f"❌ Realtime analytics error: {e}")
            return jsonify({'error': str(e)}), 500

    @app.route('/api/analytics/export/<stream_id>', methods=['GET'])
    @jwt_required()
    def export_analytics(stream_id):
        """Export analytics data"""
        try:
            format_type = request.args.get('format', 'json')  # json, csv, pdf
            analytics = unified_system.analytics_engine.export_analytics(stream_id, format_type)
            
            return jsonify({
                'success': True,
                'stream_id': stream_id,
                'format': format_type,
                'export_url': analytics.get('export_url'),
                'data': analytics.get('data')
            })
            
        except Exception as e:
            logger.error(f"❌ Export analytics error: {e}")
            return jsonify({'error': str(e)}), 500

    # === FILE MANAGEMENT API ===
    
    @app.route('/api/upload/media', methods=['POST'])
    @jwt_required()
    def upload_media():
        """Upload media file (image, video, audio)"""
        try:
            if 'file' not in request.files:
                return jsonify({'error': 'No file provided'}), 400
            
            file = request.files['file']
            if file.filename == '':
                return jsonify({'error': 'No file selected'}), 400
            
            # Validate file type
            allowed_extensions = {'png', 'jpg', 'jpeg', 'gif', 'mp4', 'avi', 'mov', 'webm', 'mp3', 'wav'}
            if not ('.' in file.filename and 
                   file.filename.rsplit('.', 1)[1].lower() in allowed_extensions):
                return jsonify({'error': 'File type not allowed'}), 400
            
            # Generate unique filename
            filename = secure_filename(file.filename)
            file_id = str(uuid.uuid4())
            file_path = os.path.join('uploads', f"{file_id}_{filename}")
            
            # Save file
            file.save(file_path)
            
            # Process if needed (resize images, optimize videos)
            processed_info = unified_system.obs_controller.process_uploaded_file(file_path)
            
            return jsonify({
                'success': True,
                'file_id': file_id,
                'filename': filename,
                'file_path': file_path,
                'processed_info': processed_info
            })
            
        except Exception as e:
            logger.error(f"❌ Media upload error: {e}")
            return jsonify({'error': str(e)}), 500

    @app.route('/api/media/gallery', methods=['GET'])
    @jwt_required()
    def get_media_gallery():
        """Get media gallery"""
        try:
            media_type = request.args.get('type', 'all')  # all, images, videos, audio
            page = int(request.args.get('page', 1))
            per_page = int(request.args.get('per_page', 20))
            
            gallery = unified_system.obs_controller.get_media_gallery(media_type, page, per_page)
            
            return jsonify({
                'success': True,
                'media_type': media_type,
                'page': page,
                'per_page': per_page,
                'gallery': gallery
            })
            
        except Exception as e:
            logger.error(f"❌ Media gallery error: {e}")
            return jsonify({'error': str(e)}), 500

    # === SCHEDULING API ===
    
    @app.route('/api/schedule/stream', methods=['POST'])
    @jwt_required()
    def schedule_stream():
        """Schedule a stream"""
        try:
            data = request.get_json()
            
            schedule_data = {
                'title': data['title'],
                'description': data.get('description', ''),
                'scheduled_time': datetime.fromisoformat(data['scheduled_time'].replace('Z', '+00:00')),
                'platforms': data.get('platforms', []),
                'duration_minutes': data.get('duration_minutes', 60),
                'recording_enabled': data.get('recording_enabled', False),
                'settings': data.get('settings', {})
            }
            
            result = unified_system.scheduler.schedule_stream(schedule_data)
            
            return jsonify({
                'success': True,
                'schedule_id': result.get('schedule_id'),
                'scheduled_time': schedule_data['scheduled_time'].isoformat()
            })
            
        except Exception as e:
            logger.error(f"❌ Schedule stream error: {e}")
            return jsonify({'error': str(e)}), 500

    @app.route('/api/schedule/upcoming', methods=['GET'])
    @jwt_required()
    def get_upcoming_streams():
        """Get upcoming scheduled streams"""
        try:
            limit = int(request.args.get('limit', 10))
            upcoming = unified_system.scheduler.get_upcoming_streams(limit)
            
            return jsonify({
                'success': True,
                'upcoming_streams': upcoming
            })
            
        except Exception as e:
            logger.error(f"❌ Upcoming streams error: {e}")
            return jsonify({'error': str(e)}), 500

    # === WEBHOOK HANDLERS ===
    
    @app.route('/webhooks/<platform>', methods=['POST'])
    def handle_platform_webhook(platform):
        """Handle webhooks from streaming platforms"""
        try:
            webhook_data = request.json
            
            # Process webhook based on platform
            if platform == 'youtube':
                result = unified_system.platform_streamer.youtube.handle_webhook(webhook_data)
            elif platform == 'twitch':
                result = unified_system.platform_streamer.twitch.handle_webhook(webhook_data)
            elif platform == 'facebook':
                result = unified_system.platform_streamer.facebook.handle_webhook(webhook_data)
            else:
                result = {'error': 'Unknown platform'}
            
            # Emit webhook event to connected clients
            socketio.emit('platform_webhook', {
                'platform': platform,
                'data': webhook_data,
                'processed': result
            }, room='studio')
            
            return jsonify(result)
            
        except Exception as e:
            logger.error(f"❌ Webhook error: {e}")
            return jsonify({'error': str(e)}), 500

    # === HEALTH AND MONITORING ===
    
    @app.route('/api/health/detailed', methods=['GET'])
    def detailed_health_check():
        """Detailed health check with all subsystems"""
        try:
            health_status = {
                'status': 'healthy',
                'timestamp': datetime.utcnow().isoformat(),
                'version': '2.0.0',
                'subsystems': {}
            }
            
            # Check broadcast engine
            try:
                broadcast_status = unified_system.broadcast_engine.get_stream_status()
                health_status['subsystems']['broadcast_engine'] = {
                    'status': 'healthy',
                    'active_streams': len(broadcast_status.get('active_platforms', {}))
                }
            except Exception as e:
                health_status['subsystems']['broadcast_engine'] = {
                    'status': 'error',
                    'error': str(e)
                }
            
            # Check OBS connection
            try:
                obs_connected = unified_system.obs_controller.is_connected()
                health_status['subsystems']['obs'] = {
                    'status': 'healthy' if obs_connected else 'disconnected',
                    'connected': obs_connected
                }
            except Exception as e:
                health_status['subsystems']['obs'] = {
                    'status': 'error',
                    'error': str(e)
                }
            
            # Check database
            try:
                db.session.execute('SELECT 1')
                health_status['subsystems']['database'] = {'status': 'healthy'}
            except Exception as e:
                health_status['subsystems']['database'] = {
                    'status': 'error',
                    'error': str(e)
                }
            
            return jsonify(health_status)
            
        except Exception as e:
            logger.error(f"❌ Health check error: {e}")
            return jsonify({
                'status': 'unhealthy',
                'error': str(e)
            }), 500

    return app