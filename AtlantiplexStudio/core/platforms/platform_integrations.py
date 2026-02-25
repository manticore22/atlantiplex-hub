import requests
import json
import base64
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import logging
import asyncio
import websockets
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

logger = logging.getLogger(__name__)

class YouTubeStreamer:
    """YouTube Live Streaming API integration"""
    
    def __init__(self, api_key: str, client_secret: str = None):
        self.api_key = api_key
        self.client_secret = client_secret
        self.youtube = None
        self.credentials = None
        self.scopes = ['https://www.googleapis.com/auth/youtube.force-ssl']
        
    def authenticate(self, credentials_data: Dict = None):
        """Authenticate with YouTube API"""
        try:
            if credentials_data:
                self.credentials = Credentials.from_authorized_user_info(
                    credentials_data, self.scopes
                )
            
            if not self.credentials or not self.credentials.valid:
                if self.credentials and self.credentials.expired and self.credentials.refresh_token:
                    self.credentials.refresh(Request())
                else:
                    flow = InstalledAppFlow.from_client_config(
                        {"web": {"client_id": "your_client_id", "client_secret": self.client_secret}},
                        self.scopes
                    )
                    self.credentials = flow.run_local_server(port=0)
            
            self.youtube = build('youtube', 'v3', credentials=self.credentials)
            return True
            
        except Exception as e:
            logger.error(f"YouTube authentication error: {e}")
            return False
    
    def create_broadcast(self, title: str, description: str, scheduled_start: datetime = None) -> Dict:
        """Create a YouTube live broadcast"""
        try:
            broadcast_data = {
                'snippet': {
                    'title': title,
                    'description': description,
                    'scheduledStartTime': scheduled_start.isoformat() if scheduled_start else None
                },
                'status': {
                    'privacyStatus': 'public',
                    'selfDeclaredMadeForKids': False
                }
            }
            
            # Remove scheduledStartTime if not provided
            if not scheduled_start:
                del broadcast_data['snippet']['scheduledStartTime']
            
            broadcast = self.youtube.liveBroadcasts().insert(
                part='snippet,status',
                body=broadcast_data
            ).execute()
            
            return broadcast
            
        except HttpError as e:
            logger.error(f"YouTube broadcast creation error: {e}")
            raise Exception(f"YouTube API Error: {e}")
    
    def create_stream(self, title: str) -> Dict:
        """Create a YouTube stream"""
        try:
            stream_data = {
                'snippet': {
                    'title': f"{title} - Stream",
                    'description': f"Stream for {title}"
                },
                'cdn': {
                    'format': '1080p',
                    'ingestionType': 'rtmp'
                }
            }
            
            stream = self.youtube.liveStreams().insert(
                part='snippet,cdn',
                body=stream_data
            ).execute()
            
            return stream
            
        except HttpError as e:
            logger.error(f"YouTube stream creation error: {e}")
            raise Exception(f"YouTube API Error: {e}")
    
    def bind_broadcast_to_stream(self, broadcast_id: str, stream_id: str) -> Dict:
        """Bind broadcast to stream"""
        try:
            self.youtube.liveBroadcasts().bind(
                id=broadcast_id,
                streamId=stream_id
            ).execute()
            
            return {'broadcastId': broadcast_id, 'streamId': stream_id}
            
        except HttpError as e:
            logger.error(f"YouTube bind error: {e}")
            raise Exception(f"YouTube API Error: {e}")
    
    def start_broadcast(self, broadcast_id: str) -> Dict:
        """Start YouTube broadcast"""
        try:
            broadcast = self.youtube.liveBroadcasts().transition(
                broadcastStatus='live',
                id=broadcast_id,
                part='status'
            ).execute()
            
            return broadcast
            
        except HttpError as e:
            logger.error(f"YouTube start broadcast error: {e}")
            raise Exception(f"YouTube API Error: {e}")
    
    def stop_broadcast(self, broadcast_id: str) -> Dict:
        """Stop YouTube broadcast"""
        try:
            broadcast = self.youtube.liveBroadcasts().transition(
                broadcastStatus='complete',
                id=broadcast_id,
                part='status'
            ).execute()
            
            return broadcast
            
        except HttpError as e:
            logger.error(f"YouTube stop broadcast error: {e}")
            raise Exception(f"YouTube API Error: {e}")
    
    def get_broadcast_analytics(self, broadcast_id: str) -> Dict:
        """Get broadcast analytics"""
        try:
            broadcast = self.youtube.liveBroadcasts().list(
                id=broadcast_id,
                part='snippet,statistics'
            ).execute()
            
            if 'items' in broadcast and len(broadcast['items']) > 0:
                return broadcast['items'][0]
            
            return {}
            
        except HttpError as e:
            logger.error(f"YouTube analytics error: {e}")
            return {}

class TwitchStreamer:
    """Twitch API integration for live streaming"""
    
    def __init__(self, client_id: str, client_secret: str, access_token: str = None):
        self.client_id = client_id
        self.client_secret = client_secret
        self.access_token = access_token
        self.base_url = "https://api.twitch.tv/helix"
        
    def authenticate(self) -> bool:
        """Get OAuth token"""
        try:
            url = "https://id.twitch.tv/oauth2/token"
            params = {
                'client_id': self.client_id,
                'client_secret': self.client_secret,
                'grant_type': 'client_credentials'
            }
            
            response = requests.post(url, params=params)
            if response.status_code == 200:
                data = response.json()
                self.access_token = data['access_token']
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Twitch authentication error: {e}")
            return False
    
    def get_headers(self) -> Dict:
        """Get request headers with authentication"""
        return {
            'Client-ID': self.client_id,
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        }
    
    def create_stream_marker(self, description: str) -> Dict:
        """Create a stream marker"""
        try:
            url = f"{self.base_url}/streams/markers"
            data = {
                'user_id': self.get_user_id(),
                'description': description
            }
            
            response = requests.post(url, headers=self.get_headers(), json=data)
            return response.json() if response.status_code == 200 else {}
            
        except Exception as e:
            logger.error(f"Twitch stream marker error: {e}")
            return {}
    
    def get_user_id(self) -> str:
        """Get authenticated user ID"""
        try:
            url = f"{self.base_url}/users"
            response = requests.get(url, headers=self.get_headers())
            
            if response.status_code == 200:
                data = response.json()
                return data['data'][0]['id'] if data['data'] else ''
            
            return ''
            
        except Exception as e:
            logger.error(f"Twitch get user ID error: {e}")
            return ''
    
    def get_stream_info(self, user_id: str = None) -> Dict:
        """Get current stream information"""
        try:
            if not user_id:
                user_id = self.get_user_id()
            
            url = f"{self.base_url}/streams"
            params = {'user_id': user_id}
            
            response = requests.get(url, headers=self.get_headers(), params=params)
            
            if response.status_code == 200:
                data = response.json()
                return data['data'][0] if data['data'] else {}
            
            return {}
            
        except Exception as e:
            logger.error(f"Twitch stream info error: {e}")
            return {}
    
    def modify_stream_info(self, title: str, game_id: str = None) -> bool:
        """Modify stream information"""
        try:
            url = f"{self.base_url}/channels"
            data = {
                'game_id': game_id or '',
                'title': title
            }
            
            response = requests.patch(url, headers=self.get_headers(), json=data)
            return response.status_code == 204
            
        except Exception as e:
            logger.error(f"Twitch modify stream error: {e}")
            return False

class FacebookStreamer:
    """Facebook Live API integration"""
    
    def __init__(self, access_token: str, page_id: str):
        self.access_token = access_token
        self.page_id = page_id
        self.base_url = "https://graph.facebook.com/v18.0"
        
    def create_live_video(self, title: str, description: str) -> Dict:
        """Create Facebook Live video"""
        try:
            url = f"{self.base_url}/{self.page_id}/live_videos"
            params = {
                'access_token': self.access_token,
                'title': title,
                'description': description,
                'status': 'LIVE_NOW'
            }
            
            response = requests.post(url, params=params)
            
            if response.status_code == 200:
                return response.json()
            
            return {}
            
        except Exception as e:
            logger.error(f"Facebook create live video error: {e}")
            return {}
    
    def get_stream_url(self, live_video_id: str) -> str:
        """Get RTMP stream URL"""
        try:
            url = f"{self.base_url}/{live_video_id}"
            params = {
                'access_token': self.access_token,
                'fields': 'stream_url'
            }
            
            response = requests.get(url, params=params)
            
            if response.status_code == 200:
                data = response.json()
                return data.get('stream_url', '')
            
            return ''
            
        except Exception as e:
            logger.error(f"Facebook get stream URL error: {e}")
            return ''
    
    def end_live_video(self, live_video_id: str) -> bool:
        """End Facebook Live video"""
        try:
            url = f"{self.base_url}/{live_video_id}"
            params = {
                'access_token': self.access_token,
                'end_live_video': True
            }
            
            response = requests.post(url, params=params)
            return response.status_code == 200
            
        except Exception as e:
            logger.error(f"Facebook end live video error: {e}")
            return False

class LinkedInStreamer:
    """LinkedIn Live API integration"""
    
    def __init__(self, access_token: str):
        self.access_token = access_token
        self.base_url = "https://api.linkedin.com/v2"
        
    def create_live_broadcast(self, title: str, description: str) -> Dict:
        """Create LinkedIn Live broadcast"""
        try:
            url = f"{self.base_url}/liveBroadcasts"
            headers = {
                'Authorization': f'Bearer {self.access_token}',
                'Content-Type': 'application/json'
            }
            
            data = {
                'owner': 'urn:li:person:CURRENT_USER',
                'title': title,
                'description': description
            }
            
            response = requests.post(url, headers=headers, json=data)
            
            if response.status_code == 201:
                return response.json()
            
            return {}
            
        except Exception as e:
            logger.error(f"LinkedIn create broadcast error: {e}")
            return {}
    
    def get_broadcast_data(self, broadcast_id: str) -> Dict:
        """Get broadcast data including stream URL"""
        try:
            url = f"{self.base_url}/liveBroadcasts/{broadcast_id}"
            headers = {
                'Authorization': f'Bearer {self.access_token}'
            }
            
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                return response.json()
            
            return {}
            
        except Exception as e:
            logger.error(f"LinkedIn get broadcast data error: {e}")
            return {}
    
    def start_broadcast(self, broadcast_id: str) -> bool:
        """Start LinkedIn broadcast"""
        try:
            url = f"{self.base_url}/liveBroadcasts/{broadcast_id}/start"
            headers = {
                'Authorization': f'Bearer {self.access_token}',
                'Content-Type': 'application/json'
            }
            
            response = requests.post(url, headers=headers)
            return response.status_code == 204
            
        except Exception as e:
            logger.error(f"LinkedIn start broadcast error: {e}")
            return False

class MultiPlatformStreamer:
    """Multi-platform streaming manager"""
    
    def __init__(self):
        self.streamers = {}
        self.active_streams = {}
        
    def add_youtube_streamer(self, api_key: str, client_secret: str = None):
        """Add YouTube streamer"""
        self.streamers['youtube'] = YouTubeStreamer(api_key, client_secret)
        
    def add_twitch_streamer(self, client_id: str, client_secret: str, access_token: str = None):
        """Add Twitch streamer"""
        self.streamers['twitch'] = TwitchStreamer(client_id, client_secret, access_token)
        
    def add_facebook_streamer(self, access_token: str, page_id: str):
        """Add Facebook streamer"""
        self.streamers['facebook'] = FacebookStreamer(access_token, page_id)
        
    def add_linkedin_streamer(self, access_token: str):
        """Add LinkedIn streamer"""
        self.streamers['linkedin'] = LinkedInStreamer(access_token)
    
    def start_multi_platform_stream(self, stream_data: Dict) -> Dict:
        """Start streaming on multiple platforms"""
        results = {}
        
        for platform, streamer in self.streamers.items():
            if platform in stream_data.get('platforms', []):
                try:
                    if platform == 'youtube':
                        result = self._start_youtube_stream(streamer, stream_data)
                    elif platform == 'twitch':
                        result = self._start_twitch_stream(streamer, stream_data)
                    elif platform == 'facebook':
                        result = self._start_facebook_stream(streamer, stream_data)
                    elif platform == 'linkedin':
                        result = self._start_linkedin_stream(streamer, stream_data)
                    
                    results[platform] = result
                    
                except Exception as e:
                    logger.error(f"Failed to start {platform} stream: {e}")
                    results[platform] = {'error': str(e)}
        
        return results
    
    def _start_youtube_stream(self, streamer: YouTubeStreamer, stream_data: Dict) -> Dict:
        """Start YouTube stream"""
        if not streamer.authenticate(stream_data.get('credentials')):
            raise Exception("YouTube authentication failed")
        
        # Create broadcast
        broadcast = streamer.create_broadcast(
            stream_data['title'],
            stream_data.get('description', ''),
            stream_data.get('scheduled_start')
        )
        
        # Create stream
        stream = streamer.create_stream(stream_data['title'])
        
        # Bind broadcast to stream
        streamer.bind_broadcast_to_stream(
            broadcast['id'],
            stream['id']
        )
        
        # Start broadcast
        if stream_data.get('start_immediately', False):
            streamer.start_broadcast(broadcast['id'])
        
        return {
            'broadcast_id': broadcast['id'],
            'stream_id': stream['id'],
            'stream_url': stream['cdn']['ingestionInfo']['rtmpUrl'],
            'stream_key': stream['cdn']['ingestionInfo']['streamName'],
            'status': 'live' if stream_data.get('start_immediately') else 'ready'
        }
    
    def _start_twitch_stream(self, streamer: TwitchStreamer, stream_data: Dict) -> Dict:
        """Start Twitch stream"""
        if not streamer.authenticate():
            raise Exception("Twitch authentication failed")
        
        # Modify stream info
        streamer.modify_stream_info(stream_data['title'])
        
        # Create stream marker
        streamer.create_stream_marker(f"Stream started: {stream_data['title']}")
        
        return {
            'status': 'live',
            'title': stream_data['title'],
            'platform': 'twitch'
        }
    
    def _start_facebook_stream(self, streamer: FacebookStreamer, stream_data: Dict) -> Dict:
        """Start Facebook stream"""
        # Create live video
        live_video = streamer.create_live_video(
            stream_data['title'],
            stream_data.get('description', '')
        )
        
        if not live_video:
            raise Exception("Failed to create Facebook live video")
        
        # Get stream URL
        stream_url = streamer.get_stream_url(live_video['id'])
        
        return {
            'live_video_id': live_video['id'],
            'stream_url': stream_url,
            'status': 'live'
        }
    
    def _start_linkedin_stream(self, streamer: LinkedInStreamer, stream_data: Dict) -> Dict:
        """Start LinkedIn stream"""
        # Create broadcast
        broadcast = streamer.create_live_broadcast(
            stream_data['title'],
            stream_data.get('description', '')
        )
        
        if not broadcast:
            raise Exception("Failed to create LinkedIn broadcast")
        
        # Get broadcast data
        broadcast_data = streamer.get_broadcast_data(broadcast['id'])
        
        # Start broadcast
        if stream_data.get('start_immediately', False):
            streamer.start_broadcast(broadcast['id'])
        
        return {
            'broadcast_id': broadcast['id'],
            'stream_url': broadcast_data.get('streamUrl', ''),
            'status': 'live' if stream_data.get('start_immediately') else 'ready'
        }
    
    def stop_multi_platform_stream(self, stream_data: Dict) -> Dict:
        """Stop streaming on multiple platforms"""
        results = {}
        
        for platform, stream_info in stream_data.get('platform_streams', {}).items():
            try:
                if platform == 'youtube' and 'youtube' in self.streamers:
                    result = self._stop_youtube_stream(self.streamers['youtube'], stream_info)
                elif platform == 'facebook' and 'facebook' in self.streamers:
                    result = self._stop_facebook_stream(self.streamers['facebook'], stream_info)
                elif platform == 'linkedin' and 'linkedin' in self.streamers:
                    result = self._stop_linkedin_stream(self.streamers['linkedin'], stream_info)
                else:
                    result = {'status': 'stopped'}
                
                results[platform] = result
                
            except Exception as e:
                logger.error(f"Failed to stop {platform} stream: {e}")
                results[platform] = {'error': str(e)}
        
        return results
    
    def _stop_youtube_stream(self, streamer: YouTubeStreamer, stream_info: Dict) -> Dict:
        """Stop YouTube stream"""
        if 'broadcast_id' in stream_info:
            streamer.stop_broadcast(stream_info['broadcast_id'])
        
        return {'status': 'stopped'}
    
    def _stop_facebook_stream(self, streamer: FacebookStreamer, stream_info: Dict) -> Dict:
        """Stop Facebook stream"""
        if 'live_video_id' in stream_info:
            streamer.end_live_video(stream_info['live_video_id'])
        
        return {'status': 'stopped'}
    
    def _stop_linkedin_stream(self, streamer: LinkedInStreamer, stream_info: Dict) -> Dict:
        """Stop LinkedIn stream"""
        # LinkedIn doesn't have a specific stop endpoint
        # Broadcast ends when streaming stops
        return {'status': 'stopped'}
    
    def get_analytics(self, stream_data: Dict) -> Dict:
        """Get analytics from all platforms"""
        results = {}
        
        for platform, stream_info in stream_data.get('platform_streams', {}).items():
            try:
                if platform == 'youtube' and 'youtube' in self.streamers:
                    result = self.streamers['youtube'].get_broadcast_analytics(
                        stream_info.get('broadcast_id')
                    )
                elif platform == 'twitch' and 'twitch' in self.streamers:
                    result = self.streamers['twitch'].get_stream_info()
                else:
                    result = {}
                
                results[platform] = result
                
            except Exception as e:
                logger.error(f"Failed to get {platform} analytics: {e}")
                results[platform] = {'error': str(e)}
        
        return results